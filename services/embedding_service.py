from typing import List
import openai
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service responsible for creating embeddings using OpenAI."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-large"):
        """
        Initialize the embedding service.

        Args:
            api_key: OpenAI API key
            model: Embedding model to use
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings.create(
                input=text, model=self.model, dimensions=1536  # Ye line add karo
            )
            embedding = response.data[0].embedding
            logger.debug(f"Created embedding of dimension {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                input=texts, model=self.model, dimensions=1536  # Ye line add karo
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Created {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {str(e)}")
            raise
