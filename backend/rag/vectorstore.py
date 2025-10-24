#!/usr/bin/env python3
"""
Weaviate vector store integration for document chunks (v4 API).
"""

import logging
from typing import List, Dict, Optional

try:
    import weaviate
    import weaviate.classes as wvc
    from weaviate.classes.config import Property, DataType, Configure
except ImportError:
    weaviate = None
    logging.warning("weaviate-client not installed. Install with: pip install weaviate-client")

logger = logging.getLogger(__name__)


class WeaviateVectorStore:
    """Weaviate vector database client for storing and retrieving document chunks."""

    def __init__(self, url: str, api_key: str, collection_name: str = "DocumentChunk"):
        """
        Initialize Weaviate client.

        Args:
            url: Weaviate cluster URL
            api_key: Weaviate API key
            collection_name: Name of the collection to use
        """
        if not weaviate:
            raise ImportError("weaviate-client package is required. Install with: pip install weaviate-client")

        self.collection_name = collection_name

        try:
            # Initialize Weaviate client (v4 API)
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=url,
                auth_credentials=weaviate.auth.AuthApiKey(api_key),
                skip_init_checks=False
            )

            # Test connection
            if self.client.is_ready():
                logger.info(f"Connected to Weaviate at {url}")
            else:
                raise ConnectionError("Weaviate cluster is not ready")

            # Ensure collection exists
            self.ensure_collection_exists()

        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    def ensure_collection_exists(self):
        """Create DocumentChunk collection schema if it doesn't exist."""
        try:
            # Check if collection already exists
            if self.client.collections.exists(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            # Create collection with schema
            self.client.collections.create(
                name=self.collection_name,
                description="Medical document chunks for RAG",
                vectorizer_config=Configure.Vectorizer.none(),  # We provide our own vectors
                properties=[
                    Property(name="text", data_type=DataType.TEXT, description="Chunk text content"),
                    Property(name="source_type", data_type=DataType.TEXT, description="Document source type (gpc, cofepris, plm)"),
                    Property(name="document_name", data_type=DataType.TEXT, description="Source document filename"),
                    Property(name="page_number", data_type=DataType.INT, description="Page number in source document"),
                    Property(name="namespace", data_type=DataType.TEXT, description="Document namespace for filtering"),
                    Property(name="section", data_type=DataType.TEXT, description="Section name (for GPC documents)"),
                    Property(name="evidence_level", data_type=DataType.TEXT, description="Evidence level rating (A, B, C, D)"),
                    Property(name="generic_name", data_type=DataType.TEXT, description="Generic drug name (for COFEPRIS)"),
                    Property(name="brand_name", data_type=DataType.TEXT, description="Brand/trade name (for COFEPRIS)"),
                    Property(name="manufacturer", data_type=DataType.TEXT, description="Manufacturer name (for COFEPRIS)"),
                ]
            )
            logger.info(f"Created collection '{self.collection_name}'")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def insert_chunks(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Batch insert chunks with their embeddings.

        Args:
            chunks: List of chunk dictionaries with text and metadata
            embeddings: List of embedding vectors (same length as chunks)
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks and embeddings must have same length: {len(chunks)} vs {len(embeddings)}")

        try:
            collection = self.client.collections.get(self.collection_name)

            # Insert in batches
            with collection.batch.dynamic() as batch:
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    # Prepare data object
                    properties = {
                        "text": chunk.get("text", ""),
                        "source_type": chunk.get("source_type"),
                        "document_name": chunk.get("document_name"),
                        "page_number": chunk.get("page_number"),
                        "namespace": chunk.get("namespace"),
                        "section": chunk.get("section"),
                        "evidence_level": chunk.get("evidence_level"),
                        "generic_name": chunk.get("generic_name"),
                        "brand_name": chunk.get("brand_name"),
                        "manufacturer": chunk.get("manufacturer"),
                    }

                    # Add to batch
                    batch.add_object(
                        properties=properties,
                        vector=embedding
                    )

                    if (i + 1) % 50 == 0:
                        logger.info(f"Inserted {i + 1}/{len(chunks)} chunks")

            logger.info(f"Successfully inserted {len(chunks)} chunks")

        except Exception as e:
            logger.error(f"Error inserting chunks: {e}")
            raise

    def search(
        self,
        query_vector: List[float],
        limit: int = 3,
        namespace_filter: Optional[str] = None,
        source_type_filter: Optional[str] = None,
        min_certainty: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            namespace_filter: Filter by namespace (e.g., "gpc", "cofepris")
            source_type_filter: Filter by source type
            min_certainty: Minimum similarity threshold (0-1)

        Returns:
            Search results with chunks and metadata
        """
        try:
            collection = self.client.collections.get(self.collection_name)

            # Build filter
            filters = None
            if namespace_filter and source_type_filter:
                filters = wvc.query.Filter.all_of([
                    wvc.query.Filter.by_property("namespace").equal(namespace_filter),
                    wvc.query.Filter.by_property("source_type").equal(source_type_filter)
                ])
            elif namespace_filter:
                filters = wvc.query.Filter.by_property("namespace").equal(namespace_filter)
            elif source_type_filter:
                filters = wvc.query.Filter.by_property("source_type").equal(source_type_filter)

            # Execute search
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                filters=filters,
                return_metadata=wvc.query.MetadataQuery(certainty=True)
            )

            # Convert results to dict format
            results = []
            for obj in response.objects:
                result = {
                    **obj.properties,
                    "_certainty": obj.metadata.certainty if obj.metadata else None
                }
                results.append(result)

            logger.debug(f"Search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise

    def delete_by_namespace(self, namespace: str):
        """
        Delete all chunks from a specific namespace.

        Args:
            namespace: Namespace to delete
        """
        try:
            collection = self.client.collections.get(self.collection_name)

            result = collection.data.delete_many(
                where=wvc.query.Filter.by_property("namespace").equal(namespace)
            )

            logger.info(f"Deleted {result.successful} chunks from namespace '{namespace}'")
            return result

        except Exception as e:
            logger.error(f"Error deleting namespace: {e}")
            raise

    def get_stats(self) -> Dict:
        """
        Get statistics about stored chunks.

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.client.collections.get(self.collection_name)
            aggregate = collection.aggregate.over_all(total_count=True)

            stats = {
                "total_chunks": aggregate.total_count
            }

            logger.info(f"Vector store stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_chunks": 0, "error": str(e)}

    def close(self):
        """Close Weaviate client connection."""
        if self.client:
            self.client.close()
            logger.info("Weaviate client closed")
