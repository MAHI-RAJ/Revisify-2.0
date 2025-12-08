"""Document ingestion service"""
from pathlib import Path
from extensions import db
from models import Document
from integrations.parsers.pdf_parser import PDFParser
from services.chunk_service import ChunkService
from services.embed_service import EmbedService
from services.vector_store_service import VectorStoreService
from services.concept_service import ConceptService
from services.prereq_service import PrereqService
from services.roadmap_service import RoadmapService

class IngestService:
    """Service for processing uploaded documents"""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.chunk_service = ChunkService()
        self.embed_service = EmbedService()
        self.vector_store_service = VectorStoreService()
        self.concept_service = ConceptService()
        self.prereq_service = PrereqService()
        self.roadmap_service = RoadmapService()
    
    def process_document(self, document_id):
        """
        Process a document through the full pipeline
        
        Args:
            document_id: ID of the document to process
        """
        document = Document.query.get(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        try:
            # 1. Extract text
            if document.file_type == "pdf":
                parsed_data = self.pdf_parser.parse(document.filepath)
            else:
                # TODO: Add PPT and DOCX parsers
                raise ValueError(f"File type {document.file_type} not yet supported")
            
            raw_text = parsed_data.get("text", "")
            
            # 2. Chunk text
            chunks = self.chunk_service.create_chunks(document_id, parsed_data)
            
            # 3. Generate embeddings
            self.embed_service.generate_embeddings(chunks)
            
            # 4. Build FAISS index
            self.vector_store_service.build_index(document_id, chunks)
            
            # 5. Extract concepts
            concepts = self.concept_service.extract_concepts(document_id, raw_text)
            
            # 6. Infer prerequisites
            prereq_edges = self.prereq_service.infer_prerequisites(document_id, concepts)
            
            # 7. Build roadmap
            roadmap_steps = self.roadmap_service.build_roadmap(document_id)
            
            # 8. Mark document as ready
            document.status = "ready"
            db.session.commit()
            
        except Exception as e:
            document.status = "error"
            document.error_message = str(e)
            db.session.commit()
            raise

