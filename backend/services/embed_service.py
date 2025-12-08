"""Embedding service"""
from extensions import db
from models import Chunk
from config import Config
import numpy as np

class EmbedService:
    """Service for generating embeddings"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        except ImportError:
            # Fallback: use a simple hash-based embedding (not recommended for production)
            self.model = None
    
    def generate_embeddings(self, chunks):
        """
        Generate embeddings for chunks
        
        Args:
            chunks: List of Chunk objects
        """
        if not chunks:
            return
        
        if not self.model:
            # Fallback: create dummy embeddings
            for chunk in chunks:
                chunk.embedding = np.random.rand(Config.EMBEDDING_DIMENSION).tolist()
            db.session.commit()
            return
        
        # Extract texts
        texts = [chunk.chunk_text for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Store embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()
        
        db.session.commit()

