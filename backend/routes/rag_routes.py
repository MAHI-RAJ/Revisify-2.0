from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.rag_service import RagService


rag_bp = Blueprint("rag", __name__, url_prefix="/api/rag")


# -------------------------
# Helpers
# -------------------------
def _ok(data: Any, status: int = 200):
    return jsonify({"ok": True, "data": data}), status


def _err(message: str, status: int = 400, code: str = "BAD_REQUEST", details: Any = None):
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status


def _get_identity_user_id() -> str:
    ident = get_jwt_identity()
    if isinstance(ident, dict):
        uid = ident.get("id") or ident.get("user_id") or ident.get("sub")
        if not uid:
            raise ValueError("JWT identity dict missing user id")
        return str(uid)
    if ident is None:
        raise ValueError("Missing JWT identity")
    return str(ident)


def _json() -> Dict[str, Any]:
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data


def _as_int(x: Any, name: str) -> int:
    try:
        return int(x)
    except Exception:
        raise ValueError(f"Field '{name}' must be an integer")


# -------------------------
# Routes
# -------------------------

@rag_bp.post("/ask")
@jwt_required()
def rag_ask():
    """
    Ask a question grounded to the uploaded document.
    Input:
      {
        "document_id": 123,
        "question": "....",
        "top_k": 6,              # optional
        "max_tokens": 512        # optional
      }
    Output:
      {
        "answer": "...",
        "citations": [
           {"loc": 12, "chunk_id": 501, "snippet": "...."},
           ...
        ]
      }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        data = _json()

        if "document_id" not in data or "question" not in data:
            return _err("Missing fields: document_id, question", 400, "VALIDATION_ERROR", {"req_id": req_id})

        document_id = _as_int(data["document_id"], "document_id")
        question = str(data["question"]).strip()
        if not question:
            return _err("question cannot be empty", 400, "VALIDATION_ERROR", {"req_id": req_id})

        top_k = data.get("top_k", 6)
        max_tokens = data.get("max_tokens", None)

        try:
            top_k = int(top_k)
        except Exception:
            return _err("top_k must be integer", 400, "VALIDATION_ERROR", {"req_id": req_id})

        if top_k < 1 or top_k > 20:
            return _err("top_k must be between 1 and 20", 400, "VALIDATION_ERROR", {"req_id": req_id})

        svc = RagService()
        result = svc.ask(
            user_id=user_id,
            document_id=document_id,
            question=question,
            top_k=top_k,
            max_tokens=max_tokens,
        )

        if not isinstance(result, dict) or "answer" not in result:
            return _err("RAG service returned invalid response", 500, "SERVICE_ERROR", {"req_id": req_id})

        result["req_id"] = req_id
        return _ok(result)

    except ValueError as e:
        return _err(str(e), 400, "VALIDATION_ERROR", {"req_id": req_id})
    except Exception as e:
        current_app.logger.exception("rag_ask failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})


@rag_bp.get("/history")
@jwt_required()
def rag_history():
    """
    Optional: returns recent RAG chats for a document.
    Query: document_id, limit
    Output: { "items": [ {question, answer, citations, created_at}, ... ] }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        document_id = request.args.get("document_id")
        if not document_id:
            return _err("Missing query param: document_id", 400, "VALIDATION_ERROR", {"req_id": req_id})

        limit = request.args.get("limit", "20")
        document_id_i = _as_int(document_id, "document_id")
        try:
            limit_i = int(limit)
        except Exception:
            return _err("limit must be integer", 400, "VALIDATION_ERROR", {"req_id": req_id})

        limit_i = max(1, min(limit_i, 100))

        svc = RagService()
        items = svc.history(user_id=user_id, document_id=document_id_i, limit=limit_i)

        return _ok({"items": items, "req_id": req_id})

    except ValueError as e:
        return _err(str(e), 400, "VALIDATION_ERROR", {"req_id": req_id})
    except Exception as e:
        current_app.logger.exception("rag_history failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})
