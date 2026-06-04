import json
from pathlib import Path

from services.auth_service import AuthError, _MySQLConnection


class AdminStore:
    def __init__(self, database_url):
        if not database_url:
            raise RuntimeError("DATABASE_URL is required")
        self.database_url = database_url

    def _connect(self):
        return _MySQLConnection(self.database_url)

    def _now(self):
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    def upsert_dataset(self, owner_user_id, data_path, dataset_info=None, status="ready"):
        normalized_path = str(data_path or "").strip()
        if not normalized_path:
            raise AuthError("data_path is required")
        dataset_info = dataset_info if isinstance(dataset_info, dict) else {}
        now = self._now()
        dataset_name = (
            str(dataset_info.get("dataset_name") or Path(normalized_path).stem or "dataset").strip()[:128]
            or "dataset"
        )
        source_format = dataset_info.get("format") or dataset_info.get("source_format")
        cell_count = dataset_info.get("cell_count")
        gene_count = dataset_info.get("gene_count")
        vector_dim = dataset_info.get("vector_dim")
        embedding_key = dataset_info.get("embedding_key")
        visualization_source = dataset_info.get("visualization_source")
        metadata_summary = json.dumps(dataset_info, ensure_ascii=False) if dataset_info else None

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id
                FROM datasets
                WHERE owner_user_id = ? AND data_path = ?
                LIMIT 1
                """,
                (owner_user_id, normalized_path),
            ).fetchone()
            if row:
                updates = ["dataset_name = ?", "status = ?", "updated_at = ?"]
                values = [dataset_name, status or "ready", now]
                optional_updates = {
                    "source_format": source_format,
                    "cell_count": cell_count,
                    "gene_count": gene_count,
                    "vector_dim": vector_dim,
                    "embedding_key": embedding_key,
                    "visualization_source": visualization_source,
                }
                for field_name, field_value in optional_updates.items():
                    if field_value is None:
                        continue
                    updates.append(f"{field_name} = ?")
                    values.append(field_value)
                if metadata_summary is not None:
                    updates.append("metadata_summary = ?")
                    values.append(metadata_summary)
                values.append(row["id"])
                conn.execute(f"UPDATE datasets SET {', '.join(updates)} WHERE id = ?", values)
                dataset_id = row["id"]
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO datasets (
                        owner_user_id, dataset_name, data_path, source_format,
                        cell_count, gene_count, vector_dim, embedding_key,
                        visualization_source, metadata_summary, status, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        owner_user_id,
                        dataset_name,
                        normalized_path,
                        source_format,
                        int(cell_count) if cell_count is not None else None,
                        int(gene_count) if gene_count is not None else None,
                        int(vector_dim) if vector_dim is not None else None,
                        embedding_key,
                        visualization_source,
                        metadata_summary,
                        status or "ready",
                        now,
                        now,
                    ),
                )
                dataset_id = cursor.lastrowid
        return self.get_dataset(dataset_id)

    def get_dataset_by_owner_and_path(self, owner_user_id, data_path):
        normalized_path = str(data_path or "").strip()
        if not normalized_path:
            return None
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT d.*, u.username AS owner_username, u.role AS owner_role
                FROM datasets d
                JOIN users u ON u.id = d.owner_user_id
                WHERE d.owner_user_id = ? AND d.data_path = ?
                LIMIT 1
                """,
                (owner_user_id, normalized_path),
            ).fetchone()
        return self._row_to_dataset(row) if row else None

    def get_dataset(self, dataset_id):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT d.*, u.username AS owner_username, u.role AS owner_role
                FROM datasets d
                JOIN users u ON u.id = d.owner_user_id
                WHERE d.id = ?
                """,
                (dataset_id,),
            ).fetchone()
        return self._row_to_dataset(row) if row else None

    def list_users_with_stats(self):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    u.role,
                    u.is_active,
                    u.display_name,
                    u.email,
                    u.last_login_at,
                    u.last_login_ip,
                    u.created_by,
                    u.disabled_reason,
                    u.token_version,
                    u.created_at,
                    u.updated_at,
                    (
                        SELECT COUNT(*)
                        FROM datasets d
                        WHERE d.owner_user_id = u.id
                    ) AS dataset_count,
                    (
                        SELECT COUNT(*)
                        FROM user_indexes ui
                        WHERE ui.user_id = u.id
                    ) AS index_count,
                    (
                        SELECT jb.status
                        FROM index_build_jobs jb
                        WHERE jb.user_id = u.id
                        ORDER BY jb.updated_at DESC, jb.created_at DESC
                        LIMIT 1
                    ) AS last_job_status,
                    (
                        SELECT jb.updated_at
                        FROM index_build_jobs jb
                        WHERE jb.user_id = u.id
                        ORDER BY jb.updated_at DESC, jb.created_at DESC
                        LIMIT 1
                    ) AS last_job_updated_at
                FROM users u
                ORDER BY u.id ASC
                """
            ).fetchall()
        return [self._row_to_user_stats(row) for row in rows]

    def get_user_detail(self, user_id):
        users = [item for item in self.list_users_with_stats() if int(item["id"]) == int(user_id)]
        if not users:
            raise AuthError("user not found")
        user = users[0]
        datasets = self.list_datasets(owner_user_id=user_id)
        indexes = self.list_indexes(user_id=user_id)
        jobs = self.list_build_jobs(user_id=user_id, limit=20)
        return {
            "user": user,
            "datasets": datasets,
            "indexes": indexes,
            "jobs": jobs,
            "charts": {
                "index_types": self._group_name_count(indexes, "index_type"),
                "metrics": self._group_name_count(indexes, "distance_metric"),
            },
        }

    def get_overview(self, trend_days=14):
        with self._connect() as conn:
            user_counts = conn.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active,
                    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS disabled,
                    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) AS admins,
                    SUM(CASE WHEN role = 'super_admin' THEN 1 ELSE 0 END) AS super_admins
                FROM users
                """
            ).fetchone()
            dataset_counts = conn.execute(
                "SELECT COUNT(*) AS total FROM datasets"
            ).fetchone()
            index_counts = conn.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN SUBSTRING(created_at, 1, 10) = SUBSTRING(UTC_TIMESTAMP(), 1, 10) THEN 1 ELSE 0 END) AS today
                FROM user_indexes
                """
            ).fetchone()
            job_counts = conn.execute(
                """
                SELECT
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
                    SUM(CASE WHEN status IN ('queued', 'running') THEN 1 ELSE 0 END) AS in_progress
                FROM index_build_jobs
                """
            ).fetchone()
            index_type_rows = conn.execute(
                """
                SELECT index_type AS name, COUNT(*) AS value
                FROM user_indexes
                GROUP BY index_type
                ORDER BY value DESC, name ASC
                """
            ).fetchall()
            metric_rows = conn.execute(
                """
                SELECT distance_metric AS name, COUNT(*) AS value
                FROM user_indexes
                GROUP BY distance_metric
                ORDER BY value DESC, name ASC
                """
            ).fetchall()
            top_users = conn.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    COUNT(ui.id) AS index_count,
                    (
                        SELECT COUNT(*)
                        FROM datasets d
                        WHERE d.owner_user_id = u.id
                    ) AS dataset_count
                FROM users u
                LEFT JOIN user_indexes ui ON ui.user_id = u.id
                GROUP BY u.id, u.username
                ORDER BY index_count DESC, dataset_count DESC, u.id ASC
                LIMIT 10
                """
            ).fetchall()
            trend_rows = conn.execute(
                f"""
                SELECT
                    SUBSTRING(created_at, 1, 10) AS day,
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
                FROM index_build_jobs
                WHERE created_at >= DATE_FORMAT(DATE_SUB(UTC_TIMESTAMP(), INTERVAL {int(trend_days)} DAY), '%%Y-%%m-%%d')
                GROUP BY SUBSTRING(created_at, 1, 10)
                ORDER BY day ASC
                """
            ).fetchall()

        return {
            "counts": {
                "users_total": int(user_counts["total"] or 0),
                "users_active": int(user_counts["active"] or 0),
                "users_disabled": int(user_counts["disabled"] or 0),
                "admins_total": int(user_counts["admins"] or 0),
                "super_admins_total": int(user_counts["super_admins"] or 0),
                "datasets_total": int(dataset_counts["total"] or 0),
                "indexes_total": int(index_counts["total"] or 0),
                "indexes_today": int(index_counts["today"] or 0),
                "jobs_completed": int(job_counts["completed"] or 0),
                "jobs_failed": int(job_counts["failed"] or 0),
                "jobs_in_progress": int(job_counts["in_progress"] or 0),
            },
            "distributions": {
                "index_types": [self._row_to_name_value(row) for row in index_type_rows],
                "metrics": [self._row_to_name_value(row) for row in metric_rows],
            },
            "top_users": [
                {
                    "id": int(row["id"]),
                    "username": row["username"],
                    "index_count": int(row["index_count"] or 0),
                    "dataset_count": int(row["dataset_count"] or 0),
                }
                for row in top_users
            ],
            "build_job_trend": [
                {
                    "day": row["day"],
                    "total": int(row["total"] or 0),
                    "completed": int(row["completed"] or 0),
                    "failed": int(row["failed"] or 0),
                }
                for row in trend_rows
            ],
        }

    def list_datasets(self, owner_user_id=None):
        query = """
            SELECT
                d.*,
                u.username AS owner_username,
                u.role AS owner_role,
                (
                    SELECT COUNT(*)
                    FROM user_indexes ui
                    WHERE ui.dataset_id = d.id
                ) AS index_count
            FROM datasets d
            JOIN users u ON u.id = d.owner_user_id
        """
        params = []
        if owner_user_id is not None:
            query += " WHERE d.owner_user_id = ?"
            params.append(owner_user_id)
        query += " ORDER BY d.updated_at DESC, d.id DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_dataset(row) for row in rows]

    def delete_dataset(self, dataset_id):
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise AuthError("dataset not found")
        with self._connect() as conn:
            conn.execute("DELETE FROM index_build_jobs WHERE dataset_id = ?", (dataset_id,))
            conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        return dataset

    def list_indexes(self, user_id=None, dataset_id=None):
        query = """
            SELECT
                ui.*,
                u.username AS owner_username,
                u.role AS owner_role,
                d.dataset_name
            FROM user_indexes ui
            JOIN users u ON u.id = ui.user_id
            LEFT JOIN datasets d ON d.id = ui.dataset_id
        """
        clauses = []
        params = []
        if user_id is not None:
            clauses.append("ui.user_id = ?")
            params.append(user_id)
        if dataset_id is not None:
            clauses.append("ui.dataset_id = ?")
            params.append(dataset_id)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY ui.updated_at DESC, ui.id DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_index(row) for row in rows]

    def get_index(self, index_id):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    ui.*,
                    u.username AS owner_username,
                    u.role AS owner_role,
                    d.dataset_name
                FROM user_indexes ui
                JOIN users u ON u.id = ui.user_id
                LEFT JOIN datasets d ON d.id = ui.dataset_id
                WHERE ui.id = ?
                """,
                (index_id,),
            ).fetchone()
        return self._row_to_index(row) if row else None

    def list_build_jobs(self, user_id=None, limit=120):
        query = """
            SELECT
                jb.*,
                u.username AS owner_username,
                d.dataset_name
            FROM index_build_jobs jb
            JOIN users u ON u.id = jb.user_id
            LEFT JOIN datasets d ON d.id = jb.dataset_id
        """
        params = []
        if user_id is not None:
            query += " WHERE jb.user_id = ?"
            params.append(user_id)
        query += " ORDER BY jb.updated_at DESC, jb.created_at DESC LIMIT ?"
        params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_build_job(row) for row in rows]

    def list_audit_logs(self, limit=120):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    l.*,
                    u.username AS actor_username
                FROM admin_audit_logs l
                LEFT JOIN users u ON u.id = l.actor_user_id
                ORDER BY l.created_at DESC, l.id DESC
                LIMIT ?
                """,
                (int(limit),),
            ).fetchall()
        return [self._row_to_audit_log(row) for row in rows]

    def create_audit_log(
        self,
        *,
        actor_user_id,
        actor_role,
        action_type,
        target_user_id=None,
        target_index_id=None,
        target_dataset_id=None,
        target_username=None,
        detail=None,
        ip_address=None,
    ):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO admin_audit_logs (
                    actor_user_id, actor_role, action_type,
                    target_user_id, target_index_id, target_dataset_id,
                    target_username, detail_json, ip_address, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    actor_user_id,
                    actor_role,
                    action_type,
                    target_user_id,
                    target_index_id,
                    target_dataset_id,
                    target_username,
                    json.dumps(detail or {}, ensure_ascii=False),
                    (ip_address or "").strip() or None,
                    self._now(),
                ),
            )

    def _group_name_count(self, rows, field_name):
        counts = {}
        for row in rows:
            key = str(row.get(field_name) or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return [{"name": name, "value": value} for name, value in sorted(counts.items())]

    def _row_to_name_value(self, row):
        return {
            "name": str(row.get("name") or "unknown"),
            "value": int(row.get("value") or 0),
        }

    def _row_to_user_stats(self, row):
        return {
            "id": int(row["id"]),
            "username": row["username"],
            "role": row["role"],
            "is_active": bool(row["is_active"]),
            "display_name": row.get("display_name"),
            "email": row.get("email"),
            "last_login_at": row.get("last_login_at"),
            "last_login_ip": row.get("last_login_ip"),
            "created_by": int(row["created_by"]) if row.get("created_by") is not None else None,
            "disabled_reason": row.get("disabled_reason"),
            "token_version": int(row.get("token_version") or 1),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
            "dataset_count": int(row.get("dataset_count") or 0),
            "index_count": int(row.get("index_count") or 0),
            "last_job_status": row.get("last_job_status"),
            "last_job_updated_at": row.get("last_job_updated_at"),
        }

    def _row_to_dataset(self, row):
        item = dict(row)
        item["id"] = int(item["id"])
        item["owner_user_id"] = int(item["owner_user_id"])
        item["cell_count"] = int(item["cell_count"]) if item.get("cell_count") is not None else None
        item["gene_count"] = int(item["gene_count"]) if item.get("gene_count") is not None else None
        item["vector_dim"] = int(item["vector_dim"]) if item.get("vector_dim") is not None else None
        item["index_count"] = int(item["index_count"]) if item.get("index_count") is not None else 0
        item["metadata_summary"] = json.loads(item.get("metadata_summary") or "null")
        return item

    def _row_to_index(self, row):
        item = dict(row)
        item["id"] = int(item["id"])
        item["user_id"] = int(item["user_id"])
        item["dataset_id"] = int(item["dataset_id"]) if item.get("dataset_id") is not None else None
        item["created_by"] = int(item["created_by"]) if item.get("created_by") is not None else None
        item["is_active"] = bool(item["is_active"])
        item["cell_count"] = int(item["cell_count"]) if item.get("cell_count") is not None else None
        item["gene_count"] = int(item["gene_count"]) if item.get("gene_count") is not None else None
        item["vector_dim"] = int(item["vector_dim"]) if item.get("vector_dim") is not None else None
        item["build_time_ms"] = float(item["build_time_ms"]) if item.get("build_time_ms") is not None else None
        item["quantization_config"] = json.loads(item.get("quantization_config") or "{}")
        item["metadata_keys"] = json.loads(item.get("metadata_keys") or "[]")
        item["hnsw_params"] = json.loads(item.get("hnsw_params") or "{}")
        item["search_params"] = json.loads(item.get("search_params") or "{}")
        return item

    def _row_to_build_job(self, row):
        item = dict(row)
        item["dataset_id"] = int(item["dataset_id"]) if item.get("dataset_id") is not None else None
        item["requested_by"] = int(item["requested_by"]) if item.get("requested_by") is not None else None
        item["activate"] = bool(item.get("activate"))
        item["progress_pct"] = float(item.get("progress_pct") or 0)
        item["processed_cells"] = int(item.get("processed_cells") or 0)
        item["total_cells"] = int(item["total_cells"]) if item.get("total_cells") is not None else None
        item["elapsed_seconds"] = float(item.get("elapsed_seconds") or 0)
        item["rate_cells_per_second"] = (
            float(item["rate_cells_per_second"]) if item.get("rate_cells_per_second") is not None else None
        )
        item["eta_seconds"] = float(item["eta_seconds"]) if item.get("eta_seconds") is not None else None
        item["dataset_summary"] = json.loads(item.get("dataset_summary") or "null")
        item["history"] = json.loads(item.get("history") or "[]")
        item["result"] = json.loads(item.get("result_json") or "null")
        item["error"] = item.get("error_text")
        item.pop("result_json", None)
        item.pop("error_text", None)
        return item

    def _row_to_audit_log(self, row):
        item = dict(row)
        item["id"] = int(item["id"])
        item["actor_user_id"] = int(item["actor_user_id"])
        item["target_user_id"] = int(item["target_user_id"]) if item.get("target_user_id") is not None else None
        item["target_index_id"] = int(item["target_index_id"]) if item.get("target_index_id") is not None else None
        item["target_dataset_id"] = int(item["target_dataset_id"]) if item.get("target_dataset_id") is not None else None
        item["detail"] = json.loads(item.get("detail_json") or "{}")
        item.pop("detail_json", None)
        return item
