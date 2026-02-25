"""
Shared test fixtures and configurations for all tests.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch

# Set test environment BEFORE importing anything
os.environ["ENV"] = "testing"
os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["DOCUMENTS_PATH"] = "/tmp/test_docs"


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = MagicMock()
    mock_table = MagicMock()
    mock.table.return_value = mock_table
    
    # Default responses
    response = MagicMock()
    response.data = [{"id": 1}]
    
    mock_table.insert.return_value.execute.return_value = response
    mock_table.select.return_value.execute.return_value = response
    mock_table.select.return_value.eq.return_value.execute.return_value = response
    mock_table.delete.return_value.eq.return_value.execute.return_value = response
    
    mock_rpc_response = MagicMock()
    mock_rpc_response.data = [{"id": 1, "content": "test", "similarity": 0.95}]
    mock.rpc.return_value.execute.return_value = mock_rpc_response
    
    return mock


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    mock = MagicMock()
    
    # Mock embeddings
    embed_response = MagicMock()
    embed_response.data = [MagicMock() for _ in range(3)]
    for item in embed_response.data:
        item.embedding = [0.1] * 1536
    mock.embeddings.create.return_value = embed_response
    
    # Mock chat completions
    chat_response = MagicMock()
    chat_response.choices = [MagicMock()]
    chat_response.choices[0].message.content = "Test response"
    mock.chat.completions.create.return_value = chat_response
    
    return mock


@pytest.fixture(autouse=True)
def mock_external_services(mock_supabase, mock_openai):
    """Auto-patch all external services."""
    with patch("supabase.create_client", return_value=mock_supabase):
        with patch("openai.OpenAI", return_value=mock_openai):
            yield




@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    from datetime import datetime
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
