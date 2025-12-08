from extensions import db
from models import RoadmapStep, Hint, StepProgress
from integrations.llm_client import LLMClient
from integrations.safety.anti_spoonfeed import AntiSpoonfeedFilter
from config import Config

class TutorService:
    """Service for providing anti-spoonfeeding hints and assistance"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.anti_spoonfeed_filter = AntiSpoonfeedFilter()
    
    def get_hint(self, user_id, roadmap_step_id, hint_number, question_context=""):
        """
        Get a Socratic hint with micro-question (max 3 hints per step)
        
        Args:
            user_id: ID of the user
            roadmap_step_id: ID of the roadmap step
            hint_number: Which hint (1, 2, or 3)
            question_context: Optional context about what the user is struggling with
        
        Returns:
            Dict with hint text and micro-question
        """
        # Check hint count
        existing_hints = Hint.query.filter_by(
            user_id=user_id,
            roadmap_step_id=roadmap_step_id
        ).count()
        
        if existing_hints >= Config.MAX_HINTS_PER_STEP:
            return {
                "error": f"Maximum {Config.MAX_HINTS_PER_STEP} hints allowed per step",
                "hint_count": existing_hints
            }
        
        if hint_number > Config.MAX_HINTS_PER_STEP:
            return {
                "error": f"Hint number must be between 1 and {Config.MAX_HINTS_PER_STEP}",
                "hint_number": hint_number
            }
        
        # Get step context
        roadmap_step = RoadmapStep.query.get(roadmap_step_id)
        if not roadmap_step:
            raise ValueError(f"Roadmap step {roadmap_step_id} not found")
        
        concept_name = roadmap_step.concept.name if roadmap_step.concept else ""
        concept_description = roadmap_step.concept.description if roadmap_step.concept else ""
        
        # Generate hint using LLM
        hint_data = self.llm_client.generate_hint(
            concept_name=concept_name,
            concept_description=concept_description,
            hint_number=hint_number,
            question_context=question_context,
            previous_hints=self._get_previous_hints(user_id, roadmap_step_id)
        )
        
        # Apply anti-spoonfeed filter
        filtered_hint = self.anti_spoonfeed_filter.filter_hint(hint_data["hint"])
        filtered_micro_q = self.anti_spoonfeed_filter.filter_hint(hint_data.get("micro_question", ""))
        
        # Store hint
        hint = Hint(
            user_id=user_id,
            roadmap_step_id=roadmap_step_id,
            hint_number=hint_number,
            hint_text=filtered_hint,
            micro_question=filtered_micro_q
        )
        db.session.add(hint)
        db.session.commit()
        
        return {
            "hint_number": hint_number,
            "hint": filtered_hint,
            "micro_question": filtered_micro_q,
            "hints_remaining": Config.MAX_HINTS_PER_STEP - (existing_hints + 1)
        }
    
    def _get_previous_hints(self, user_id, roadmap_step_id):
        """Get previously given hints for context"""
        hints = Hint.query.filter_by(
            user_id=user_id,
            roadmap_step_id=roadmap_step_id
        ).order_by(Hint.hint_number).all()
        
        return [{
            "hint_number": h.hint_number,
            "hint": h.hint_text,
            "micro_question": h.micro_question
        } for h in hints]
    
    def get_hint_count(self, user_id, roadmap_step_id):
        """Get number of hints used for a step"""
        return Hint.query.filter_by(
            user_id=user_id,
            roadmap_step_id=roadmap_step_id
        ).count()
    
    def should_unlock_notes(self, user_id, roadmap_step_id):
        """
        Check if full notes should be unlocked based on performance
        
        Notes are unlocked if:
        - User score is below threshold, OR
        - User has used all 3 hints
        
        Returns:
            bool: True if notes should be unlocked
        """
        # Check step progress
        progress = StepProgress.query.filter_by(
            user_id=user_id,
            roadmap_step_id=roadmap_step_id
        ).first()
        
        if not progress:
            return False
        
        # Check if score is below threshold
        from config import Config
        if progress.mastery_score is not None and progress.mastery_score < Config.MCQ_THRESHOLD_SCORE:
            return True
        
        # Check if all hints used
        hint_count = self.get_hint_count(user_id, roadmap_step_id)
        if hint_count >= Config.MAX_HINTS_PER_STEP:
            return True
        
        return False

