#!/usr/bin/env python3
"""Test Weaviate connection"""

import os
from dotenv import load_dotenv
import weaviate

load_dotenv()

url = os.getenv('WEAVIATE_URL')
api_key = os.getenv('WEAVIATE_API_KEY')

print(f"Attempting to connect to: {url}")
print(f"API Key (first 20 chars): {api_key[:20]}...")

try:
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=url,
        auth_credentials=weaviate.auth.AuthApiKey(api_key),
        skip_init_checks=True  # Skip initial checks
    )

    print("✓ Client created")

    if client.is_ready():
        print("✓ Weaviate is ready!")

        # Try to list collections
        collections = list(client.collections.list_all())
        print(f"✓ Found {len(collections)} collections")
        for coll in collections:
            print(f"  - {coll}")
    else:
        print("✗ Weaviate is not ready")

    client.close()
    print("✓ Connection closed")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
