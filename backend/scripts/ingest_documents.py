#!/usr/bin/env python3
"""
Document ingestion script for MediCopilot.

Ingests GPC and COFEPRIS documents into Weaviate vector database.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from rag.embeddings import SaptivaEmbeddingService, MockEmbeddingService
from rag.vectorstore import WeaviateVectorStore
from rag.pipeline import RAGPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion function."""
    parser = argparse.ArgumentParser(description='Ingest medical documents into Weaviate')
    parser.add_argument(
        '--mode',
        choices=['all', 'gpc', 'cofepris', 'single'],
        default='all',
        help='Ingestion mode'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Single file to ingest (required if mode=single)'
    )
    parser.add_argument(
        '--namespace',
        type=str,
        help='Namespace for single file ingestion'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data before ingestion'
    )
    parser.add_argument(
        '--mock-embeddings',
        action='store_true',
        help='Use mock embeddings (for testing without API key)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Verify required environment variables
    required_vars = ['WEAVIATE_HOST', 'WEAVIATE_API_KEY']
    if not args.mock_embeddings:
        required_vars.append('SAPTIVA_API_KEY')

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set them in .env file")
        sys.exit(1)

    try:
        # Initialize services
        logger.info("Initializing services...")

        if args.mock_embeddings:
            logger.warning("Using MOCK embeddings - not suitable for production!")
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

        logger.info("✅ Services initialized successfully")

        # Clear data if requested
        if args.clear:
            logger.warning("Clearing existing data...")
            if args.mode == 'gpc' or args.mode == 'all':
                pipeline.clear_namespace('gpc')
            if args.mode == 'cofepris' or args.mode == 'all':
                pipeline.clear_namespace('cofepris')

        # Determine data directory (relative to script location)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        data_dir = project_root / "data"

        logger.info(f"Data directory: {data_dir}")

        # Perform ingestion based on mode
        if args.mode == 'single':
            if not args.file or not args.namespace:
                logger.error("--file and --namespace are required for single mode")
                sys.exit(1)

            logger.info(f"\n{'='*60}")
            logger.info("INGESTING SINGLE FILE")
            logger.info(f"{'='*60}\n")

            pipeline.ingest_document(args.file, args.namespace)

        elif args.mode == 'gpc' or args.mode == 'all':
            gpc_dir = data_dir / "GPC"

            if not gpc_dir.exists():
                logger.error(f"GPC directory not found: {gpc_dir}")
            else:
                logger.info(f"\n{'='*60}")
                logger.info("INGESTING GPC DOCUMENTS")
                logger.info(f"{'='*60}\n")

                total = pipeline.ingest_directory(str(gpc_dir), namespace='gpc')
                logger.info(f"GPC ingestion complete: {total} chunks")

        if args.mode == 'cofepris' or args.mode == 'all':
            cofepris_dir = data_dir / "COFEPRIS"

            if not cofepris_dir.exists():
                logger.error(f"COFEPRIS directory not found: {cofepris_dir}")
            else:
                logger.info(f"\n{'='*60}")
                logger.info("INGESTING COFEPRIS DOCUMENTS")
                logger.info(f"{'='*60}\n")

                total = pipeline.ingest_directory(str(cofepris_dir), namespace='cofepris')
                logger.info(f"COFEPRIS ingestion complete: {total} chunks")

        # Show final statistics
        logger.info(f"\n{'='*60}")
        logger.info("FINAL STATISTICS")
        logger.info(f"{'='*60}")

        stats = pipeline.get_stats()
        logger.info(f"Total chunks in database: {stats.get('total_chunks', 0)}")

        logger.info(f"\n{'='*60}")
        logger.info("✅ INGESTION COMPLETE!")
        logger.info(f"{'='*60}\n")

    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
