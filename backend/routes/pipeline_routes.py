from flask import Blueprint, request, jsonify
from extensions import db
from models import Document
from routes.auth_routes import token_required

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/status/<int:doc_id>", methods=["GET"])
@token_required
def get_pipeline_status(doc_id):
    """GET /api/pipeline/status/<doc_id> - Get processing pipeline status"""
    try:
        user = request.current_user
        document = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Return detailed pipeline status
        status_info = {
            "document_id": document.id,
            "status": document.status,
            "error_message": document.error_message,
            "stages": {
                "upload": "completed",
                "extraction": "completed" if document.status != "processing" else "pending",
                "chunking": "completed" if document.status != "processing" else "pending",
                "embedding": "completed" if document.status != "processing" else "pending",
                "indexing": "completed" if document.status != "processing" else "pending",
                "concept_extraction": "completed" if document.status == "ready" else "pending",
                "prereq_inference": "completed" if document.status == "ready" else "pending",
                "roadmap_build": "completed" if document.status == "ready" else "pending"
            }
        }
        
        # If document has chunks/concepts, mark stages as completed
        from models import Chunk, Concept
        if Chunk.query.filter_by(document_id=doc_id).first():
            status_info["stages"]["chunking"] = "completed"
        if Concept.query.filter_by(document_id=doc_id).first():
            status_info["stages"]["concept_extraction"] = "completed"
        
        return jsonify(status_info), 200
    
    except Exception as e:
        return jsonify({"error": "Failed to get pipeline status", "details": str(e)}), 500

@pipeline_bp.route("/progress/<int:doc_id>", methods=["GET"])
@token_required
def get_pipeline_progress(doc_id):
    """GET /api/pipeline/progress/<doc_id> - Get detailed processing progress"""
    try:
        user = request.current_user
        document = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        from models import Chunk, Concept, RoadmapStep
        
        # Count progress indicators
        chunk_count = Chunk.query.filter_by(document_id=doc_id).count()
        concept_count = Concept.query.filter_by(document_id=doc_id).count()
        roadmap_step_count = RoadmapStep.query.join(Concept).filter(Concept.document_id == doc_id).count()
        
        progress = {
            "document_id": document.id,
            "status": document.status,
            "progress_percentage": 0,
            "current_stage": "upload",
            "details": {
                "chunks_extracted": chunk_count,
                "concepts_identified": concept_count,
                "roadmap_steps_created": roadmap_step_count
            }
        }
        
        # Calculate progress percentage
        if document.status == "ready":
            progress["progress_percentage"] = 100
            progress["current_stage"] = "completed"
        elif document.status == "error":
            progress["current_stage"] = "error"
        elif chunk_count > 0:
            if concept_count > 0:
                if roadmap_step_count > 0:
                    progress["progress_percentage"] = 90
                    progress["current_stage"] = "roadmap_build"
                else:
                    progress["progress_percentage"] = 70
                    progress["current_stage"] = "concept_extraction"
            else:
                progress["progress_percentage"] = 50
                progress["current_stage"] = "chunking"
        else:
            progress["progress_percentage"] = 20
            progress["current_stage"] = "extraction"
        
        return jsonify(progress), 200
    
    except Exception as e:
        return jsonify({"error": "Failed to get progress", "details": str(e)}), 500

