"""
Test script for RAG integration
"""
import asyncio
from app.rag.pipeline import rag_pipeline


async def test_weaviate_connection():
    """Test Weaviate connection"""
    print("=== Testing Weaviate Connection ===")

    is_ready = rag_pipeline.is_ready()
    print(f"Weaviate ready: {is_ready}")

    if is_ready:
        stats = rag_pipeline.get_stats()
        print(f"Total chunks in database: {stats.get('total_chunks', 'N/A')}")
        print(f"Collection: {stats.get('collection', 'N/A')}")
    else:
        print("❌ Weaviate is not ready. Check connection settings.")
        return False

    print("✅ Weaviate connection successful\n")
    return True


async def test_rag_search():
    """Test RAG search functionality"""
    print("=== Testing RAG Search ===")

    # Test query for pharyngitis (we know this should have results)
    query = "dolor de garganta fiebre exudado amigdalino"
    print(f"Query: {query}")

    try:
        results = await rag_pipeline.search(
            query=query,
            top_k=3,
            namespace_filter="gpc",
            min_certainty=0.6
        )

        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            certainty = result.get("certainty", 0)
            text = result.get("text", "")[:200]  # First 200 chars

            print(f"\n[Result {i}]")
            print(f"Source: {metadata.get('sourceName', 'Unknown')}")
            print(f"Section: {metadata.get('section', 'N/A')}")
            print(f"Evidence Level: {metadata.get('evidenceLevel', 'N/A')}")
            print(f"Certainty: {certainty:.2f}")
            print(f"Text preview: {text}...")

        if results:
            print("\n✅ RAG search successful")

            # Test context formatting
            context = rag_pipeline.format_context_for_prompt(results)
            print("\n=== Formatted Context for Prompt ===")
            print(context[:500] + "..." if len(context) > 500 else context)

            return True
        else:
            print("\n⚠️  No results found. Database might be empty or query doesn't match content.")
            return False

    except Exception as e:
        print(f"\n❌ RAG search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("MediCopilot RAG Integration Test")
    print("=" * 60)
    print()

    # Test connection first
    connection_ok = await test_weaviate_connection()

    if connection_ok:
        # Test search
        search_ok = await test_rag_search()

        if search_ok:
            print("\n" + "=" * 60)
            print("✅ All RAG tests passed!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️  RAG search test had issues")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Weaviate connection failed")
        print("=" * 60)
        print("\nCheck your .env file:")
        print("- WEAVIATE_URL should be set")
        print("- WEAVIATE_API_KEY should be set")


if __name__ == "__main__":
    asyncio.run(main())
