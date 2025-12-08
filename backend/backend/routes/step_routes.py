"""Step routes for learning loop"""
from flask import Blueprint, jsonify, request
from routes.auth_routes import token_required
from services.roadmap_service import RoadmapService
from services.mcq_service import MCQService
from services.notes_service import NotesService
from services.flashcard_service import FlashcardService
from services.tutor_service import TutorService
from services.prereq_service import PrereqService
from models import RoadmapStep, StepProgress


step_bp = Blueprint("steps", __name__)
roadmap_service = RoadmapService()
mcq_service = MCQService()
notes_service = NotesService()
flashcard_service = FlashcardService()
tutor_service = TutorService()
prereq_service = PrereqService()


def _user_can_access_step(step: RoadmapStep, user_id: int) -> bool:
    """Check gating: prerequisites cleared or no prereqs"""
    if not step or not step.concept_id:
        return False
    return prereq_service.check_prerequisites_cleared(step.concept_id, user_id)


@step_bp.route("/<int:step_id>", methods=["GET"])
@token_required
def get_step(step_id):
    """GET /api/steps/<step_id> - step metadata + progress"""
    user = request.current_user
    step = RoadmapStep.query.get(step_id)
    if not step or step.document.user_id != user.id:
        return jsonify({"error": "Step not found"}), 404

    progress = StepProgress.query.filter_by(user_id=user.id, roadmap_step_id=step_id).first()
    status = progress.status if progress else ("unlocked" if _user_can_access_step(step, user.id) else "locked")

    return jsonify({
        "id": step.id,
        "concept_id": step.concept_id,
        "concept_name": step.concept.name if step.concept else None,
        "order": step.order,
        "status": status,
        "mastery": progress.mastery_score if progress else 0.0
    }), 200


@step_bp.route("/<int:step_id>/mcqs", methods=["GET"])
@token_required
def get_step_mcqs(step_id):
    """GET /api/steps/<step_id>/mcqs - returns/generates MCQ set"""
    user = request.current_user
    step = RoadmapStep.query.get(step_id)
    if not step or step.document.user_id != user.id:
        return jsonify({"error": "Step not found"}), 404

    if not _user_can_access_step(step, user.id):
        return jsonify({"error": "Prerequisites not cleared yet"}), 403

    concept = step.concept
    if not concept:
        return jsonify({"error": "Concept missing for this step"}), 400

    mcq_set = mcq_service.generate_mcq_set(
        roadmap_step_id=step.id,
        concept_name=concept.name,
        concept_description=concept.description or "",
        document_context=""
    )

    mcqs_payload = mcq_service.get_mcq_set_for_step(step.id)
    return jsonify({"mcq_set": mcqs_payload}), 200


@step_bp.route("/<int:step_id>/notes", methods=["GET"])
@token_required
def get_step_notes(step_id):
    """GET /api/steps/<step_id>/notes - returns/generates remediation notes if unlocked"""
    user = request.current_user
    step = RoadmapStep.query.get(step_id)
    if not step or step.document.user_id != user.id:
        return jsonify({"error": "Step not found"}), 404

    # Gating: allow notes if below threshold or hints exhausted
    if not tutor_service.should_unlock_notes(user.id, step_id):
        return jsonify({"error": "Notes locked. Use hints or submit attempt first."}), 403

    concept = step.concept
    if not concept:
        return jsonify({"error": "Concept missing for this step"}), 400

    note = notes_service.get_or_generate_notes(
        roadmap_step_id=step.id,
        concept_name=concept.name,
        concept_description=concept.description or "",
        document_context=""
    )

    return jsonify({
        "note": {
            "id": note.id,
            "summary": note.summary,
            "explanation": note.explanation
        }
    }), 200


@step_bp.route("/<int:step_id>/flashcards", methods=["GET"])
@token_required
def get_step_flashcards(step_id):
    """GET /api/steps/<step_id>/flashcards - returns/generates flashcards"""
    user = request.current_user
    step = RoadmapStep.query.get(step_id)
    if not step or step.document.user_id != user.id:
        return jsonify({"error": "Step not found"}), 404

    concept = step.concept
    if not concept:
        return jsonify({"error": "Concept missing for this step"}), 400

    flashcards = flashcard_service.get_or_generate_flashcards(
        roadmap_step_id=step.id,
        concept_name=concept.name,
        concept_description=concept.description or "",
        count=5
    )

    return jsonify({"flashcards": flashcards}), 200

