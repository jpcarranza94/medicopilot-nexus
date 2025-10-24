#!/usr/bin/env python3
"""
Embedding generation service using Saptiva AI API.
"""

import time
import logging
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)


class SaptivaEmbeddingService:
    """Generate embeddings using Saptiva AI's embedding API."""

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.saptiva.com/api/embed",
        model: str = "Saptiva Embed",
        max_retries: int = 2,
        retry_delay: float = 1.0
    ):
        """
        Initialize SaptivaEmbeddingService.

        Args:
            api_key: Saptiva API key
            api_url: Saptiva API URL for embeddings
            model: Model name (default: "Saptiva Embed")
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries (seconds)
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Setup session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text.

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats

        Raises:
            Exception: If embedding generation fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Truncate very long texts (most embedding models have limits)
        max_length = 8000  # characters
        if len(text) > max_length:
            logger.warning(f"Text length {len(text)} exceeds {max_length}, truncating")
            text = text[:max_length]

        for attempt in range(self.max_retries + 1):
            try:
                # Make API request
                payload = {
                    "model": self.model,
                    "prompt": text
                }

                response = self.session.post(
                    self.api_url,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()

                # Parse response
                result = response.json()

                # Handle different response formats
                if isinstance(result, dict):
                    # Try common keys
                    embedding = (
                        result.get('embedding') or
                        result.get('embeddings') or
                        result.get('data', {}).get('embedding') or
                        result.get('vector')
                    )
                elif isinstance(result, list):
                    embedding = result
                else:
                    raise ValueError(f"Unexpected response format: {type(result)}")

                if not embedding:
                    raise ValueError(f"No embedding found in response: {result}")

                if not isinstance(embedding, list):
                    raise ValueError(f"Expected list, got {type(embedding)}")

                logger.debug(f"Generated embedding of dimension {len(embedding)}")
                return embedding

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    logger.warning(f"Embedding generation failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Embedding generation failed after {self.max_retries + 1} attempts: {e}")
                    raise
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Embedding generation failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Embedding generation failed after {self.max_retries + 1} attempts: {e}")
                    raise

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{(len(texts) - 1) // batch_size + 1}")

            for text in batch:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)

            # Small delay to avoid rate limiting
            if i + batch_size < len(texts):
                time.sleep(0.1)

        return embeddings


class MockEmbeddingService:
    """Mock embedding service for testing without API access."""

    def __init__(self, dimension: int = 1536):
        """
        Initialize mock service.

        Args:
            dimension: Embedding vector dimension
        """
        self.dimension = dimension
        logger.warning("Using MockEmbeddingService - not suitable for production!")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic mock embedding based on text hash."""
        import hashlib

        # Create deterministic embedding from text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Convert hash to numbers
        embedding = []
        for i in range(self.dimension):
            # Use different parts of the hash
            idx = (i * 2) % len(text_hash)
            val = int(text_hash[idx:idx+2], 16) / 255.0 - 0.5
            embedding.append(val)

        return embedding

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """Generate mock embeddings for multiple texts."""
        return [self.generate_embedding(text) for text in texts]
