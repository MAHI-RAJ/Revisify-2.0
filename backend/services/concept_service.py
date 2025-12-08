from extensions import db
from models import Document, Concept
from integrations.llm_client import LLMClient
import re

class ConceptService:
    """Service for extracting and managing concepts from documents"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def extract_concepts(self, document_id, raw_text):
        """
        Extract key concepts from document text using LLM
        
        Args:
            document_id: ID of the document
            raw_text: Raw text content from document
        
        Returns:
            List of Concept objects
        """
        document = Document.query.get(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Use LLM to extract concepts
        concepts_data = self.llm_client.extract_concepts(raw_text)
        
        # Canonicalize and deduplicate
        canonicalized = self.canonicalize_concepts(concepts_data)
        
        # Store concepts
        concepts = []
        for concept_data in canonicalized:
            concept = Concept(
                document_id=document_id,
                name=concept_data["name"],
                description=concept_data.get("description", ""),
                canonical_name=concept_data.get("canonical_name", concept_data["name"])
            )
            db.session.add(concept)
            concepts.append(concept)
        
        db.session.commit()
        return concepts
    
    def canonicalize_concepts(self, concepts_data):
        """
        Canonicalize concept names to handle duplicates and variations
        
        Args:
            concepts_data: List of concept dicts from LLM
        
        Returns:
            Deduplicated and canonicalized list
        """
        canonical_map = {}
        canonicalized = []
        
        for concept in concepts_data:
            name = concept.get("name", "").strip()
            if not name:
                continue
            
            # Normalize: lowercase, remove extra spaces
            normalized = re.sub(r'\s+', ' ', name.lower().strip())
            
            # Check for duplicates (simple approach - can be enhanced)
            is_duplicate = False
            for canonical_name, existing in canonical_map.items():
                # Check similarity (simple substring check, can use fuzzy matching)
                if normalized in canonical_name.lower() or canonical_name.lower() in normalized:
                    # Merge into existing
                    existing["description"] = existing.get("description", "") + " " + concept.get("description", "")
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                canonical_name = name.title()  # Capitalize properly
                canonical_map[canonical_name] = {
                    "name": name,
                    "canonical_name": canonical_name,
                    "description": concept.get("description", "")
                }
                canonicalized.append(canonical_map[canonical_name])
        
        return canonicalized
    
    def get_concepts_for_document(self, document_id):
        """Get all concepts for a document"""
        return Concept.query.filter_by(document_id=document_id).all()
    
    def get_concept_by_id(self, concept_id):
        """Get a concept by ID"""
        return Concept.query.get(concept_id)

