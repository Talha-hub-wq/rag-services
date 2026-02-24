"""
Test suite for vector store service.
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestVectorStoreInitialization:
    """Test vector store initialization."""
    
    def test_vector_store_initializes_with_credentials(self, mock_supabase_client):
        """Test vector store initialization."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            assert store.table_name == "documents"
            assert store.client is not None
    
    def test_vector_store_custom_table_name(self, mock_supabase_client):
        """Test vector store with custom table name."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key",
                table_name="custom_docs"
            )
            
            assert store.table_name == "custom_docs"


@pytest.mark.unit
class TestInsertDocument:
    """Test document insertion."""
    
    def test_insert_document_returns_true(self, mock_supabase_client):
        """Test that insert_document returns True on success."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            result = store.insert_document(
                content="Test document",
                embedding=[0.1] * 1536,
                source_file="test.docx"
            )
            
            assert result is True
    
    def test_insert_document_with_metadata(self, mock_supabase_client):
        """Test inserting document with metadata."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            metadata = {"chunk_index": 0, "total_chunks": 5}
            result = store.insert_document(
                content="Test document",
                embedding=[0.1] * 1536,
                source_file="test.docx",
                metadata=metadata
            )
            
            assert result is True
    
    def test_insert_multiple_documents(self, mock_supabase_client):
        """Test inserting multiple documents sequentially."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            for i in range(5):
                result = store.insert_document(
                    content=f"Document {i}",
                    embedding=[0.1 + i * 0.01] * 1536,
                    source_file=f"doc{i}.docx"
                )
                assert result is True


@pytest.mark.unit
class TestBatchInsert:
    """Test batch document insertion."""
    
    def test_insert_documents_batch_returns_true(self, mock_supabase_client):
        """Test that batch insert returns True."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            documents = [
                {
                    "content": f"Doc {i}",
                    "embedding": [0.1] * 1536,
                    "source_file": f"doc{i}.docx"
                }
                for i in range(10)
            ]
            
            result = store.insert_documents_batch(documents)
            
            assert result is True
    
    def test_insert_empty_batch(self, mock_supabase_client):
        """Test inserting empty batch."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            result = store.insert_documents_batch([])
            
            # Empty batch should be handled gracefully
            assert result is True


@pytest.mark.unit
class TestSearchSimilar:
    """Test similarity search."""
    
    def test_search_similar_returns_documents(self, mock_supabase_client):
        """Test that search_similar returns documents."""
        from services.vector_store import VectorStore
        
        # Mock the RPC response
        mock_supabase_client.rpc.return_value.execute.return_value.data = [
            {
                "id": 1,
                "content": "Similar document 1",
                "source_file": "doc1.docx",
                "similarity": 0.95
            },
            {
                "id": 2,
                "content": "Similar document 2",
                "source_file": "doc2.docx",
                "similarity": 0.87
            }
        ]
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            results = store.search_similar(
                query_embedding=[0.1] * 1536,
                top_k=5
            )
            
            assert isinstance(results, list)
            assert len(results) > 0
    
    def test_search_with_custom_top_k(self, mock_supabase_client):
        """Test search with custom top_k."""
        from services.vector_store import VectorStore
        
        mock_supabase_client.rpc.return_value.execute.return_value.data = [
            {"id": i, "content": f"Doc {i}", "source_file": f"doc{i}.docx", "similarity": 0.9}
            for i in range(10)
        ]
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            results = store.search_similar(
                query_embedding=[0.1] * 1536,
                top_k=10
            )
            
            assert len(results) <= 10
    
    def test_search_with_similarity_threshold(self, mock_supabase_client):
        """Test search with similarity threshold."""
        from services.vector_store import VectorStore
        
        mock_supabase_client.rpc.return_value.execute.return_value.data = [
            {"id": 1, "content": "High similarity", "source_file": "doc1.docx", "similarity": 0.95},
            {"id": 2, "content": "Low similarity", "source_file": "doc2.docx", "similarity": 0.45}
        ]
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            results = store.search_similar(
                query_embedding=[0.1] * 1536,
                top_k=10,
                similarity_threshold=0.7
            )
            
            # Should filter based on threshold
            assert isinstance(results, list)
    
    def test_search_returns_no_results(self, mock_supabase_client):
        """Test search when no results found."""
        from services.vector_store import VectorStore
        
        mock_supabase_client.rpc.return_value.execute.return_value.data = []
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            results = store.search_similar(
                query_embedding=[0.1] * 1536,
                top_k=5
            )
            
            assert results == []


@pytest.mark.unit
class TestVectorStoreError:
    """Test error handling."""
    
    def test_insert_document_error_handling(self, mock_supabase_client):
        """Test error handling during insert."""
        from services.vector_store import VectorStore
        
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            result = store.insert_document(
                content="Test",
                embedding=[0.1] * 1536,
                source_file="test.docx"
            )
            
            # Should return False on error
            assert result is False
    
    def test_batch_insert_error_handling(self, mock_supabase_client):
        """Test error handling during batch insert."""
        from services.vector_store import VectorStore
        
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            documents = [{"content": "Doc", "embedding": [0.1] * 1536}]
            result = store.insert_documents_batch(documents)
            
            assert result is False


@pytest.mark.unit
class TestVectorDimensions:
    """Test vector dimension handling."""
    
    def test_accepts_1536_dimension_vectors(self, mock_supabase_client):
        """Test accepting 1536-dimension embeddings."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            embedding = [0.1] * 1536
            result = store.insert_document(
                content="Test",
                embedding=embedding,
                source_file="test.docx"
            )
            
            assert result is True


@pytest.mark.unit
class TestSourceFileTracking:
    """Test source file tracking."""
    
    def test_document_preserves_source_file(self, mock_supabase_client):
        """Test that source file is preserved."""
        from services.vector_store import VectorStore
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            source_file = "important_document.docx"
            result = store.insert_document(
                content="Test content",
                embedding=[0.1] * 1536,
                source_file=source_file
            )
            
            assert result is True
    
    def test_search_results_include_source_file(self, mock_supabase_client):
        """Test that search results include source file."""
        from services.vector_store import VectorStore
        
        mock_supabase_client.rpc.return_value.execute.return_value.data = [
            {
                "id": 1,
                "content": "Result content",
                "source_file": "result_doc.docx",
                "similarity": 0.95
            }
        ]
        
        with patch('supabase.create_client', return_value=mock_supabase_client):
            store = VectorStore(
                supabase_url="https://test.supabase.co",
                supabase_key="test-key"
            )
            
            results = store.search_similar(
                query_embedding=[0.1] * 1536,
                top_k=5
            )
            
            assert len(results) > 0
            assert "source_file" in results[0]
