"""
Weaviate Vector Store for RAG
"""
import weaviate
import weaviate.classes as wvc
from typing import List, Dict, Optional
from app.config.settings import settings


class WeaviateVectorStore:
    """Client for interacting with Weaviate vector database"""

    def __init__(self):
        self.url = settings.WEAVIATE_URL
        self.api_key = settings.WEAVIATE_API_KEY
        self.collection_name = "DocumentChunk"
        self._client = None

    def connect(self):
        """Establish connection to Weaviate Cloud"""
        if self._client is None:
            self._client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.url,
                auth_credentials=weaviate.auth.AuthApiKey(self.api_key)
            )
        return self._client

    def disconnect(self):
        """Close connection to Weaviate"""
        if self._client:
            self._client.close()
            self._client = None

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 3,
        namespace_filter: Optional[str] = None,
        source_type_filter: Optional[str] = None,
        min_certainty: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar documents using vector similarity

        Args:
            query_vector: Embedding vector for the query
            top_k: Number of results to return
            namespace_filter: Filter by namespace (e.g., "gpc", "cofepris")
            source_type_filter: Filter by source type
            min_certainty: Minimum similarity threshold (0-1)

        Returns:
            List of matching document chunks with metadata
        """
        try:
            client = self.connect()
            collection = client.collections.get(self.collection_name)

            # Build filters
            filters = []
            if namespace_filter:
                filters.append(
                    wvc.query.Filter.by_property("namespace").equal(namespace_filter)
                )
            if source_type_filter:
                filters.append(
                    wvc.query.Filter.by_property("source_type").equal(source_type_filter)
                )

            # Combine filters with AND
            combined_filter = None
            if len(filters) == 1:
                combined_filter = filters[0]
            elif len(filters) > 1:
                combined_filter = wvc.query.Filter.all_of(filters)

            # Execute search
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=top_k,
                filters=combined_filter,
                return_metadata=wvc.query.MetadataQuery(certainty=True)
            )

            # Format results
            results = []
            for obj in response.objects:
                # Only include results above certainty threshold
                if obj.metadata.certainty and obj.metadata.certainty >= min_certainty:
                    results.append({
                        "text": obj.properties.get("text", ""),
                        "metadata": {
                            "sourceName": obj.properties.get("document_name", ""),
                            "sourceType": obj.properties.get("source_type", ""),
                            "sourceNamespace": obj.properties.get("namespace", ""),
                            "pageNumber": obj.properties.get("page_number"),
                            "section": obj.properties.get("section"),
                            "evidenceLevel": obj.properties.get("evidence_level"),
                            "chunkIndex": 0,  # Not stored in current schema
                        },
                        "certainty": obj.metadata.certainty
                    })

            return results

        except Exception as e:
            print(f"Error searching Weaviate: {e}")
            return []

    def is_ready(self) -> bool:
        """Check if Weaviate connection is ready"""
        try:
            client = self.connect()
            return client.is_ready()
        except Exception:
            return False

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            client = self.connect()
            collection = client.collections.get(self.collection_name)
            aggregate = collection.aggregate.over_all(total_count=True)

            return {
                "total_chunks": aggregate.total_count,
                "collection": self.collection_name,
                "ready": self.is_ready()
            }
        except Exception as e:
            return {
                "error": str(e),
                "ready": False
            }


# Singleton instance
vector_store = WeaviateVectorStore()
