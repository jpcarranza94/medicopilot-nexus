#!/usr/bin/env python3
"""Clear COFEPRIS namespace from Weaviate before re-uploading."""

import os
from dotenv import load_dotenv
from rag.vectorstore import WeaviateVectorStore

load_dotenv()

vector_store = WeaviateVectorStore(
    url=os.getenv('WEAVIATE_URL'),
    api_key=os.getenv('WEAVIATE_API_KEY')
)

print("Current stats before clearing:")
stats = vector_store.get_stats()
print(f"  Total chunks: {stats['total_chunks']}")

print("\nClearing COFEPRIS namespace...")
vector_store.delete_by_namespace("cofepris")

print("\nStats after clearing:")
stats = vector_store.get_stats()
print(f"  Total chunks: {stats['total_chunks']}")

vector_store.close()
print("\n✅ Done!")
