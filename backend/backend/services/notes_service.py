"""Notes generation service"""
from extensions import db
from models import Note
from integrations.llm_client import LLMClient


class NotesService:
    """Generate and retrieve remediation notes"""

    def __init__(self):
        self.llm_client = LLMClient()

    def get_or_generate_notes(self, roadmap_step_id, concept_name, concept_description, document_context=""):
        """Return existing notes or generate new ones"""
        note = Note.query.filter_by(roadmap_step_id=roadmap_step_id).first()
        if note:
            return note

        notes_data = self.llm_client.generate_notes(
            concept_name=concept_name,
            concept_description=concept_description,
            document_context=document_context
        )

        note = Note(
            roadmap_step_id=roadmap_step_id,
            summary=notes_data.get("summary", ""),
            explanation=notes_data.get("explanation", "")
        )
        db.session.add(note)
        db.session.commit()
        return note

    def get_notes_dict(self, roadmap_step_id):
        """Return notes as dict"""
        note = Note.query.filter_by(roadmap_step_id=roadmap_step_id).first()
        if not note:
            return None
        return {
            "id": note.id,
            "summary": note.summary,
            "explanation": note.explanation
        }

