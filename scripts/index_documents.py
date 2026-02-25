"""
Script to index documents from local directory into Supabase vector store.
This should be run once to process and index all documents.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import logging
from config import settings
from services import DocumentLoader, TextProcessor, EmbeddingService, VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def index_documents():
    """Main function to index all documents."""
    logger.info("Starting document indexing process...")

    # Initialize services
    logger.info("Initializing services...")
    document_loader = DocumentLoader(settings.documents_path)
    text_processor = TextProcessor()
    embedding_service = EmbeddingService(
        api_key=settings.openai_api_key, model=settings.embedding_model
    )
    vector_store = VectorStore(
        supabase_url=settings.supabase_url, supabase_key=settings.supabase_key
    )

    # Print table initialization schema
    logger.info("Vector store table schema:")
    vector_store.initialize_table()

    # Statistics
    total_documents = 0
    total_chunks = 0
    indexed_chunks = 0
    failed_chunks = 0

    # Process documents
    logger.info(f"Loading documents from: {settings.documents_path}")

    for file_path, content in document_loader.load_all_documents():
        total_documents += 1
        logger.info(f"Processing document {total_documents}: {file_path}")

        # Process document into chunks
        chunks = text_processor.process_document(
            content, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap
        )

        total_chunks += len(chunks)
        logger.info(f"Created {len(chunks)} chunks from document")

        # Create embeddings and store
        for idx, chunk in enumerate(chunks):
            try:
                # Create embedding
                embedding = embedding_service.create_embedding(chunk)

                # Store in vector database
                success = vector_store.insert_document(
                    content=chunk,
                    embedding=embedding,
                    source_file=file_path,
                    metadata={"chunk_index": idx, "total_chunks": len(chunks)},
                )

                if success:
                    indexed_chunks += 1
                else:
                    failed_chunks += 1

                # MEMORY CLEAR karo har 10 chunks pe
                if idx % 10 == 0:
                    import gc

                    gc.collect()

            except Exception as e:
                logger.error(f"Error: {str(e)}")
                failed_chunks += 1

    # Print summary
    logger.info("=" * 60)
    logger.info("INDEXING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total documents processed: {total_documents}")
    logger.info(f"Total chunks created: {total_chunks}")
    logger.info(f"Successfully indexed: {indexed_chunks}")
    logger.info(f"Failed chunks: {failed_chunks}")
    logger.info(f"Success rate: {(indexed_chunks/total_chunks*100):.2f}%")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        index_documents()
    except Exception as e:
        logger.error(f"Fatal error during indexing: {str(e)}")
        raise
