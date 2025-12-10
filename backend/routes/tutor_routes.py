from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

# Services (you implement these in backend/services/)
from services.tutor_service import TutorService
from services.notes_service import NotesService
from services.flashcard_service import FlashcardService


tutor_bp = Blueprint("tutor", __name__, url_prefix="/api/tutor")


# -------------------------
# Helpers
# -------------------------
HINT_LIMIT_DEFAULT = 3


def _ok(data: Any, status: int = 200):
    return jsonify({"ok": True, "data": data}), status


def _err(message: str, status: int = 400, code: str = "BAD_REQUEST", details: Any = None):
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status


def _get_identity_user_id() -> str:
    ident = get_jwt_identity()
    # allow either string/uuid OR dict identity
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
    if data is None:
        raise ValueError("Request body must be JSON")
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    return data


def _require(data: Dict[str, Any], field: str, typ: Optional[type] = None):
    if field not in data:
        raise ValueError(f"Missing field: {field}")
    val = data[field]
    if typ is not None and not isinstance(val, typ):
        raise ValueError(f"Field '{field}' must be {typ.__name__}")
    return val


def _as_int(x: Any, name: str) -> int:
    try:
        return int(x)
    except Exception:
        raise ValueError(f"Field '{name}' must be an integer")


def _hint_limit() -> int:
    # allow override via config
    return int(current_app.config.get("HINT_LIMIT", HINT_LIMIT_DEFAULT))


# -------------------------
# Routes
# -------------------------

@tutor_bp.post("/hint")
@jwt_required()
def tutor_hint():
    """
    Anti-spoonfeed hint endpoint.
    Input:
      {
        "document_id": 123,
        "step_id": 45,
        "topic": "optional string (fallback if step has no label)",
        "user_text": "what student wrote / last wrong answer",
        "hint_no": 1
      }

    Output:
      {
        "hint_no": 1,
        "hint_limit": 3,
        "hint": "...",
        "micro_question": "...",
        "blocked": false
      }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        data = _json()

        document_id = _as_int(_require(data, "document_id"), "document_id")
        step_id = _as_int(_require(data, "step_id"), "step_id")
        user_text = str(_require(data, "user_text"))
        hint_no = _as_int(_require(data, "hint_no"), "hint_no")
        topic = str(data.get("topic") or "").strip() or None

        limit = _hint_limit()
        if hint_no < 1:
            return _err("hint_no must be >= 1", 400, "VALIDATION_ERROR")
        if hint_no > limit:
            return _ok(
                {
                    "hint_no": hint_no,
                    "hint_limit": limit,
                    "blocked": True,
                    "message": "Hint limit reached. Submit MCQs or unlock notes (if eligible).",
                    "req_id": req_id,
                },
                200,
            )

        tutor = TutorService()
        result = tutor.generate_socratic_hint(
            user_id=user_id,
            document_id=document_id,
            step_id=step_id,
            user_text=user_text,
            hint_no=hint_no,
            topic=topic,
            hint_limit=limit,
        )

        # result must include: hint, micro_question
        if not isinstance(result, dict) or "hint" not in result or "micro_question" not in result:
            return _err("Tutor service returned invalid response", 500, "SERVICE_ERROR", {"req_id": req_id})

        out = {
            "hint_no": hint_no,
            "hint_limit": limit,
            "hint": result.get("hint"),
            "micro_question": result.get("micro_question"),
            "blocked": False,
            "req_id": req_id,
        }
        # optional extras
        if "policy" in result:
            out["policy"] = result["policy"]
        if "safety_flags" in result:
            out["safety_flags"] = result["safety_flags"]

        return _ok(out)

    except ValueError as e:
        return _err(str(e), 400, "VALIDATION_ERROR", {"req_id": req_id})
    except Exception as e:
        current_app.logger.exception("tutor_hint failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})


@tutor_bp.post("/attempt")
@jwt_required()
def tutor_attempt():
    """
    Optional: grade student's micro-question attempt during Socratic loop.
    Input:
      {
        "document_id": 123,
        "step_id": 45,
        "micro_question": "...",
        "student_attempt": "...",
        "hint_no": 1
      }
    Output:
      { "correct": true/false, "feedback": "...", "next_action": "continue_hint|back_to_mcq|unlock_notes" }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        data = _json()

        document_id = _as_int(_require(data, "document_id"), "document_id")
        step_id = _as_int(_require(data, "step_id"), "step_id")
        micro_question = str(_require(data, "micro_question"))
        student_attempt = str(_require(data, "student_attempt"))
        hint_no = _as_int(_require(data, "hint_no"), "hint_no")

        tutor = TutorService()
        result = tutor.grade_micro_attempt(
            user_id=user_id,
            document_id=document_id,
            step_id=step_id,
            micro_question=micro_question,
            student_attempt=student_attempt,
            hint_no=hint_no,
        )

        if not isinstance(result, dict) or "correct" not in result:
            return _err("Tutor service returned invalid response", 500, "SERVICE_ERROR", {"req_id": req_id})

        result["req_id"] = req_id
        return _ok(result)

    except ValueError as e:
        return _err(str(e), 400, "VALIDATION_ERROR", {"req_id": req_id})
    except Exception as e:
        current_app.logger.exception("tutor_attempt failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})


@tutor_bp.post("/unlock-notes")
@jwt_required()
def unlock_notes():
    """
    Unlock/generate full explanation notes for a step.
    This should be allowed only when user score < threshold OR your step_progress says eligible.
    Input:
      { "document_id": 123, "step_id": 45 }
    Output:
      { "unlocked": true, "notes": "...", "notes_type": "explanation" }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        data = _json()
        document_id = _as_int(_require(data, "document_id"), "document_id")
        step_id = _as_int(_require(data, "step_id"), "step_id")

        notes = NotesService()
        result = notes.unlock_or_generate_explanation(
            user_id=user_id,
            document_id=document_id,
            step_id=step_id,
        )

        if not isinstance(result, dict):
            return _err("Notes service returned invalid response", 500, "SERVICE_ERROR", {"req_id": req_id})

        result["req_id"] = req_id
        return _ok(result)

    except ValueError as e:
        return _err(str(e), 400, "VALIDATION_ERROR", {"req_id": req_id})
    except Exception as e:
        current_app.logger.exception("unlock_notes failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})


@tutor_bp.get("/flashcards")
@jwt_required()
def get_flashcards():
    """
    Fetch flashcards for a step (generated earlier or on demand).
    Query params: document_id, step_id
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        document_id = request.args.get("document_id")
        step_id = request.args.get("step_id")
        if document_id is None or step_id is None:
            return _err("Missing query params: document_id, step_id", 400, "VALIDATION_ERROR", {"req_id": req_id})

        document_id_i = _as_int(document_id, "document_id")
        step_id_i = _as_int(step_id, "step_id")

        svc = FlashcardService()
        cards = svc.get_or_generate(
            user_id=user_id,
            document_id=document_id_i,
            step_id=step_id_i,
        )

        return _ok({"flashcards": cards, "req_id": req_id})

    except ValueError as e:
        return _err(str(e), 400, "VALIDATION_ERROR", {"req_id": req_id})
    except Exception as e:
        current_app.logger.exception("get_flashcards failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})
