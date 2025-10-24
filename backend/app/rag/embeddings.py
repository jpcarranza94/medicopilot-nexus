"""
Saptiva Embeddings Service for RAG
"""
import httpx
from typing import List
from app.config.settings import settings


class SaptivaEmbeddingService:
    """Service for generating embeddings using Saptiva API"""

    def __init__(self):
        self.api_key = settings.SAPTIVA_API_KEY
        self.api_url = "https://api.saptiva.com/api/embed/"  # Trailing slash for redirect
        self.model = "Saptiva Embed"
        self.timeout = 30.0

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Saptiva Embed model

        Args:
            text: Text to embed

        Returns:
            1024-dimensional embedding vector

        Raises:
            httpx.HTTPError: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": text,  # Saptiva embed API expects "prompt" field
            "model": self.model
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            # Saptiva returns embedding in "embeddings" field (plural)
            embedding = data.get("embeddings") or data.get("embedding") or data.get("vector", [])

            if not embedding:
                raise ValueError(f"No embedding found in response: {data}")

            return embedding

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings


# Singleton instance
embedding_service = SaptivaEmbeddingService()
