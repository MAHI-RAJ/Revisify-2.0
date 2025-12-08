from extensions import db
from models import RoadmapStep, MCQSet, MCQ
from integrations.llm_client import LLMClient
from config import Config
import random

class MCQService:
    """Service for generating and managing MCQ sets"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def generate_mcq_set(self, roadmap_step_id, concept_name, concept_description, document_context=""):
        """
        Generate a set of 5-10 MCQs for a roadmap step
        
        Args:
            roadmap_step_id: ID of the roadmap step
            concept_name: Name of the concept
            concept_description: Description of the concept
            document_context: Optional context from document chunks
        
        Returns:
            MCQSet object with associated MCQ objects
        """
        # Check if MCQ set already exists
        existing_set = MCQSet.query.filter_by(roadmap_step_id=roadmap_step_id).first()
        if existing_set:
            return existing_set
        
        # Determine number of MCQs (5-10)
        num_mcqs = random.randint(Config.MCQ_COUNT_MIN, Config.MCQ_COUNT_MAX)
        
        # Generate MCQs using LLM
        mcqs_data = self.llm_client.generate_mcqs(
            concept_name=concept_name,
            concept_description=concept_description,
            document_context=document_context,
            num_questions=num_mcqs
        )
        
        # Create MCQ set
        mcq_set = MCQSet(
            roadmap_step_id=roadmap_step_id,
            question_count=len(mcqs_data)
        )
        db.session.add(mcq_set)
        db.session.flush()  # Get ID
        
        # Create MCQ objects
        mcqs = []
        for idx, mcq_data in enumerate(mcqs_data):
            mcq = MCQ(
                mcq_set_id=mcq_set.id,
                question_number=idx + 1,
                question_text=mcq_data["question"],
                option_a=mcq_data["options"]["A"],
                option_b=mcq_data["options"]["B"],
                option_c=mcq_data["options"]["C"],
                option_d=mcq_data["options"].get("D", ""),
                correct_answer=mcq_data["correct_answer"].upper(),  # A, B, C, or D
                explanation=mcq_data.get("explanation", "")
            )
            db.session.add(mcq)
            mcqs.append(mcq)
        
        db.session.commit()
        return mcq_set
    
    def get_mcq_set_for_step(self, roadmap_step_id):
        """Get MCQ set for a roadmap step"""
        mcq_set = MCQSet.query.filter_by(roadmap_step_id=roadmap_step_id).first()
        if not mcq_set:
            return None
        
        mcqs = MCQ.query.filter_by(mcq_set_id=mcq_set.id).order_by(MCQ.question_number).all()
        
        return {
            "id": mcq_set.id,
            "question_count": mcq_set.question_count,
            "questions": [{
                "id": mcq.id,
                "question_number": mcq.question_number,
                "question_text": mcq.question_text,
                "options": {
                    "A": mcq.option_a,
                    "B": mcq.option_b,
                    "C": mcq.option_c,
                    "D": mcq.option_d
                }
                # Don't include correct_answer or explanation in response
            } for mcq in mcqs]
        }
    
    def get_correct_answers(self, mcq_set_id):
        """Get correct answers for grading (internal use)"""
        mcqs = MCQ.query.filter_by(mcq_set_id=mcq_set_id).all()
        return {mcq.question_number: mcq.correct_answer for mcq in mcqs}
    
    def get_explanations(self, mcq_set_id):
        """Get explanations for MCQs"""
        mcqs = MCQ.query.filter_by(mcq_set_id=mcq_set_id).order_by(MCQ.question_number).all()
        return {
            mcq.question_number: {
                "correct_answer": mcq.correct_answer,
                "explanation": mcq.explanation
            }
            for mcq in mcqs
        }

