from flask import Flask, jsonify, render_template, request

from config import DEFAULT_SAMPLE_DATA
from services.data_loader import load_cell_vectors
from services.vector_index import CellVectorIndex


app = Flask(__name__)
index = CellVectorIndex()


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "indexed": index.is_ready})


@app.post("/api/index/build")
def build_index():
    payload = request.get_json(silent=True) or {}
    data_path = payload.get("data_path") or str(DEFAULT_SAMPLE_DATA)

    try:
        dataset = load_cell_vectors(data_path)
        index.build(dataset)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "message": "index built",
            "collection": index.collection_name,
            "cell_count": len(dataset.cell_ids),
            "vector_dim": dataset.vector_dim,
        }
    )


@app.post("/api/search/by-id")
def search_by_id():
    payload = request.get_json(silent=True) or {}
    cell_id = payload.get("cell_id")
    top_k = int(payload.get("top_k", 5))

    if not cell_id:
        return jsonify({"error": "cell_id is required"}), 400

    try:
        results = index.search_by_cell_id(cell_id, top_k=top_k)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"query": {"cell_id": cell_id, "top_k": top_k}, "results": results})


@app.post("/api/search/by-vector")
def search_by_vector():
    payload = request.get_json(silent=True) or {}
    vector = payload.get("vector")
    top_k = int(payload.get("top_k", 5))

    if not vector:
        return jsonify({"error": "vector is required"}), 400

    try:
        results = index.search_by_vector(vector, top_k=top_k)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"query": {"top_k": top_k}, "results": results})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
