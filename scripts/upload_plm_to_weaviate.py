#!/usr/bin/env python3
"""
Upload fake PLM medication data to Weaviate.
"""

import os
import json
from dotenv import load_dotenv
from rag.embeddings import SaptivaEmbeddingService
from rag.vectorstore import WeaviateVectorStore

load_dotenv()

# Initialize services
print("Initializing services...")
embedding_service = SaptivaEmbeddingService(
    api_key=os.getenv('SAPTIVA_API_KEY'),
    api_url=os.getenv('SAPTIVA_API_URL', 'https://api.saptiva.com/api/embed'),
    model=os.getenv('SAPTIVA_EMBED_MODEL', 'Saptiva Embed')
)

vector_store = WeaviateVectorStore(
    url=os.getenv('WEAVIATE_URL'),
    api_key=os.getenv('WEAVIATE_API_KEY')
)

# Load PLM data
print("Loading PLM medication data...")
with open('backend/data/plm_medications_fake.json', 'r', encoding='utf-8') as f:
    plm_data = json.load(f)

print(f"Loaded {len(plm_data)} medications")

# Convert to chunks
print("\nConverting to chunks...")
chunks = []
embeddings_to_generate = []

for i, med in enumerate(plm_data, 1):
    # Create a rich text description for embedding
    text = f"""
Medicamento: {med['generic_name']}
Marca Comercial: {med['brand_name']}
Fabricante: {med['manufacturer']}
Presentación: {med['presentation']} {med['concentration']}
Empaque: {med['package_size']}
Vía de administración: {med['administration_route']}
Clase terapéutica: {med['therapeutic_class']}

Indicaciones: {med['indications']}

Dosificación: {med['dosing']}

Contraindicaciones: {med['contraindications']}

Interacciones: {med['interactions']}

Categoría en embarazo: {med['pregnancy_category']}
Precio público: ${med['precio_publico']} MXN
Registro COFEPRIS: {med['registro_cofepris']}
    """.strip()

    chunk = {
        "text": text,
        "source_type": "plm",
        "document_name": f"PLM_{med['brand_name']}",
        "page_number": 1,
        "namespace": "plm",
        "section": None,
        "evidence_level": None,
        "generic_name": med['generic_name'],
        "brand_name": med['brand_name'],
        "manufacturer": med['manufacturer']
    }

    chunks.append(chunk)
    embeddings_to_generate.append(text)

    print(f"  [{i}/{len(plm_data)}] Prepared: {med['generic_name']} - {med['brand_name']}")

# Generate embeddings
print("\nGenerating embeddings...")
embeddings = []

for i, text in enumerate(embeddings_to_generate, 1):
    print(f"  [{i}/{len(embeddings_to_generate)}] Generating embedding...")
    embedding = embedding_service.generate_embedding(text)
    embeddings.append(embedding)

print(f"\n✅ Generated {len(embeddings)} embeddings")

# Upload to Weaviate
print("\nUploading to Weaviate...")
vector_store.insert_chunks(chunks, embeddings)

print(f"✅ Successfully uploaded {len(chunks)} PLM medications to Weaviate!")

# Get stats
stats = vector_store.get_stats()
print(f"\n{'='*60}")
print(f"Total chunks in Weaviate: {stats['total_chunks']}")
print(f"  - GPC: 324 chunks")
print(f"  - PLM: {len(chunks)} chunks")
print(f"  - COFEPRIS: (upload in progress)")
print(f"{'='*60}")

vector_store.close()
