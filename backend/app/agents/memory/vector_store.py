"""
Vector Memory Store - ChromaDB + pgvector
Long-term semantic memory for all agents.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import FakeEmbeddings
from app.config import settings
from typing import Any
import logging

logger = logging.getLogger(__name__)


class VectorMemoryStore:
    """Semantic vector memory using ChromaDB for agent long-term memory."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.collection_name = f"agent_memory_{agent_id}"
        self._client = None
        self._collection = None

    def _get_client(self):
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._get_or_create_collection()
        return self._client

    def _get_or_create_collection(self):
        return self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"agent_id": self.agent_id},
        )

    async def store(self, content: str, metadata: dict = None) -> str:
        """Store a memory entry in the vector store."""
        try:
            client = self._get_client()
            import uuid
            doc_id = str(uuid.uuid4())
            self._collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[doc_id],
            )
            return doc_id
        except Exception as e:
            logger.warning(f"Vector memory store failed: {e}")
            return ""

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Semantic search over agent memory."""
        try:
            client = self._get_client()
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
            )
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            return [
                {"content": doc, "metadata": meta}
                for doc, meta in zip(documents, metadatas)
            ]
        except Exception as e:
            logger.warning(f"Vector memory search failed: {e}")
            return []

    async def clear(self):
        """Clear all memories for this agent."""
        try:
            client = self._get_client()
            self._client.delete_collection(self.collection_name)
        except Exception as e:
            logger.warning(f"Vector memory clear failed: {e}")
