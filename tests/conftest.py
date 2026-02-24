"""
Shared test fixtures and configurations for all tests.
"""
import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient


# Set test environment
os.environ['ENV'] = 'testing'


@pytest.fixture(scope="session")
def test_env():
    """Load test environment variables."""
    test_env = {
        "OPENAI_API_KEY": "sk-test-key-1234567890",
        "EMBEDDING_MODEL": "text-embedding-3-large",
        "CHAT_MODEL": "gpt-4-turbo-preview",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "JWT_SECRET_KEY": "test-secret-key",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "CHUNK_SIZE": "500",
        "CHUNK_OVERLAP": "50",
        "DOCUMENTS_PATH": "/tmp/test_documents",
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "test@gmail.com",
        "SMTP_PASSWORD": "test-password",
        "EMAIL_FROM": "test@example.com"
    }
    for key, value in test_env.items():
        os.environ[key] = value
    return test_env


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response from AI"
    mock_client.chat.completions.create.return_value = mock_response
    
    # Mock embeddings
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock()]
    mock_embedding_response.data[0].embedding = [0.1] * 1536  # 1536 dimensions
    mock_client.embeddings.create.return_value = mock_embedding_response
    
    return mock_client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock insert
    mock_insert = MagicMock()
    mock_insert.execute.return_value = MagicMock(data=[{"id": 1}])
    mock_table.insert.return_value = mock_insert
    
    # Mock select
    mock_select = MagicMock()
    mock_select.execute.return_value = MagicMock(data=[{"id": 1, "email": "test@example.com"}])
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_select
    mock_select.single.return_value = mock_select
    
    # Mock RPC calls
    mock_rpc = MagicMock()
    mock_rpc.execute.return_value = MagicMock(data=[{"id": 1, "content": "test", "similarity": 0.95}])
    mock_client.rpc.return_value = mock_rpc
    
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
        "created_at": datetime.utcnow()
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
        "similarity": 0.95
    }


@pytest.fixture
def sample_chat_request():
    """Sample chat request."""
    return {
        "query": "What is the main topic of the document?",
        "top_k": 5,
        "similarity_threshold": 0.5
    }


@pytest.fixture
def sample_documents_for_rag():
    """Sample retrieved documents for RAG."""
    return [
        {
            "content": "The main topic is about machine learning.",
            "source_file": "doc1.docx",
            "similarity": 0.95
        },
        {
            "content": "Machine learning involves training models.",
            "source_file": "doc2.docx",
            "similarity": 0.87
        }
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
        "exp": datetime.utcnow() + timedelta(minutes=30)
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
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


@pytest.fixture
def fastapi_test_client(test_env, mock_openai_client, mock_supabase_client):
    """Create FastAPI test client with mocked services."""
    from fastapi import FastAPI, Depends
    from fastapi.testclient import TestClient
    
    # Import your main app
    from main import app
    
    # Create test client
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment after each test."""
    yield
    # Cleanup code here if needed
    pass
