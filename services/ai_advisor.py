from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AIAdvisorError(RuntimeError):
    pass


DEFAULT_SUGGESTED_QUESTION = (
    "请结合当前数据集，分别说明 HNSW、IVF、PQ 的优势、劣势、适用场景，"
    "并给出它们各自推荐的参数设置。"
)


def build_dataset_context(
    *,
    data_path: str,
    dataset_info: dict[str, Any] | None = None,
    current_build_options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    info = dict(dataset_info or {})
    metadata_columns = info.get("metadata_columns") or info.get("metadata_fields") or []
    obsm_keys = info.get("obsm_keys") or []
    summary = {
        "source_path": info.get("source_path") or data_path,
        "format": info.get("format"),
        "cell_count": info.get("cell_count"),
        "gene_count": info.get("gene_count"),
        "vector_dim": info.get("vector_dim"),
        "embedding_key": info.get("embedding_key"),
        "visualization_source": info.get("visualization_source"),
        "metadata_columns": list(metadata_columns)[:24],
        "metadata_column_count": len(metadata_columns),
        "obsm_keys": list(obsm_keys)[:12],
        "current_build_options": dict(current_build_options or {}),
    }
    return {key: value for key, value in summary.items() if value not in (None, "", [], {})}


def request_ai_chat(
    *,
    api_key: str | None,
    model: str,
    api_url: str,
    dataset_context: dict[str, Any],
    user_question: str = "",
    conversation_history: list[dict[str, str]] | None = None,
    timeout_seconds: int = 45,
) -> dict[str, Any]:
    if not api_key:
        raise AIAdvisorError("ZHIPU_API_KEY is not configured")

    question = (user_question or "").strip() or DEFAULT_SUGGESTED_QUESTION
    messages = _build_messages(
        dataset_context=dataset_context,
        user_question=question,
        conversation_history=conversation_history or [],
    )
    body = _post_ai_messages(
        api_key=api_key,
        model=model,
        api_url=api_url,
        messages=messages,
        timeout_seconds=timeout_seconds,
    )

    answer_text = _extract_message_text(body)
    if not answer_text:
        raise AIAdvisorError("AI service returned empty answer")

    return {
        "model": body.get("model") or model,
        "answer": answer_text,
        "suggested_question": DEFAULT_SUGGESTED_QUESTION,
        "raw": body,
    }


def request_cell_analysis_chat(
    *,
    api_key: str | None,
    model: str,
    api_url: str,
    dataset_context: dict[str, Any],
    user_question: str,
    intent: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    cell_hits: list[dict[str, Any]],
    next_steps: list[str],
    evidence_bundle: dict[str, Any] | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    timeout_seconds: int = 45,
) -> dict[str, Any]:
    if not api_key:
        raise AIAdvisorError("ZHIPU_API_KEY is not configured")

    messages = _build_cell_analysis_messages(
        dataset_context=dataset_context,
        user_question=user_question,
        intent=intent,
        knowledge_hits=knowledge_hits,
        cell_hits=cell_hits,
        next_steps=next_steps,
        evidence_bundle=evidence_bundle or {},
        conversation_history=conversation_history or [],
    )
    body = _post_ai_messages(
        api_key=api_key,
        model=model,
        api_url=api_url,
        messages=messages,
        timeout_seconds=timeout_seconds,
    )
    answer_text = _extract_message_text(body)
    if not answer_text:
        raise AIAdvisorError("AI service returned empty answer")
    return {
        "model": body.get("model") or model,
        "answer": answer_text,
        "raw": body,
    }


def _build_messages(
    *,
    dataset_context: dict[str, Any],
    user_question: str,
    conversation_history: list[dict[str, str]],
) -> list[dict[str, str]]:
    system_prompt = (
        "你是单细胞相似检索系统里的 FAISS 索引调参与问答助手。"
        "你服务于当前数据集页面，可以回答索引类型、距离度量、参数选择、速度/召回/内存权衡等问题。"
        "你只能在 HNSW、IVF、PQ 这三种索引之间讨论。"
        "当用户询问“怎么选索引”或“参数怎么配”时，默认不要替用户指定唯一最佳索引，"
        "而要分别说明 HNSW、IVF、PQ 的优势、劣势、适用场景和建议参数。"
        "只有当用户明确要求你做单一推荐时，你才可以给出单一推荐。"
        "回答必须使用中文，优先给出工程上可执行的建议。"
        "如果信息不足，请明确写出你的假设。"
        "回答尽量结构化、易读，适合前端小窗展示。"
    )
    context_prompt = (
        "当前数据集摘要如下，请把这些信息作为你回答问题时的主要上下文。"
        "\n\n可用参数范围："
        "\n- HNSW: M=4~128, EF Construct=16~4096, EF Search=16~4096"
        "\n- IVF: NList=1~65536, NProbe=1~4096"
        "\n- PQ: Compression 只能在 x8 / x16 / x32 / x64 中选择"
        f"\n\n数据集摘要：\n{json.dumps(dataset_context, ensure_ascii=False, indent=2)}"
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": context_prompt},
    ]
    for item in conversation_history[-8:]:
        role = str(item.get("role") or "").strip().lower()
        content = str(item.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        messages.append({"role": role, "content": content[:4000]})
    messages.append({"role": "user", "content": user_question[:4000]})
    return messages


def _build_cell_analysis_messages(
    *,
    dataset_context: dict[str, Any],
    user_question: str,
    intent: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    cell_hits: list[dict[str, Any]],
    next_steps: list[str],
    evidence_bundle: dict[str, Any],
    conversation_history: list[dict[str, str]],
) -> list[dict[str, str]]:
    system_prompt = (
        "你是面向单细胞数据的自然语言检索与 AI 辅助分析助手。"
        "你要结合当前数据集摘要、知识库命中片段、候选细胞结果，回答用户关于 cell_type、marker gene、疾病关联、组织来源、结果解释和下一步分析建议的问题。"
        "你必须使用中文，并明确区分“数据集中的直接证据”和“知识库中的辅助知识”。"
        "如果证据不足，不要编造结论，要说明假设与限制。"
        "回答尽量按“结论、依据、解释、下一步建议”组织，适合前端小窗展示。"
    )
    llm_context = dict(evidence_bundle.get("llm_context") or {})
    if llm_context:
        context_prompt = (
            "下面是 Evidence Fusion 生成的结构化上下文，请严格优先依据这些证据回答。\n\n"
            f"{json.dumps(llm_context, ensure_ascii=False, indent=2)}"
        )
    else:
        context_prompt = (
            "下面是当前会话的结构化上下文，请以这些内容作为主要依据。\n\n"
            f"数据集摘要：\n{json.dumps(dataset_context, ensure_ascii=False, indent=2)}\n\n"
            f"问题解析结果：\n{json.dumps(intent, ensure_ascii=False, indent=2)}\n\n"
            f"命中知识片段：\n{json.dumps(knowledge_hits[:4], ensure_ascii=False, indent=2)}\n\n"
            f"命中候选细胞：\n{json.dumps(cell_hits[:8], ensure_ascii=False, indent=2)}\n\n"
            f"建议的下一步动作：\n{json.dumps(next_steps[:5], ensure_ascii=False, indent=2)}"
        )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": context_prompt},
    ]
    for item in conversation_history[-8:]:
        role = str(item.get("role") or "").strip().lower()
        content = str(item.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        messages.append({"role": role, "content": content[:4000]})
    messages.append({"role": "user", "content": (user_question or "").strip()[:4000]})
    return messages


def _post_ai_messages(
    *,
    api_key: str,
    model: str,
    api_url: str,
    messages: list[dict[str, str]],
    timeout_seconds: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": 0.2,
    }
    request = Request(
        api_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw_text = response.read().decode("utf-8")
    except HTTPError as exc:
        error_text = exc.read().decode("utf-8", errors="ignore")
        raise AIAdvisorError(f"AI service HTTP {exc.code}: {error_text or exc.reason}") from exc
    except URLError as exc:
        raise AIAdvisorError(f"AI service connection failed: {exc.reason}") from exc

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise AIAdvisorError("AI service returned invalid JSON") from exc


def _extract_message_text(body: dict[str, Any]) -> str:
    choices = body.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(part.strip() for part in parts if str(part).strip()).strip()
    return ""
