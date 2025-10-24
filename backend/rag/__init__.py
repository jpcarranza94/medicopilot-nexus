"""
RAG (Retrieval-Augmented Generation) module for MediCopilot.

This module provides document processing, embedding generation,
and vector storage capabilities for clinical documents.
"""

from .ingest import DocumentProcessor
from .embeddings import SaptivaEmbeddingService
from .vectorstore import WeaviateVectorStore
from .pipeline import RAGPipeline

__all__ = [
    "DocumentProcessor",
    "SaptivaEmbeddingService",
    "WeaviateVectorStore",
    "RAGPipeline",
]
