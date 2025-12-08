"""Chunking service"""
from extensions import db
from models import Document, Chunk
from config import Config

class ChunkService:
    """Service for chunking document text"""
    
    def create_chunks(self, document_id, parsed_data):
        """
        Create chunks from parsed document data
        
        Args:
            document_id: ID of the document
            parsed_data: Dict with 'text' and 'pages' (list of page dicts)
        
        Returns:
            List of Chunk objects
        """
        document = Document.query.get(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        chunks = []
        chunk_index = 0
        
        # Chunk by pages if available
        if "pages" in parsed_data and parsed_data["pages"]:
            for page_data in parsed_data["pages"]:
                page_text = page_data.get("text", "")
                page_number = page_data.get("page_number", 0)
                
                # Split page text into chunks with overlap
                page_chunks = self._chunk_text(
                    text=page_text,
                    chunk_size=Config.CHUNK_SIZE,
                    overlap=Config.CHUNK_OVERLAP
                )
                
                for chunk_text in page_chunks:
                    chunk = Chunk(
                        document_id=document_id,
                        chunk_text=chunk_text,
                        page_number=page_number,
                        chunk_index=chunk_index
                    )
                    db.session.add(chunk)
                    chunks.append(chunk)
                    chunk_index += 1
        else:
            # Fallback: chunk entire text
            full_text = parsed_data.get("text", "")
            text_chunks = self._chunk_text(
                text=full_text,
                chunk_size=Config.CHUNK_SIZE,
                overlap=Config.CHUNK_OVERLAP
            )
            
            for chunk_text in text_chunks:
                chunk = Chunk(
                    document_id=document_id,
                    chunk_text=chunk_text,
                    chunk_index=chunk_index
                )
                db.session.add(chunk)
                chunks.append(chunk)
                chunk_index += 1
        
        db.session.commit()
        return chunks
    
    def _chunk_text(self, text, chunk_size, overlap):
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of chunk strings
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start forward by (chunk_size - overlap)
            start += chunk_size - overlap
        
        return chunks

