"""
Test RAG results for diabetes demo patient
"""
import asyncio
from app.rag.pipeline import rag_pipeline


async def test_diabetes_plan_query():
    """Test what RAG returns for diabetes treatment plan"""
    print("=" * 80)
    print("TEST 1: Clinical Plan Query - Diabetes Treatment")
    print("=" * 80)

    # Simulate the query that would be generated from SOAP
    subjective = "Paciente femenina de 52 años con cuadro de 3 meses de polidipsia, poliuria y pérdida de peso no intencionada de 5 kg"
    objective = "TA: 130/85 mmHg, FC: 78 lpm, Peso: 82 kg, IMC: 32.0, Glucosa en ayuno: 185 mg/dL, HbA1c: 8.5%"

    query = f"{subjective} {objective}"
    print(f"\nQuery: {query[:150]}...")
    print()

    try:
        results = await rag_pipeline.search(
            query=query,
            top_k=5,  # Get top 5 for diabetes
            namespace_filter="gpc",
            min_certainty=0.65  # Lower threshold to see more results
        )

        print(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            certainty = result.get("certainty", 0)
            text = result.get("text", "")

            print(f"[Result {i}] Certainty: {certainty:.3f}")
            print(f"Source: {metadata.get('sourceName', 'Unknown')}")
            print(f"Section: {metadata.get('section', 'N/A')}")
            print(f"Evidence Level: {metadata.get('evidenceLevel', 'N/A')}")
            print(f"Text preview: {text[:300]}...")
            print()

        # Show formatted context
        print("=" * 80)
        print("FORMATTED CONTEXT FOR LLM PROMPT:")
        print("=" * 80)
        context = rag_pipeline.format_context_for_prompt(results)
        print(context[:1000] + "..." if len(context) > 1000 else context)

        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


async def test_diabetes_hpi_query():
    """Test what RAG returns for HPI suggestions"""
    print("\n" + "=" * 80)
    print("TEST 2: HPI Query - Diabetes Symptoms")
    print("=" * 80)

    query = "polidipsia poliuria pérdida de peso diabetes síntomas"
    print(f"\nQuery: {query}")
    print()

    try:
        results = await rag_pipeline.search(
            query=query,
            top_k=3,
            namespace_filter="gpc",
            min_certainty=0.65
        )

        print(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            certainty = result.get("certainty", 0)
            text = result.get("text", "")

            print(f"[Result {i}] Certainty: {certainty:.3f}")
            print(f"Source: {metadata.get('sourceName', 'Unknown')}")
            print(f"Text: {text[:400]}...")
            print()

        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


async def test_metformin_query():
    """Test what RAG returns for metformin medication"""
    print("\n" + "=" * 80)
    print("TEST 3: Medication Query - Metformin")
    print("=" * 80)

    query = "metformina tratamiento diabetes primera línea dosis"
    print(f"\nQuery: {query}")
    print()

    try:
        results = await rag_pipeline.search(
            query=query,
            top_k=3,
            namespace_filter="gpc",
            min_certainty=0.65
        )

        print(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            certainty = result.get("certainty", 0)
            text = result.get("text", "")

            print(f"[Result {i}] Certainty: {certainty:.3f}")
            print(f"Source: {metadata.get('sourceName', 'Unknown')}")
            print(f"Text: {text[:400]}...")
            print()

        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


async def test_diabetes_complications_query():
    """Test what RAG returns for diabetes complications"""
    print("\n" + "=" * 80)
    print("TEST 4: Complications Query - Diabetes Monitoring")
    print("=" * 80)

    query = "diabetes complicaciones crónicas monitoreo HbA1c metas control glucémico"
    print(f"\nQuery: {query}")
    print()

    try:
        results = await rag_pipeline.search(
            query=query,
            top_k=3,
            namespace_filter="gpc",
            min_certainty=0.65
        )

        print(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            certainty = result.get("certainty", 0)
            text = result.get("text", "")

            print(f"[Result {i}] Certainty: {certainty:.3f}")
            print(f"Source: {metadata.get('sourceName', 'Unknown')}")
            print(f"Text: {text[:400]}...")
            print()

        return results
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


async def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DIABETES DEMO PATIENT - RAG TEST" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Test if Weaviate is ready
    if not rag_pipeline.is_ready():
        print("❌ Weaviate is not ready. Check connection.")
        return

    stats = rag_pipeline.get_stats()
    print(f"✅ Weaviate ready - {stats.get('total_chunks', 0)} chunks loaded\n")

    # Run all tests
    results1 = await test_diabetes_plan_query()
    results2 = await test_diabetes_hpi_query()
    results3 = await test_metformin_query()
    results4 = await test_diabetes_complications_query()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Clinical Plan): {len(results1)} results")
    print(f"Test 2 (HPI Symptoms): {len(results2)} results")
    print(f"Test 3 (Metformin): {len(results3)} results")
    print(f"Test 4 (Complications): {len(results4)} results")

    total_results = len(results1) + len(results2) + len(results3) + len(results4)

    if total_results > 0:
        print(f"\n✅ RAG is returning {total_results} total results for diabetes queries")
        print("\nNOTE: Check if results are actually from diabetes GPC or from other sources.")
        print("      You may need to review the actual document chunks in Weaviate.")
    else:
        print("\n⚠️  No results found. The diabetes GPC may not be loaded in Weaviate.")
        print("     Or the query embeddings are not matching the document content.")


if __name__ == "__main__":
    asyncio.run(main())
