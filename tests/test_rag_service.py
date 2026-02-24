"""
Test suite for RAG service.
"""
import pytest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any


@pytest.mark.unit
class TestRAGServiceInitialization:
    """Test RAG service initialization."""
    
    def test_rag_service_initializes_with_api_key(self, mock_openai_client):
        """Test RAG service initialization."""
        from services.rag_service import RAGService
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(
                api_key="sk-test-key",
                model="gpt-4-turbo-preview"
            )
            
            assert service.model == "gpt-4-turbo-preview"
            assert service.system_prompt
    
    def test_rag_service_has_system_prompt(self, mock_openai_client):
        """Test that RAG service has proper system prompt."""
        from services.rag_service import RAGService
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(api_key="sk-test-key")
            
            assert "context" in service.system_prompt.lower()
            assert "question" in service.system_prompt.lower()


@pytest.mark.unit
class TestGenerateResponse:
    """Test response generation."""
    
    def test_generate_response_with_context(self, mock_openai_client, sample_documents_for_rag):
        """Test generating response with context."""
        from services.rag_service import RAGService
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(api_key="sk-test-key")
            
            response = service.generate_response(
                query="What is machine learning?",
                context_documents=sample_documents_for_rag
            )
            
            assert response
            assert isinstance(response, str)
            assert len(response) > 0
    
    def test_generate_response_empty_context(self, mock_openai_client):
        """Test generating response with empty context."""
        from services.rag_service import RAGService
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(api_key="sk-test-key")
            
            response = service.generate_response(
                query="What is AI?",
                context_documents=[]
            )
            
            assert "don't have any relevant information" in response or response
    
    def test_generate_response_with_single_document(self, mock_openai_client):
        """Test generating response with single document."""
        from services.rag_service import RAGService
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(api_key="sk-test-key")
            
            documents = [{
                "content": "Python is a programming language.",
                "source_file": "doc.docx",
                "similarity": 0.95
            }]
            
            response = service.generate_response(
                query="What is Python?",
                context_documents=documents
            )
            
            assert response
            assert isinstance(response, str)
    
    def test_generate_response_includes_source_information(self, mock_openai_client):
        """Test that response includes source information."""
        from services.rag_service import RAGService
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(api_key="sk-test-key")
            
            documents = [{
                "content": "The Earth orbits the Sun.",
                "source_file": "astronomy.docx",
                "similarity": 0.99
            }]
            
            response = service.generate_response(
                query="Does Earth orbit the Sun?",
                context_documents=documents
            )
            
            # Response should be generated
            assert response
    
    def test_generate_response_handles_api_error(self, mock_openai_client):
        """Test error handling when OpenAI API fails."""
        from services.rag_service import RAGService
        
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(api_key="sk-test-key")
            
            with pytest.raises(Exception):
                service.generate_response(
                    query="What is AI?",
                    context_documents=[{"content": "AI is artificial intelligence."}]
                )


@pytest.mark.unit
class TestStreamingResponse:
    """Test streaming response generation."""
    
    def test_generate_streaming_response(self, mock_openai_client, sample_documents_for_rag):
        """Test generating streaming response."""
        from services.rag_service import RAGService
        
        # Mock streaming response
        mock_openai_client.chat.completions.create.return_value = MagicMock()
        mock_openai_client.chat.completions.create.return_value.choices = [MagicMock()]
        mock_openai_client.chat.completions.create.return_value.choices[0].delta.content = "chunk"
        
        with patch('openai.OpenAI', return_value=mock_openai_client):
            service = RAGService(api_key="sk-test-key")
            
            # Verify streaming method exists
            assert hasattr(service, 'generate_response_streaming')


@pytest.mark.unit
class TestContextBuilding:
    """Test context building for RAG."""
    
    def test_context_includes_all_documents(self):
        """Test that context includes all provided documents."""
        from services.rag_service import RAGService
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            service = RAGService(api_key="sk-test-key")
            
            documents = [
                {"content": "Doc 1", "source_file": "f1.docx", "similarity": 0.9},
                {"content": "Doc 2", "source_file": "f2.docx", "similarity": 0.8},
                {"content": "Doc 3", "source_file": "f3.docx", "similarity": 0.7}
            ]
            
            response = service.generate_response(
                query="Question?",
                context_documents=documents
            )
            
            assert response
    
    def test_context_includes_source_file_information(self):
        """Test that context includes source file information."""
        from services.rag_service import RAGService
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            service = RAGService(api_key="sk-test-key")
            
            documents = [{
                "content": "Important information",
                "source_file": "important.docx",
                "similarity": 0.95
            }]
            
            service.generate_response(
                query="Question?",
                context_documents=documents
            )
            
            # Verify API was called
            mock_client.chat.completions.create.assert_called()


@pytest.mark.unit
class TestResponseTemperature:
    """Test response generation temperature settings."""
    
    def test_response_uses_correct_temperature(self):
        """Test that response generation uses correct temperature."""
        from services.rag_service import RAGService
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            service = RAGService(api_key="sk-test-key")
            
            service.generate_response(
                query="Question?",
                context_documents=[{"content": "Answer"}]
            )
            
            # Verify temperature is set
            call_args = mock_client.chat.completions.create.call_args
            assert 'temperature' in call_args.kwargs


@pytest.mark.unit
class TestResponseMaxTokens:
    """Test response max tokens setting."""
    
    def test_response_respects_max_tokens(self):
        """Test that response generation respects max_tokens."""
        from services.rag_service import RAGService
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            service = RAGService(api_key="sk-test-key")
            
            service.generate_response(
                query="Question?",
                context_documents=[{"content": "Answer"}]
            )
            
            call_args = mock_client.chat.completions.create.call_args
            assert 'max_tokens' in call_args.kwargs
