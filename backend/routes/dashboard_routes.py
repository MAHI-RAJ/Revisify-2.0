from __future__ import annotations

import uuid
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.dashboard_service import DashboardService
from services.auth_service import AuthService


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api")


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


def _as_int(x: Any, name: str) -> int:
    try:
        return int(x)
    except Exception:
        raise ValueError(f"Field '{name}' must be an integer")


# -------------------------
# Routes
# -------------------------

@dashboard_bp.get("/dashboard")
@jwt_required()
def document_dashboard():
    """
    Document dashboard:
    GET /api/dashboard?document_id=123

    Output:
      {
        "document_id": 123,
        "overall_progress": 0.52,
        "cleared_steps": 8,
        "total_steps": 14,
        "concepts": [
          {"concept_id": 1, "name": "Binary Search", "mastery": 0.7},
          ...
        ],
        "weak_concepts": [...]
      }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        document_id = request.args.get("document_id")
        if not document_id:
            return _err("Missing query param: document_id", 400, "VALIDATION_ERROR", {"req_id": req_id})

        document_id_i = _as_int(document_id, "document_id")
        svc = DashboardService()
        data = svc.get_document_dashboard(user_id=user_id, document_id=document_id_i)

        if not isinstance(data, dict):
            return _err("Dashboard service returned invalid response", 500, "SERVICE_ERROR", {"req_id": req_id})

        data["req_id"] = req_id
        return _ok(data)

    except ValueError as e:
        return _err(str(e), 400, "VALIDATION_ERROR", {"req_id": req_id})
    except Exception as e:
        current_app.logger.exception("document_dashboard failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})


@dashboard_bp.get("/dashboard/overview")
@jwt_required()
def dashboard_overview():
    """
    Cross-document overview for the logged-in user.
    GET /api/dashboard/overview

    Output (example):
      {
        "documents": [
          {"document_id": 123, "filename": "...", "progress": 0.52, "last_activity": "..."},
          ...
        ],
        "totals": { "docs": 3, "avg_progress": 0.41 }
      }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        svc = DashboardService()
        data = svc.get_overview(user_id=user_id)

        if not isinstance(data, dict):
            return _err("Dashboard service returned invalid response", 500, "SERVICE_ERROR", {"req_id": req_id})

        data["req_id"] = req_id
        return _ok(data)

    except Exception as e:
        current_app.logger.exception("dashboard_overview failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})


@dashboard_bp.get("/profile")
@jwt_required()
def profile():
    """
    Simple user profile endpoint (for UI header / settings).
    GET /api/profile
    Output:
      { "id": "...", "name": "...", "email": "...", "created_at": "..." }
    """
    req_id = str(uuid.uuid4())
    try:
        user_id = _get_identity_user_id()
        auth = AuthService()
        user = auth.get_user_profile(user_id=user_id)

        if not isinstance(user, dict):
            return _err("Auth service returned invalid response", 500, "SERVICE_ERROR", {"req_id": req_id})

        user["req_id"] = req_id
        return _ok(user)

    except Exception as e:
        current_app.logger.exception("profile failed req_id=%s err=%s", req_id, e)
        return _err("Internal server error", 500, "INTERNAL_ERROR", {"req_id": req_id})
