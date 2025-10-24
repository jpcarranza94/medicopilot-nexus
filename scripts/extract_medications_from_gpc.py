#!/usr/bin/env python3
"""
Extract medications mentioned in GPC documents from Weaviate and create PLM data.
"""

import os
import json
import re
from dotenv import load_dotenv
from rag.embeddings import SaptivaEmbeddingService
from rag.vectorstore import WeaviateVectorStore
from rag.pipeline import RAGPipeline

load_dotenv()

# Initialize services
embedding_service = SaptivaEmbeddingService(
    api_key=os.getenv('SAPTIVA_API_KEY'),
    api_url=os.getenv('SAPTIVA_API_URL', 'https://api.saptiva.com/api/embed'),
    model=os.getenv('SAPTIVA_EMBED_MODEL', 'Saptiva Embed')
)

vector_store = WeaviateVectorStore(
    url=os.getenv('WEAVIATE_URL'),
    api_key=os.getenv('WEAVIATE_API_KEY')
)

pipeline = RAGPipeline(
    embedding_service=embedding_service,
    vector_store=vector_store
)

# Search queries for different conditions
queries = [
    "medicamentos para diabetes tratamiento metformina insulina",
    "medicamentos para hipertension arterial antihipertensivos",
    "medicamentos para dislipidemia estatinas",
    "medicamentos para hipotiroidismo levotiroxina",
    "antibioticos para neumonia",
    "analgésicos para cefalea dolor de cabeza",
    "tratamiento obesidad"
]

print("Searching GPC documents for medication mentions...\n")

all_medications = set()
medication_contexts = {}

for query in queries:
    print(f"Query: {query}")
    results = pipeline.search(
        query=query,
        top_k=5,
        namespace_filter="gpc"
    )

    print(f"Found {len(results)} results\n")

    for result in results:
        text = result.get('text', '')
        doc_name = result.get('document_name', '')

        # Extract medication names (simple pattern matching)
        # Look for common medication patterns in Spanish medical text
        patterns = [
            r'\b(metformina|glibenclamida|insulina|sitagliptina|pioglitazona)\b',
            r'\b(losartan|enalapril|captopril|amlodipino|hidroclorotiazida|atenolol|metoprolol)\b',
            r'\b(atorvastatina|simvastatina|rosuvastatina|pravastatina)\b',
            r'\b(levotiroxina)\b',
            r'\b(amoxicilina|azitromicina|levofloxacino|ceftriaxona|claritromicina)\b',
            r'\b(paracetamol|ibuprofeno|naproxeno|ketorolaco|metamizol)\b',
            r'\b(orlistat)\b',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for med in matches:
                all_medications.add(med.capitalize())
                if med.capitalize() not in medication_contexts:
                    medication_contexts[med.capitalize()] = []
                medication_contexts[med.capitalize()].append({
                    'document': doc_name,
                    'context': text[:200] + '...'
                })

    print(f"Medications found so far: {len(all_medications)}\n")

print("\n" + "="*60)
print("MEDICATIONS FOUND IN GPC DOCUMENTS:")
print("="*60)
for med in sorted(all_medications):
    docs = set([ctx['document'] for ctx in medication_contexts[med]])
    print(f"- {med} (mentioned in: {', '.join(sorted(docs))})")

print(f"\nTotal unique medications: {len(all_medications)}")

# Save to JSON
output = {
    'medications': sorted(list(all_medications)),
    'contexts': medication_contexts
}

with open('backend/data/gpc_medications_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n✅ Saved to: backend/data/gpc_medications_extracted.json")
