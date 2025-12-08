from extensions import db
from models import Concept, PrereqEdge
from integrations.llm_client import LLMClient

class PrereqService:
    """Service for inferring prerequisite relationships between concepts"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        # Fallback prior map for common domain knowledge
        self.fallback_prior_map = self._build_fallback_prior_map()
    
    def _build_fallback_prior_map(self):
        """
        Build a fallback prior map for common prerequisite relationships
        This helps when LLM can't infer prereqs from the document
        """
        return {
            # Math examples
            "calculus": ["algebra", "trigonometry"],
            "linear algebra": ["algebra"],
            "differential equations": ["calculus"],
            # Programming examples
            "object-oriented programming": ["programming basics", "data structures"],
            "design patterns": ["object-oriented programming"],
            "algorithms": ["data structures", "programming basics"],
            # General
            "advanced topics": ["basics", "fundamentals"]
        }
    
    def infer_prerequisites(self, document_id, concepts):
        """
        Infer prerequisites for each concept using LLM + fallback map
        
        Args:
            document_id: ID of the document
            concepts: List of Concept objects
        
        Returns:
            List of PrereqEdge objects
        """
        concept_names = {c.id: c.name for c in concepts}
        concept_name_to_id = {c.name: c.id for c in concepts}
        
        prereq_edges = []
        
        for concept in concepts:
            # Try LLM inference first
            llm_prereqs = self.llm_client.infer_prerequisites(
                concept_name=concept.name,
                concept_description=concept.description,
                all_concepts=[c.name for c in concepts]
            )
            
            # Use fallback if LLM returns few/no prereqs
            if len(llm_prereqs) < 2:
                fallback_prereqs = self._get_fallback_prereqs(concept.name)
                # Merge, prioritizing LLM results
                all_prereq_names = list(set(llm_prereqs + fallback_prereqs))
            else:
                all_prereq_names = llm_prereqs
            
            # Create edges for valid prerequisites (that exist in our concept list)
            for prereq_name in all_prereq_names[:4]:  # Limit to 2-4 prereqs
                prereq_id = concept_name_to_id.get(prereq_name)
                if prereq_id and prereq_id != concept.id:  # Avoid self-loops
                    # Check if edge already exists
                    existing = PrereqEdge.query.filter_by(
                        concept_id=concept.id,
                        prerequisite_id=prereq_id
                    ).first()
                    
                    if not existing:
                        edge = PrereqEdge(
                            document_id=document_id,
                            concept_id=concept.id,
                            prerequisite_id=prereq_id
                        )
                        db.session.add(edge)
                        prereq_edges.append(edge)
        
        db.session.commit()
        return prereq_edges
    
    def _get_fallback_prereqs(self, concept_name):
        """Get prerequisites from fallback prior map"""
        concept_lower = concept_name.lower()
        
        # Direct match
        if concept_lower in self.fallback_prior_map:
            return self.fallback_prior_map[concept_lower]
        
        # Partial match (contains)
        for key, prereqs in self.fallback_prior_map.items():
            if key in concept_lower or concept_lower in key:
                return prereqs
        
        return []
    
    def get_prerequisites_for_concept(self, concept_id):
        """Get all prerequisites for a concept"""
        edges = PrereqEdge.query.filter_by(concept_id=concept_id).all()
        return [edge.prerequisite for edge in edges]
    
    def get_dependent_concepts(self, concept_id):
        """Get all concepts that depend on this concept as a prerequisite"""
        edges = PrereqEdge.query.filter_by(prerequisite_id=concept_id).all()
        return [edge.concept for edge in edges]
    
    def check_prerequisites_cleared(self, concept_id, user_id):
        """
        Check if all prerequisites for a concept are cleared by the user
        
        Args:
            concept_id: ID of the concept
            user_id: ID of the user
        
        Returns:
            bool: True if all prerequisites are cleared
        """
        from models import StepProgress
        
        prereqs = self.get_prerequisites_for_concept(concept_id)
        
        for prereq in prereqs:
            # Check if prerequisite step is cleared
            progress = StepProgress.query.filter_by(
                user_id=user_id,
                concept_id=prereq.id
            ).first()
            
            if not progress or progress.status != "cleared":
                return False
        
        return True

