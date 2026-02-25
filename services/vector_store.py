from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Service responsible for storing and retrieving embeddings from Supabase."""

    def __init__(
        self, supabase_url: str, supabase_key: str, table_name: str = "documents"
    ):
        """
        Initialize the vector store.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service key
            table_name: Name of the table to store documents
        """
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = table_name

    def initialize_table(self):
        """
        Initialize the vector store table with proper schema.
        Note: This should be run as a SQL migration in Supabase.
        """
        # This is informational - actual table creation should be done via Supabase SQL editor
        schema = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Create documents table
        CREATE TABLE IF NOT EXISTS documents (
            id BIGSERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding VECTOR(1536),
            metadata JSONB,
            source_file TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
        );
        
        -- Create index for similarity search
        CREATE INDEX IF NOT EXISTS documents_embedding_idx 
        ON documents USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
        logger.info(f"Table schema for '{self.table_name}':\n{schema}")

    def insert_document(
        self,
        content: str,
        embedding: List[float],
        source_file: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Insert a document with its embedding into the vector store.

        Args:
            content: Document text content
            embedding: Embedding vector
            source_file: Source file path
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "content": content,
                "embedding": embedding,
                "source_file": source_file,
                "metadata": metadata or {},
            }

            result = self.client.table(self.table_name).insert(data).execute()
            logger.debug(f"Inserted document from {source_file}")
            return True
        except Exception as e:
            logger.error(f"Error inserting document: {str(e)}")
            return False

    def insert_documents_batch(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Insert multiple documents in a batch.

        Args:
            documents: List of document dictionaries with content, embedding, source_file

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).insert(documents).execute()
            logger.info(f"Inserted {len(documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error batch inserting documents: {str(e)}")
            return False

    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar documents with content and metadata
        """
        try:
            # Execute RPC function for similarity search
            result = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": similarity_threshold,
                    "match_count": top_k,
                },
            ).execute()

            documents = result.data if result.data else []
            logger.info(f"Found {len(documents)} similar documents")
            return documents
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []

    def clear_all_documents(self) -> bool:
        """
        Clear all documents from the vector store.
        Use with caution!

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).delete().neq("id", 0).execute()
            logger.warning("Cleared all documents from vector store")
            return True
        except Exception as e:
            logger.error(f"Error clearing documents: {str(e)}")
            return False
