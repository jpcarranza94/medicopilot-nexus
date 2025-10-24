#!/usr/bin/env python3
"""
Test script for RAG pipeline.

Tests the complete RAG flow: ingestion and search.
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from rag.embeddings import SaptivaEmbeddingService, MockEmbeddingService
from rag.vectorstore import WeaviateVectorStore
from rag.pipeline import RAGPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_search(pipeline: RAGPipeline):
    """Test search functionality."""
    print("\n" + "="*60)
    print("TESTING SEARCH FUNCTIONALITY")
    print("="*60 + "\n")

    test_queries = [
        {
            "query": "tratamiento para diabetes tipo 2",
            "namespace": "gpc",
            "description": "Treatment for type 2 diabetes"
        },
        {
            "query": "hipertensión arterial diagnóstico",
            "namespace": "gpc",
            "description": "Hypertension diagnosis"
        },
        {
            "query": "azitromicina presentaciones",
            "namespace": "cofepris",
            "description": "Azithromycin presentations"
        },
        {
            "query": "medicamentos para infección urinaria",
            "namespace": None,
            "description": "Medications for UTI (search all)"
        },
    ]

    for i, test in enumerate(test_queries, start=1):
        print(f"\n{'─'*60}")
        print(f"Test Query {i}: {test['description']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Namespace: {test['namespace'] or 'all'}")
        print(f"{'─'*60}\n")

        try:
            results = pipeline.search(
                query=test['query'],
                top_k=3,
                namespace_filter=test['namespace']
            )

            if not results:
                print("❌ No results found")
                continue

            print(f"✅ Found {len(results)} results:\n")

            for j, chunk in enumerate(results, start=1):
                print(f"[Result {j}]")
                print(f"  Document: {chunk.get('document_name', 'Unknown')}")
                print(f"  Namespace: {chunk.get('namespace', 'Unknown')}")
                print(f"  Page: {chunk.get('page_number', 'N/A')}")

                if chunk.get('section'):
                    print(f"  Section: {chunk.get('section')}")

                if chunk.get('evidence_level'):
                    print(f"  Evidence Level: {chunk.get('evidence_level')}")

                if chunk.get('generic_name'):
                    print(f"  Generic Name: {chunk.get('generic_name')}")

                text = chunk.get('text', '')
                preview = text[:200] + "..." if len(text) > 200 else text
                print(f"  Text Preview: {preview}")
                print()

        except Exception as e:
            print(f"❌ Search failed: {e}\n")

    # Test formatted context
    print(f"\n{'─'*60}")
    print("Testing Context Formatting")
    print(f"{'─'*60}\n")

    try:
        results = pipeline.search("diabetes tratamiento", top_k=2, namespace_filter="gpc")
        context = pipeline.format_context_for_prompt(results)

        print("Formatted Context for LLM Prompt:")
        print("-" * 40)
        print(context)
        print("-" * 40)

    except Exception as e:
        print(f"❌ Context formatting failed: {e}")


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("RAG PIPELINE TEST SUITE")
    print("="*60)

    # Load environment variables
    load_dotenv()

    use_mock = not os.getenv("SAPTIVA_API_KEY")

    if use_mock:
        logger.warning("No SAPTIVA_API_KEY found, using mock embeddings")

    try:
        # Initialize services
        print("\n1. Initializing services...")

        if use_mock:
            embedding_service = MockEmbeddingService()
        else:
            embedding_service = SaptivaEmbeddingService(
                api_key=os.getenv("SAPTIVA_API_KEY")
            )

        vector_store = WeaviateVectorStore(
            url=os.getenv("WEAVIATE_HOST"),
            api_key=os.getenv("WEAVIATE_API_KEY")
        )

        pipeline = RAGPipeline(
            embedding_service=embedding_service,
            vector_store=vector_store
        )

        print("✅ Services initialized\n")

        # Get stats
        print("2. Getting database statistics...")
        stats = pipeline.get_stats()
        print(f"   Total chunks in database: {stats.get('total_chunks', 0)}")

        if stats.get('total_chunks', 0) == 0:
            print("\n⚠️  No documents in database!")
            print("   Run ingestion first: python scripts/ingest_documents.py --mode all")
            return

        # Run search tests
        test_search(pipeline)

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
