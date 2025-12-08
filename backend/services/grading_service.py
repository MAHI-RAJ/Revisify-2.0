from extensions import db
from models import MCQSet, MCQ, Attempt, StepProgress
from services.mcq_service import MCQService
from services.mastery_service import MasteryService
from config import Config

class GradingService:
    """Service for grading MCQ attempts and updating progress"""
    
    def __init__(self):
        self.mcq_service = MCQService()
        self.mastery_service = MasteryService()
    
    def grade_attempt(self, user_id, mcq_set_id, answers):
        """
        Grade a user's MCQ attempt
        
        Args:
            user_id: ID of the user
            mcq_set_id: ID of the MCQ set
            answers: Dict mapping question_number -> answer (A, B, C, or D)
        
        Returns:
            Dict with score, results, and threshold status
        """
        # Get correct answers
        correct_answers = self.mcq_service.get_correct_answers(mcq_set_id)
        
        # Get MCQ set
        mcq_set = MCQSet.query.get(mcq_set_id)
        if not mcq_set:
            raise ValueError(f"MCQ set {mcq_set_id} not found")
        
        total_questions = mcq_set.question_count
        correct_count = 0
        
        # Grade each answer
        results = {}
        for question_num, user_answer in answers.items():
            correct_answer = correct_answers.get(question_num)
            is_correct = user_answer.upper() == correct_answer.upper() if correct_answer else False
            
            if is_correct:
                correct_count += 1
            
            results[question_num] = {
                "user_answer": user_answer.upper(),
                "correct_answer": correct_answer,
                "is_correct": is_correct
            }
        
        # Calculate score
        score = correct_count / total_questions if total_questions > 0 else 0
        
        # Check threshold
        threshold = Config.MCQ_THRESHOLD_SCORE
        passed = score >= threshold
        
        # Save attempt
        attempt = Attempt(
            user_id=user_id,
            mcq_set_id=mcq_set_id,
            score=score,
            correct_count=correct_count,
            total_count=total_questions,
            answers_json=str(results)  # Store as JSON string (or use JSON column if available)
        )
        db.session.add(attempt)
        
        # Update step progress
        roadmap_step_id = mcq_set.roadmap_step_id
        self._update_step_progress(user_id, roadmap_step_id, score, passed)
        
        # Update mastery
        from models import RoadmapStep
        roadmap_step = RoadmapStep.query.get(roadmap_step_id)
        if roadmap_step and roadmap_step.concept_id:
            self.mastery_service.update_mastery(
                user_id=user_id,
                concept_id=roadmap_step.concept_id,
                score=score
            )
        
        db.session.commit()
        
        return {
            "score": score,
            "correct_count": correct_count,
            "total_count": total_questions,
            "passed": passed,
            "threshold": threshold,
            "results": results,
            "attempt_id": attempt.id
        }
    
    def _update_step_progress(self, user_id, roadmap_step_id, score, passed):
        """Update step progress based on attempt"""
        from models import RoadmapStep
        
        progress = StepProgress.query.filter_by(
            user_id=user_id,
            roadmap_step_id=roadmap_step_id
        ).first()
        
        roadmap_step = RoadmapStep.query.get(roadmap_step_id)
        
        if not progress:
            progress = StepProgress(
                user_id=user_id,
                roadmap_step_id=roadmap_step_id,
                concept_id=roadmap_step.concept_id if roadmap_step else None,
                status="unlocked"
            )
            db.session.add(progress)
        
        # Update status based on performance
        if passed:
            progress.status = "cleared"
        else:
            # Keep as unlocked, but mark that notes should be available
            progress.status = "unlocked"
        
        # Update mastery score
        progress.mastery_score = score
        
        # Unlock next steps if cleared
        if passed:
            from services.roadmap_service import RoadmapService
            roadmap_service = RoadmapService()
            if progress.concept_id and roadmap_step:
                roadmap_service.unlock_next_steps(
                    document_id=roadmap_step.document_id,
                    user_id=user_id,
                    cleared_concept_id=progress.concept_id
                )
        
        db.session.flush()

