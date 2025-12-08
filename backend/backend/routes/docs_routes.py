from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models import Document, User
from routes.auth_routes import token_required
from services.ingest_service import IngestService
import os
from pathlib import Path

docs_bp = Blueprint("docs", __name__)
ingest_service = IngestService()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

@docs_bp.route("/upload", methods=["POST"])
@token_required
def upload_document():
    """POST /api/docs/upload - Upload a document (PDF/PPT/DOCX)"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type",
                "allowed_types": list(current_app.config["ALLOWED_EXTENSIONS"])
            }), 400
        
        user = request.current_user
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = int(os.path.getmtime(file.filename) if os.path.exists(file.filename) else 0)
        unique_filename = f"{user.id}_{timestamp}_{filename}"
        filepath = Path(current_app.config["UPLOAD_FOLDER"]) / unique_filename
        file.save(str(filepath))
        
        # Create document record
        document = Document(
            user_id=user.id,
            filename=filename,
            filepath=str(filepath),
            file_type=filename.rsplit(".", 1)[1].lower(),
            status="processing"
        )
        db.session.add(document)
        db.session.commit()
        
        # Trigger processing pipeline (async in production, sync for now)
        # In production, use Celery or similar task queue
        try:
            ingest_service.process_document(document.id)
        except Exception as e:
            # Log error but don't fail upload
            current_app.logger.error(f"Processing error for doc {document.id}: {str(e)}")
            document.status = "error"
            document.error_message = str(e)
            db.session.commit()
        
        return jsonify({
            "message": "Document uploaded successfully",
            "document": {
                "id": document.id,
                "filename": document.filename,
                "status": document.status,
                "created_at": document.created_at.isoformat() if document.created_at else None
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Upload failed", "details": str(e)}), 500

@docs_bp.route("/list", methods=["GET"])
@token_required
def list_documents():
    """GET /api/docs/list - List all documents for current user"""
    try:
        user = request.current_user
        documents = Document.query.filter_by(user_id=user.id).order_by(Document.created_at.desc()).all()
        
        return jsonify({
            "documents": [{
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "status": doc.status,
                "error_message": doc.error_message,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
            } for doc in documents]
        }), 200
    
    except Exception as e:
        return jsonify({"error": "Failed to list documents", "details": str(e)}), 500

@docs_bp.route("/<int:doc_id>", methods=["GET"])
@token_required
def get_document(doc_id):
    """GET /api/docs/<doc_id> - Get document details"""
    try:
        user = request.current_user
        document = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "status": document.status,
            "error_message": document.error_message,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }), 200
    
    except Exception as e:
        return jsonify({"error": "Failed to get document", "details": str(e)}), 500

@docs_bp.route("/status/<int:doc_id>", methods=["GET"])
@token_required
def get_document_status(doc_id):
    """GET /api/docs/status/<doc_id> - Get document processing status"""
    try:
        user = request.current_user
        document = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({
            "id": document.id,
            "status": document.status,
            "error_message": document.error_message,
            "progress": getattr(document, "processing_progress", None)  # If tracking progress
        }), 200
    
    except Exception as e:
        return jsonify({"error": "Failed to get status", "details": str(e)}), 500

