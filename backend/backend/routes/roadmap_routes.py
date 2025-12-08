"""Roadmap routes"""
from flask import Blueprint, jsonify, request
from routes.auth_routes import token_required
from services.roadmap_service import RoadmapService
from models import Document


roadmap_bp = Blueprint("roadmap", __name__)
roadmap_service = RoadmapService()


@roadmap_bp.route("/<int:doc_id>", methods=["GET"])
@token_required
def get_roadmap(doc_id):
    """GET /api/roadmap/<doc_id> - return ordered roadmap with progress"""
    user = request.current_user
    document = Document.query.filter_by(id=doc_id, user_id=user.id).first()
    if not document:
        return jsonify({"error": "Document not found"}), 404

    try:
        roadmap = roadmap_service.get_roadmap_for_document(doc_id, user_id=user.id)
        return jsonify({"roadmap": roadmap}), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch roadmap", "details": str(e)}), 500


@roadmap_bp.route("/current/<int:doc_id>", methods=["GET"])
@token_required
def get_current_step(doc_id):
    """GET /api/roadmap/current/<doc_id> - return current or next step"""
    user = request.current_user
    document = Document.query.filter_by(id=doc_id, user_id=user.id).first()
    if not document:
        return jsonify({"error": "Document not found"}), 404

    try:
        current_step = roadmap_service.get_current_step(doc_id, user_id=user.id)
        return jsonify({"current_step": current_step}), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch current step", "details": str(e)}), 500

