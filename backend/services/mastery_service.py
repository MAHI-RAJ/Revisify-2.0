"""Mastery tracking service"""
from extensions import db
from models import StepProgress, Concept

class MasteryService:
    """Service for updating and tracking mastery scores"""
    
    def update_mastery(self, user_id, concept_id, score):
        """
        Update mastery score for a concept
        
        Args:
            user_id: ID of the user
            concept_id: ID of the concept
            score: Score from 0.0 to 1.0
        """
        # Find step progress for this concept
        progress = StepProgress.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        if progress:
            # Update mastery (can use weighted average if multiple attempts)
            progress.mastery_score = max(progress.mastery_score or 0.0, score)
        else:
            # Create new progress entry
            from models import RoadmapStep
            roadmap_step = RoadmapStep.query.filter_by(concept_id=concept_id).first()
            if roadmap_step:
                progress = StepProgress(
                    user_id=user_id,
                    roadmap_step_id=roadmap_step.id,
                    concept_id=concept_id,
                    mastery_score=score,
                    status="unlocked"
                )
                db.session.add(progress)
        
        db.session.commit()
    
    def get_mastery_for_concept(self, user_id, concept_id):
        """Get mastery score for a concept"""
        progress = StepProgress.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        return progress.mastery_score if progress else 0.0
    
    def get_overall_mastery(self, user_id, document_id):
        """Get overall mastery for a document"""
        from models import Concept, RoadmapStep
        
        concepts = Concept.query.filter_by(document_id=document_id).all()
        if not concepts:
            return 0.0
        
        total_mastery = 0.0
        count = 0
        
        for concept in concepts:
            mastery = self.get_mastery_for_concept(user_id, concept.id)
            total_mastery += mastery
            count += 1
        
        return total_mastery / count if count > 0 else 0.0

