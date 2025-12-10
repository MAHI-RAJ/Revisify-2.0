"""RAG service for Ask-Doc"""
import numpy as np
from config import Config
from models import Chunk
from integrations.llm_client import LLMClient
from services.embed_service import EmbedService
from services.vector_store_service import VectorStoreService


class RagService:
    """Retrieve chunks and generate grounded answers with citations"""

    def __init__(self):
        self.llm_client = LLMClient()
        self.embed_service = EmbedService()
        self.vector_store_service = VectorStoreService()

    def _embed_query(self, query):
        """Embed query text"""
        if self.embed_service.model:
            return self.embed_service.model.encode([query])[0]
        return np.random.rand(Config.EMBEDDING_DIMENSION)

    def answer_question(self, document_id, question):
        """Search vectors and produce LLM answer with citations"""
        query_embedding = self._embed_query(question)
        results = self.vector_store_service.search(document_id, query_embedding, top_k=Config.RAG_TOP_K)
        if not results:
            return {"answer": "No relevant context found.", "citations": []}

        chunk_ids = [r["chunk_id"] for r in results]
        chunks = Chunk.query.filter(Chunk.id.in_(chunk_ids)).all()

        context_chunks = []
        for res in results:
            chunk = next((c for c in chunks if c.id == res["chunk_id"]), None)
            if chunk:
                context_chunks.append({
                    "chunk_id": chunk.id,
                    "page": chunk.page_number or chunk.slide_number,
                    "text": chunk.chunk_text
                })

        return self.llm_client.rag_answer(question, context_chunks)

