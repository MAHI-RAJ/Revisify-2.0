"""Attempt and grading routes"""
from flask import Blueprint, request, jsonify
from routes.auth_routes import token_required
from services.grading_service import GradingService


attempt_bp = Blueprint("attempts", __name__)
grading_service = GradingService()


@attempt_bp.route("/submit", methods=["POST"])
@token_required
def submit_attempt():
    """POST /api/attempts/submit - grade MCQ attempt"""
    try:
        data = request.get_json() or {}
        mcq_set_id = data.get("mcq_set_id")
        answers = data.get("answers", {})

        if not mcq_set_id or not isinstance(answers, dict):
            return jsonify({"error": "mcq_set_id and answers are required"}), 400

        user = request.current_user
        result = grading_service.grade_attempt(
            user_id=user.id,
            mcq_set_id=mcq_set_id,
            answers=answers
        )

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Failed to grade attempt", "details": str(e)}), 500

