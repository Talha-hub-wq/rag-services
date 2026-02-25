"""
Shared test fixtures and configurations for all tests.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient

# Set test environment BEFORE importing anything else
os.environ["ENV"] = "testing"
os.environ["OPENAI_API_KEY"] = "sk-test-key-1234567890"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["CHUNK_SIZE"] = "500"
os.environ["CHUNK_OVERLAP"] = "50"
os.environ["DOCUMENTS_PATH"] = "/tmp/test_documents"
os.environ["SMTP_HOST"] = "smtp.gmail.com"
os.environ["SMTP_PORT"] = "587"
os.environ["SMTP_USER"] = "test@gmail.com"
os.environ["SMTP_PASSWORD"] = "test-password"
os.environ["EMAIL_FROM"] = "test@example.com"


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock_client = MagicMock()

    # Mock chat completions
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response from AI"
    mock_client.chat.completions.create.return_value = mock_response

    # Mock embeddings
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock() for _ in range(3)]
    for i, item in enumerate(mock_embedding_response.data):
        item.embedding = [0.1] * 1536
    mock_client.embeddings.create.return_value = mock_embedding_response

    return mock_client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    # Mock database operations
    mock_response = MagicMock()
    mock_response.data = [{"id": 1}]

    mock_table.insert.return_value.execute.return_value = mock_response
    mock_table.select.return_value.execute.return_value = mock_response
    mock_table.select.return_value.eq.return_value.execute.return_value = (
        mock_response
    )
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        mock_response
    )
    mock_table.delete.return_value.eq.return_value.execute.return_value = (
        mock_response
    )

    # Mock RPC calls for vector search
    mock_rpc_response = MagicMock()
    mock_rpc_response.data = [
        {"id": 1, "content": "test", "similarity": 0.95},
        {"id": 2, "content": "test2", "similarity": 0.87},
    ]
    mock_client.rpc.return_value.execute.return_value = mock_rpc_response

    return mock_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "test-user-123",
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_document():
    """Sample document for testing."""
    return {
        "id": "doc-123",
        "content": "This is a test document content for RAG system testing.",
        "embedding": [0.1] * 1536,
        "source_file": "test_document.docx",
        "metadata": {"chunk_index": 0, "total_chunks": 1},
        "similarity": 0.95,
    }


@pytest.fixture
def sample_chat_request():
    """Sample chat request."""
    return {
        "query": "What is the main topic of the document?",
        "top_k": 5,
        "similarity_threshold": 0.5,
    }


@pytest.fixture
def sample_documents_for_rag():
    """Sample retrieved documents for RAG."""
    return [
        {
            "content": "The main topic is about machine learning.",
            "source_file": "doc1.docx",
            "similarity": 0.95,
        },
        {
            "content": "Machine learning involves training models.",
            "source_file": "doc2.docx",
            "similarity": 0.87,
        },
    ]


@pytest.fixture
def test_token():
    """Generate a test JWT token."""
    from datetime import datetime, timedelta
    from jose import jwt

    secret_key = "test-secret-key"
    algorithm = "HS256"

    payload = {
        "sub": "testuser@example.com",
        "user_id": "test-user-123",
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


@pytest.fixture
def test_refresh_token():
    """Generate a test refresh token."""
    from datetime import datetime, timedelta
    from jose import jwt

    secret_key = "test-secret-key"
    algorithm = "HS256"

    payload = {
        "sub": "testuser@example.com",
        "user_id": "test-user-123",
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7),
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


@pytest.fixture
def fastapi_test_client(mock_openai_client, mock_supabase_client):
    """Create FastAPI test client with mocked services."""
    with patch("services.embedding_service.OpenAI", return_value=mock_openai_client):
        with patch("services.rag_service.OpenAI", return_value=mock_openai_client):
            with patch(
                "services.vector_store.create_client", return_value=mock_supabase_client
            ):
                with patch(
                    "services.auth_service.create_client", return_value=mock_supabase_client
                ):
                    with patch(
                        "main.create_client", return_value=mock_supabase_client
                    ):
                        # Import after patching
                        from main import app

                        return TestClient(app)


@pytest.fixture(autouse=True)
def patch_supabase(mock_supabase_client):
    """Automatically patch Supabase client in all tests."""
    with patch("services.vector_store.supabase", mock_supabase_client):
        with patch("services.auth_service.supabase", mock_supabase_client):
            with patch("main.supabase", mock_supabase_client):
                yield


@pytest.fixture(autouse=True)
def patch_openai(mock_openai_client):
    """Automatically patch OpenAI client in all tests."""
    with patch("services.embedding_service.openai_client", mock_openai_client):
        with patch("services.rag_service.openai_client", mock_openai_client):
            yield
