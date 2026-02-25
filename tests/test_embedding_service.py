"""
Test suite for embedding service.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import List


@pytest.mark.unit
class TestEmbeddingServiceInitialization:
    """Test embedding service initialization."""

    def test_embedding_service_initializes_with_api_key(self, mock_openai_client):
        """Test embedding service initialization."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(
                api_key="sk-test-key", model="text-embedding-3-large"
            )

            assert service.model == "text-embedding-3-large"
            assert service.client is not None

    def test_embedding_service_uses_default_model(self, mock_openai_client):
        """Test that embedding service uses default model."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            assert service.model == "text-embedding-3-large"


@pytest.mark.unit
class TestCreateEmbedding:
    """Test single embedding creation."""

    def test_create_embedding_returns_vector(self, mock_openai_client):
        """Test that create_embedding returns a vector."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            embedding = service.create_embedding("Test text")

            assert isinstance(embedding, list)
            assert len(embedding) == 1536  # Expected dimension

    def test_create_embedding_with_long_text(self, mock_openai_client):
        """Test creating embedding for long text."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            long_text = "This is a test. " * 1000
            embedding = service.create_embedding(long_text)

            assert isinstance(embedding, list)
            assert len(embedding) == 1536

    def test_create_embedding_with_short_text(self, mock_openai_client):
        """Test creating embedding for short text."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            embedding = service.create_embedding("Hi")

            assert isinstance(embedding, list)
            assert len(embedding) == 1536

    def test_create_embedding_with_special_characters(self, mock_openai_client):
        """Test embedding with special characters."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            text = "Test@#$%^&*()_+-=[]{}|;':,./<>?"
            embedding = service.create_embedding(text)

            assert isinstance(embedding, list)

    def test_create_embedding_with_unicode(self, mock_openai_client):
        """Test embedding with unicode text."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            text = "Hello مرحبا こんにちは"
            embedding = service.create_embedding(text)

            assert isinstance(embedding, list)


@pytest.mark.unit
class TestCreateBatchEmbeddings:
    """Test batch embedding creation."""

    def test_create_embeddings_batch_returns_list(self, mock_openai_client):
        """Test that create_embeddings_batch returns list of vectors."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = service.create_embeddings_batch(texts)

            assert isinstance(embeddings, list)
            assert len(embeddings) == 3

    def test_batch_embeddings_correct_dimensions(self, mock_openai_client):
        """Test that batch embeddings have correct dimensions."""
        from services.embedding_service import EmbeddingService

        # Mock batch response
        mock_openai_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
            MagicMock(embedding=[0.3] * 1536),
        ]

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            embeddings = service.create_embeddings_batch(["Text 1", "Text 2", "Text 3"])

            assert len(embeddings) == 3
            for embedding in embeddings:
                assert len(embedding) == 1536

    def test_batch_embeddings_single_text(self, mock_openai_client):
        """Test batch embedding with single text."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            embeddings = service.create_embeddings_batch(["Single text"])

            assert len(embeddings) == 1

    def test_batch_embeddings_large_batch(self, mock_openai_client):
        """Test batch embedding with many texts."""
        from services.embedding_service import EmbeddingService

        texts = [f"Text {i}" for i in range(100)]

        # Mock response for 100 items
        mock_openai_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1] * 1536) for _ in range(100)
        ]

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            embeddings = service.create_embeddings_batch(texts)

            assert len(embeddings) == 100


@pytest.mark.unit
class TestEmbeddingDimensions:
    """Test embedding dimensions."""

    def test_embedding_dimension_is_1536(self, mock_openai_client):
        """Test that embedding dimension is 1536."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            embedding = service.create_embedding("Test")

            assert len(embedding) == 1536

    def test_embedding_values_are_floats(self, mock_openai_client):
        """Test that embedding values are floats."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            embedding = service.create_embedding("Test")

            for value in embedding:
                assert isinstance(value, float)


@pytest.mark.unit
class TestEmbeddingConsistency:
    """Test embedding consistency."""

    def test_same_text_produces_same_embedding(self, mock_openai_client):
        """Test that same text produces same embedding."""
        from services.embedding_service import EmbeddingService

        mock_openai_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.5] * 1536)
        ]

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            text = "Consistent test text"
            embedding1 = service.create_embedding(text)

            # Reset mock for second call
            mock_openai_client.embeddings.create.return_value.data = [
                MagicMock(embedding=[0.5] * 1536)
            ]

            embedding2 = service.create_embedding(text)

            # Both should have same dimension
            assert len(embedding1) == len(embedding2)


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in embedding service."""

    def test_embedding_service_handles_api_error(self, mock_openai_client):
        """Test error handling when API fails."""
        from services.embedding_service import EmbeddingService

        mock_openai_client.embeddings.create.side_effect = Exception("API Error")

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            with pytest.raises(Exception):
                service.create_embedding("Test")

    def test_batch_embedding_service_handles_api_error(self, mock_openai_client):
        """Test batch embedding error handling."""
        from services.embedding_service import EmbeddingService

        mock_openai_client.embeddings.create.side_effect = Exception("API Error")

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(api_key="sk-test-key")

            with pytest.raises(Exception):
                service.create_embeddings_batch(["Text 1", "Text 2"])


@pytest.mark.unit
class TestEmbeddingModel:
    """Test embedding model selection."""

    def test_uses_correct_embedding_model(self, mock_openai_client):
        """Test that correct embedding model is used."""
        from services.embedding_service import EmbeddingService

        with patch("openai.OpenAI", return_value=mock_openai_client):
            service = EmbeddingService(
                api_key="sk-test-key", model="text-embedding-3-large"
            )

            service.create_embedding("Test")

            # Verify API was called with correct model
            mock_openai_client.embeddings.create.assert_called()
