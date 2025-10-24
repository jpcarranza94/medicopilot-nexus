#!/usr/bin/env python3
"""
RAG Pipeline orchestrator for document ingestion and retrieval.
"""

import logging
from typing import List, Dict, Optional
from .ingest import DocumentProcessor
from .embeddings import SaptivaEmbeddingService
from .vectorstore import WeaviateVectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrate document ingestion and retrieval for RAG."""

    def __init__(
        self,
        embedding_service: SaptivaEmbeddingService,
        vector_store: WeaviateVectorStore,
        chunk_size: int = 800,
        chunk_overlap: int = 80
    ):
        """
        Initialize RAG pipeline.

        Args:
            embedding_service: Service for generating embeddings
            vector_store: Vector database for storing chunks
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.doc_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def ingest_document(self, file_path: str, namespace: str) -> int:
        """
        Ingest a single document into the vector store.

        Args:
            file_path: Path to the document file
            namespace: Document namespace (gpc, cofepris, plm)

        Returns:
            Number of chunks ingested
        """
        logger.info(f"Starting ingestion: {file_path} (namespace: {namespace})")

        try:
            # Step 1: Extract and chunk document
            logger.info("Step 1/3: Processing document...")
            chunks = self.doc_processor.process_document(file_path, namespace)

            if not chunks:
                logger.warning(f"No chunks extracted from {file_path}")
                return 0

            logger.info(f"Extracted {len(chunks)} chunks")

            # Step 2: Generate embeddings
            logger.info("Step 2/3: Generating embeddings...")
            embeddings = []

            for i, chunk in enumerate(chunks):
                if (i + 1) % 10 == 0:
                    logger.info(f"Generating embedding {i + 1}/{len(chunks)}")

                embedding = self.embedding_service.generate_embedding(chunk["text"])
                embeddings.append(embedding)

            logger.info(f"Generated {len(embeddings)} embeddings")

            # Step 3: Store in Weaviate
            logger.info("Step 3/3: Storing in vector database...")
            self.vector_store.insert_chunks(chunks, embeddings)

            logger.info(f"✅ Successfully ingested {len(chunks)} chunks from {file_path}")
            return len(chunks)

        except Exception as e:
            logger.error(f"❌ Error ingesting document {file_path}: {e}")
            raise

    def ingest_directory(self, directory_path: str, namespace: str, file_pattern: str = "*.pdf") -> int:
        """
        Ingest all documents from a directory.

        Args:
            directory_path: Path to directory containing documents
            namespace: Document namespace
            file_pattern: File pattern to match (default: *.pdf)

        Returns:
            Total number of chunks ingested
        """
        import os
        import glob

        logger.info(f"Ingesting documents from {directory_path}")

        pattern = os.path.join(directory_path, file_pattern)
        files = glob.glob(pattern)

        if not files:
            logger.warning(f"No files matching {pattern}")
            return 0

        logger.info(f"Found {len(files)} files to ingest")

        total_chunks = 0

        for i, file_path in enumerate(files, start=1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing file {i}/{len(files)}: {os.path.basename(file_path)}")
            logger.info(f"{'='*60}")

            try:
                num_chunks = self.ingest_document(file_path, namespace)
                total_chunks += num_chunks
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                continue

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Ingestion complete!")
        logger.info(f"Total files processed: {len(files)}")
        logger.info(f"Total chunks ingested: {total_chunks}")
        logger.info(f"{'='*60}\n")

        return total_chunks

    def search(
        self,
        query: str,
        top_k: int = 3,
        namespace_filter: Optional[str] = None,
        source_type_filter: Optional[str] = None,
        min_certainty: float = 0.7
    ) -> List[Dict]:
        """
        Search for relevant document chunks.

        Args:
            query: Search query text
            top_k: Number of results to return
            namespace_filter: Filter by namespace (gpc, cofepris, plm)
            source_type_filter: Filter by source type
            min_certainty: Minimum similarity threshold

        Returns:
            List of matching chunks with metadata
        """
        logger.info(f"Searching for: '{query}' (top_k={top_k}, namespace={namespace_filter})")

        try:
            # Generate query embedding
            query_vector = self.embedding_service.generate_embedding(query)

            # Search vector store
            results = self.vector_store.search(
                query_vector=query_vector,
                limit=top_k,
                namespace_filter=namespace_filter,
                source_type_filter=source_type_filter,
                min_certainty=min_certainty
            )

            # Results are already in the correct format from v4 API
            logger.info(f"Found {len(results)} matching chunks")

            return results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise

    def format_context_for_prompt(self, chunks: List[Dict], max_chunks: int = 3) -> str:
        """
        Format retrieved chunks into context string for LLM prompt.

        Args:
            chunks: List of chunk dictionaries from search
            max_chunks: Maximum number of chunks to include

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."

        context_parts = []

        for i, chunk in enumerate(chunks[:max_chunks], start=1):
            source = chunk.get("document_name", "Unknown")
            section = chunk.get("section")
            evidence_level = chunk.get("evidence_level")
            text = chunk.get("text", "")

            # Build source citation
            citation = f"[Fuente {i}] {source}"

            if section:
                citation += f", Sección: {section}"

            if evidence_level:
                citation += f", Nivel de evidencia: {evidence_level}"

            # Add chunk
            context_parts.append(f"{citation}\n{text}\n")

        return "\n".join(context_parts)

    def get_stats(self) -> Dict:
        """Get pipeline statistics."""
        return self.vector_store.get_stats()

    def clear_namespace(self, namespace: str):
        """
        Clear all chunks from a namespace.

        Args:
            namespace: Namespace to clear
        """
        logger.warning(f"Clearing namespace: {namespace}")
        self.vector_store.delete_by_namespace(namespace)
