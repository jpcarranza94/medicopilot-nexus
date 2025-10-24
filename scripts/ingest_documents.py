#!/usr/bin/env python3
"""
Document ingestion script for MediCopilot RAG pipeline.

Usage:
    python ingest_documents.py --file path/to/document.pdf --namespace gpc
    python ingest_documents.py --directory path/to/docs --namespace gpc
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.embeddings import SaptivaEmbeddingService
from rag.vectorstore import WeaviateVectorStore
from rag.pipeline import RAGPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion function."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Ingest documents into Weaviate vector store')

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', type=str, help='Path to a single PDF file')
    input_group.add_argument('--directory', type=str, help='Path to directory containing PDFs')

    # Required arguments
    parser.add_argument('--namespace', type=str, required=True,
                       choices=['gpc', 'cofepris', 'plm', 'nom'],
                       help='Document namespace (gpc, cofepris, plm, nom)')

    # Optional arguments
    parser.add_argument('--chunk-size', type=int, default=800,
                       help='Text chunk size in characters (default: 800)')
    parser.add_argument('--chunk-overlap', type=int, default=80,
                       help='Chunk overlap in characters (default: 80)')
    parser.add_argument('--clear-namespace', action='store_true',
                       help='Clear existing documents from namespace before ingestion')

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get API credentials
    saptiva_api_key = os.getenv('SAPTIVA_API_KEY')
    saptiva_api_url = os.getenv('SAPTIVA_API_URL', 'https://api.saptiva.com/api/embed')
    saptiva_model = os.getenv('SAPTIVA_EMBED_MODEL', 'Saptiva Embed')

    weaviate_url = os.getenv('WEAVIATE_URL')
    weaviate_api_key = os.getenv('WEAVIATE_API_KEY')

    # Validate credentials
    if not saptiva_api_key:
        logger.error("SAPTIVA_API_KEY not found in environment variables")
        sys.exit(1)

    if not weaviate_url or not weaviate_api_key:
        logger.error("WEAVIATE_URL and WEAVIATE_API_KEY must be set in environment variables")
        sys.exit(1)

    try:
        # Initialize services
        logger.info("Initializing embedding service...")
        embedding_service = SaptivaEmbeddingService(
            api_key=saptiva_api_key,
            api_url=saptiva_api_url,
            model=saptiva_model
        )

        logger.info("Connecting to Weaviate...")
        vector_store = WeaviateVectorStore(
            url=weaviate_url,
            api_key=weaviate_api_key,
            collection_name="DocumentChunk"
        )

        # Initialize RAG pipeline
        logger.info("Initializing RAG pipeline...")
        pipeline = RAGPipeline(
            embedding_service=embedding_service,
            vector_store=vector_store,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )

        # Clear namespace if requested
        if args.clear_namespace:
            logger.warning(f"Clearing namespace '{args.namespace}'...")
            pipeline.clear_namespace(args.namespace)

        # Ingest documents
        if args.file:
            # Single file ingestion
            if not os.path.exists(args.file):
                logger.error(f"File not found: {args.file}")
                sys.exit(1)

            logger.info(f"Ingesting file: {args.file}")
            num_chunks = pipeline.ingest_document(args.file, args.namespace)
            logger.info(f"✅ Successfully ingested {num_chunks} chunks")

        elif args.directory:
            # Directory ingestion
            if not os.path.isdir(args.directory):
                logger.error(f"Directory not found: {args.directory}")
                sys.exit(1)

            logger.info(f"Ingesting all PDFs from: {args.directory}")
            total_chunks = pipeline.ingest_directory(
                args.directory,
                args.namespace,
                file_pattern="*.pdf"
            )
            logger.info(f"✅ Successfully ingested {total_chunks} total chunks")

        # Show stats
        stats = pipeline.get_stats()
        logger.info(f"\n{'='*60}")
        logger.info(f"Vector Store Statistics:")
        logger.info(f"  Total chunks: {stats.get('total_chunks', 0)}")
        logger.info(f"{'='*60}\n")

    except Exception as e:
        logger.error(f"❌ Error during ingestion: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
