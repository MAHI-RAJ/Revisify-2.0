"""Vector store service"""
from pathlib import Path
from extensions import db
from models import Document, Chunk
from config import Config
import numpy as np

class VectorStoreService:
    """Service for FAISS vector store operations"""
    
    def build_index(self, document_id, chunks):
        """
        Build FAISS index for document chunks
        
        Args:
            document_id: ID of the document
            chunks: List of Chunk objects with embeddings
        """
        try:
            import faiss
        except ImportError:
            # FAISS not available, skip indexing
            return
        
        if not chunks:
            return
        
        # Extract embeddings
        embeddings = []
        chunk_ids = []
        
        for chunk in chunks:
            if chunk.embedding:
                embeddings.append(chunk.embedding)
                chunk_ids.append(chunk.id)
        
        if not embeddings:
            return
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        dimension = embeddings_array.shape[1]
        
        # Create FAISS index (L2 distance)
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        
        # Save index
        index_path = Path(Config.INDICES_FOLDER) / f"doc_{document_id}.index"
        faiss.write_index(index, str(index_path))
        
        # Save chunk ID mapping
        chunk_map_path = Path(Config.INDICES_FOLDER) / f"doc_{document_id}_chunks.npy"
        np.save(str(chunk_map_path), np.array(chunk_ids))
    
    def search(self, document_id, query_embedding, top_k=None):
        """
        Search for similar chunks
        
        Args:
            document_id: ID of the document
            query_embedding: Query embedding vector
            top_k: Number of results to return
        
        Returns:
            List of chunk IDs with similarity scores
        """
        try:
            import faiss
        except ImportError:
            return []
        
        if top_k is None:
            top_k = Config.RAG_TOP_K
        
        index_path = Path(Config.INDICES_FOLDER) / f"doc_{document_id}.index"
        chunk_map_path = Path(Config.INDICES_FOLDER) / f"doc_{document_id}_chunks.npy"
        
        if not index_path.exists() or not chunk_map_path.exists():
            return []
        
        # Load index and chunk mapping
        index = faiss.read_index(str(index_path))
        chunk_ids = np.load(str(chunk_map_path))
        
        # Convert query to numpy array
        query_array = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = index.search(query_array, top_k)
        
        # Return results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(chunk_ids):
                results.append({
                    "chunk_id": int(chunk_ids[idx]),
                    "distance": float(distance),
                    "similarity": 1.0 / (1.0 + distance)  # Convert distance to similarity
                })
        
        return results

