"""
RAG Pipeline - Orchestrates embeddings and vector search
"""
from typing import List, Dict, Optional
from app.rag.embeddings import embedding_service
from app.rag.vectorstore import vector_store


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline
    Combines embedding generation with vector search
    """

    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def search(
        self,
        query: str,
        top_k: int = 3,
        namespace_filter: Optional[str] = None,
        source_type_filter: Optional[str] = None,
        min_certainty: float = 0.7
    ) -> List[Dict]:
        """
        Search for relevant documents using semantic search

        Args:
            query: Search query text
            top_k: Number of results to return
            namespace_filter: Filter by namespace (e.g., "gpc" for clinical guidelines)
            source_type_filter: Filter by source type
            min_certainty: Minimum similarity threshold

        Returns:
            List of relevant document chunks with metadata
        """
        # Generate embedding for query
        query_vector = await self.embedding_service.generate_embedding(query)

        # Search vector store
        results = await self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            namespace_filter=namespace_filter,
            source_type_filter=source_type_filter,
            min_certainty=min_certainty
        )

        return results

    def format_context_for_prompt(self, results: List[Dict]) -> str:
        """
        Format search results as context for LLM prompt

        Args:
            results: List of search results from vector store

        Returns:
            Formatted context string with citations
        """
        if not results:
            return "No se encontró evidencia relevante en las guías clínicas."

        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            source_name = metadata.get("sourceName", "Fuente desconocida")
            section = metadata.get("section", "")
            evidence_level = metadata.get("evidenceLevel", "")

            # Build citation header
            citation = f"[{i}. {source_name}"
            if section:
                citation += f" - {section}"
            if evidence_level:
                citation += f" (Nivel de evidencia: {evidence_level})"
            citation += "]"

            # Add text content
            text = result.get("text", "")
            context_parts.append(f"{citation}\n{text}")

        return "\n\n".join(context_parts)

    def format_citations(self, results: List[Dict]) -> List[Dict]:
        """
        Format citations for API response

        Args:
            results: List of search results

        Returns:
            List of formatted citations
        """
        citations = []
        for result in results:
            metadata = result.get("metadata", {})
            citations.append({
                "source": metadata.get("sourceName", ""),
                "namespace": metadata.get("sourceNamespace", ""),
                "section": metadata.get("section"),
                "evidence_level": metadata.get("evidenceLevel"),
                "page": metadata.get("pageNumber"),
                "certainty": result.get("certainty")
            })
        return citations

    def is_ready(self) -> bool:
        """Check if RAG pipeline is ready"""
        return self.vector_store.is_ready()

    def get_stats(self) -> Dict:
        """Get pipeline statistics"""
        return self.vector_store.get_stats()


# Singleton instance
rag_pipeline = RAGPipeline()
