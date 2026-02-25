"""
Shared test fixtures and configurations for all tests.
Apply patches at the EARLIEST possible stage - before any imports!
"""

import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch

# ========== CRITICAL: Set environment FIRST ==========
os.environ["ENV"] = "testing"
os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["DOCUMENTS_PATH"] = "/tmp/test_docs"


# ========== pytest_configure hook - runs BEFORE collecting tests ==========
def pytest_configure(config):
    """Apply patches before test collection."""
    # Create mocks
    supabase_mock = MagicMock()
    openai_mock = MagicMock()
    
    # Configure Supabase mock
    table_mock = MagicMock()
    response = MagicMock(data=[{"id": 1}])
    
    table_mock.insert.return_value.execute.return_value = response
    table_mock.select.return_value.execute.return_value = response
    table_mock.select.return_value.eq.return_value.execute.return_value = response
    table_mock.delete.return_value.eq.return_value.execute.return_value = response
    
    rpc_response = MagicMock(data=[{"id": 1, "content": "test", "similarity": 0.95}])
    supabase_mock.table.return_value = table_mock
    supabase_mock.rpc.return_value.execute.return_value = rpc_response
    
    # Configure OpenAI mock
    embed_response = MagicMock()
    embed_response.data = [MagicMock() for _ in range(3)]
    for item in embed_response.data:
        item.embedding = [0.1] * 1536
    openai_mock.embeddings.create.return_value = embed_response
    
    chat_response = MagicMock()
    chat_response.choices = [MagicMock()]
    chat_response.choices[0].message.content = "Test response"
    openai_mock.chat.completions.create.return_value = chat_response
    
    # Apply patches GLOBALLY
    patch("supabase.create_client", return_value=supabase_mock).start()
    patch("openai.OpenAI", return_value=openai_mock).start()


@pytest.fixture(scope="function", autouse=True)
def mock_dependencies():
    """Inject mocks into all tests."""
    supabase_mock = MagicMock()
    openai_mock = MagicMock()
    
    table_mock = MagicMock()
    response = MagicMock(data=[{"id": 1}])
    
    table_mock.insert.return_value.execute.return_value = response
    table_mock.select.return_value.execute.return_value = response
    table_mock.select.return_value.eq.return_value.execute.return_value = response
    table_mock.delete.return_value.eq.return_value.execute.return_value = response
    
    rpc_response = MagicMock(data=[{"id": 1, "content": "test", "similarity": 0.95}])
    supabase_mock.table.return_value = table_mock
    supabase_mock.rpc.return_value.execute.return_value = rpc_response
    
    embed_response = MagicMock()
    embed_response.data = [MagicMock() for _ in range(3)]
    for item in embed_response.data:
        item.embedding = [0.1] * 1536
    openai_mock.embeddings.create.return_value = embed_response
    
    chat_response = MagicMock()
    chat_response.choices = [MagicMock()]
    chat_response.choices[0].message.content = "Test response"
    openai_mock.chat.completions.create.return_value = chat_response
    
    with patch("supabase.create_client", return_value=supabase_mock):
        with patch("openai.OpenAI", return_value=openai_mock):
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
