"""Dashboard aggregation service"""
from models import Document, RoadmapStep, StepProgress, Concept
from services.mastery_service import MasteryService


class DashboardService:
    """Aggregate mastery and progress for dashboard widgets"""

    def __init__(self):
        self.mastery_service = MasteryService()

    def get_dashboard(self, user_id, document_id):
        """Return dashboard stats for a document"""
        document = Document.query.filter_by(id=document_id, user_id=user_id).first()
        if not document:
            raise ValueError("Document not found")

        steps = RoadmapStep.query.filter_by(document_id=document_id).all()
        progress_rows = StepProgress.query.filter_by(user_id=user_id).all()

        status_counts = {"cleared": 0, "unlocked": 0, "locked": 0}
        mastery_scores = []

        progress_map = {(p.roadmap_step_id): p for p in progress_rows}

        for step in steps:
            prog = progress_map.get(step.id)
            status = prog.status if prog else "locked"
            status_counts[status] = status_counts.get(status, 0) + 1
            if prog and prog.mastery_score is not None:
                mastery_scores.append(prog.mastery_score)

        total_steps = len(steps)
        cleared = status_counts.get("cleared", 0)
        overall_progress = (cleared / total_steps) * 100 if total_steps else 0
        overall_mastery = sum(mastery_scores) / len(mastery_scores) if mastery_scores else 0

        concept_count = Concept.query.filter_by(document_id=document_id).count()

        return {
            "document_id": document_id,
            "filename": document.filename,
            "status": document.status,
            "progress": {
                "total_steps": total_steps,
                "cleared": cleared,
                "unlocked": status_counts.get("unlocked", 0),
                "locked": status_counts.get("locked", 0),
                "percent": overall_progress
            },
            "mastery": overall_mastery,
            "concepts": concept_count
        }

