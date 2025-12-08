from extensions import db
from models import Document, Concept, RoadmapStep, PrereqEdge, StepProgress
from services.prereq_service import PrereqService
from collections import defaultdict, deque

class RoadmapService:
    """Service for building and managing learning roadmaps"""
    
    def __init__(self):
        self.prereq_service = PrereqService()
    
    def build_roadmap(self, document_id):
        """
        Build ordered roadmap steps from concepts and prerequisites
        
        Uses topological sort to order steps based on prerequisite dependencies
        
        Args:
            document_id: ID of the document
        
        Returns:
            List of RoadmapStep objects in order
        """
        concepts = Concept.query.filter_by(document_id=document_id).all()
        if not concepts:
            raise ValueError(f"No concepts found for document {document_id}")
        
        # Build dependency graph
        graph = defaultdict(list)  # concept_id -> [dependent_concept_ids]
        in_degree = defaultdict(int)  # concept_id -> number of prerequisites
        
        for concept in concepts:
            in_degree[concept.id] = 0
        
        # Get all prerequisite edges
        edges = PrereqEdge.query.filter_by(document_id=document_id).all()
        for edge in edges:
            graph[edge.prerequisite_id].append(edge.concept_id)
            in_degree[edge.concept_id] += 1
        
        # Topological sort (Kahn's algorithm)
        queue = deque()
        for concept_id, degree in in_degree.items():
            if degree == 0:
                queue.append(concept_id)
        
        ordered_concept_ids = []
        while queue:
            concept_id = queue.popleft()
            ordered_concept_ids.append(concept_id)
            
            for dependent_id in graph[concept_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # Handle cycles (if any concepts remain)
        remaining_concepts = set(c.id for c in concepts) - set(ordered_concept_ids)
        if remaining_concepts:
            # Add remaining concepts at the end (they might have circular dependencies)
            ordered_concept_ids.extend(remaining_concepts)
        
        # Create roadmap steps
        roadmap_steps = []
        step_order = 0
        
        for concept_id in ordered_concept_ids:
            concept = next((c for c in concepts if c.id == concept_id), None)
            if not concept:
                continue
            
            # Check if step already exists
            existing_step = RoadmapStep.query.filter_by(
                document_id=document_id,
                concept_id=concept_id
            ).first()
            
            if existing_step:
                existing_step.order = step_order
                roadmap_steps.append(existing_step)
            else:
                step = RoadmapStep(
                    document_id=document_id,
                    concept_id=concept_id,
                    order=step_order,
                    step_type="concept"  # or "prerequisite" if needed
                )
                db.session.add(step)
                roadmap_steps.append(step)
            
            step_order += 1
        
        db.session.commit()
        return roadmap_steps
    
    def get_roadmap_for_document(self, document_id, user_id=None):
        """
        Get roadmap steps for a document, optionally with user progress
        
        Args:
            document_id: ID of the document
            user_id: Optional user ID to include progress
        
        Returns:
            List of roadmap step dicts with progress info
        """
        steps = RoadmapStep.query.filter_by(document_id=document_id).order_by(RoadmapStep.order).all()
        
        roadmap_data = []
        for step in steps:
            step_dict = {
                "id": step.id,
                "concept_id": step.concept_id,
                "concept_name": step.concept.name if step.concept else None,
                "order": step.order,
                "step_type": step.step_type,
                "status": "locked"  # default
            }
            
            if user_id:
                progress = StepProgress.query.filter_by(
                    user_id=user_id,
                    roadmap_step_id=step.id
                ).first()
                
                if progress:
                    step_dict["status"] = progress.status
                    step_dict["mastery"] = progress.mastery_score
                else:
                    # Check if prerequisites are cleared
                    if self.prereq_service.check_prerequisites_cleared(step.concept_id, user_id):
                        step_dict["status"] = "unlocked"
                    else:
                        step_dict["status"] = "locked"
            
            roadmap_data.append(step_dict)
        
        return roadmap_data
    
    def get_current_step(self, document_id, user_id):
        """
        Get the current/next step for a user in a document
        
        Args:
            document_id: ID of the document
            user_id: ID of the user
        
        Returns:
            RoadmapStep dict or None
        """
        roadmap = self.get_roadmap_for_document(document_id, user_id)
        
        # Find first unlocked or locked step
        for step in roadmap:
            if step["status"] == "unlocked":
                return step
            elif step["status"] == "locked":
                # Return first locked step (user needs to clear prereqs)
                return step
        
        # All steps cleared
        return None
    
    def unlock_next_steps(self, document_id, user_id, cleared_concept_id):
        """
        Unlock steps that depend on a cleared concept
        
        Args:
            document_id: ID of the document
            user_id: ID of the user
            cleared_concept_id: ID of the concept that was just cleared
        """
        # Get concepts that depend on this one
        dependent_concepts = self.prereq_service.get_dependent_concepts(cleared_concept_id)
        
        for dependent_concept in dependent_concepts:
            # Check if all prerequisites are now cleared
            if self.prereq_service.check_prerequisites_cleared(dependent_concept.id, user_id):
                # Find roadmap step
                roadmap_step = RoadmapStep.query.filter_by(
                    document_id=document_id,
                    concept_id=dependent_concept.id
                ).first()
                
                if roadmap_step:
                    # Ensure progress exists and is unlocked
                    progress = StepProgress.query.filter_by(
                        user_id=user_id,
                        roadmap_step_id=roadmap_step.id
                    ).first()
                    
                    if not progress:
                        progress = StepProgress(
                            user_id=user_id,
                            roadmap_step_id=roadmap_step.id,
                            concept_id=dependent_concept.id,
                            status="unlocked"
                        )
                        db.session.add(progress)
                    
                    elif progress.status == "locked":
                        progress.status = "unlocked"
        
        db.session.commit()

