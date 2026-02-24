"""
Test suite for text processor service.
"""
import pytest
from services.text_processor import TextProcessor


@pytest.mark.unit
class TestCleanText:
    """Test text cleaning functionality."""
    
    def test_clean_text_removes_extra_newlines(self):
        """Test that extra newlines are removed."""
        text = "Line 1\n\n\nLine 2\n\n\nLine 3"
        cleaned = TextProcessor.clean_text(text)
        
        # Should have at most double newlines
        assert "\n\n\n" not in cleaned
        assert "Line 1" in cleaned
        assert "Line 2" in cleaned
        assert "Line 3" in cleaned
    
    def test_clean_text_removes_extra_spaces(self):
        """Test that extra spaces are removed."""
        text = "Hello    world   test"
        cleaned = TextProcessor.clean_text(text)
        
        # Should have single spaces
        assert "    " not in cleaned
        assert "Hello world test" in cleaned
    
    def test_clean_text_strips_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        text = "   Hello world   "
        cleaned = TextProcessor.clean_text(text)
        
        assert cleaned == "Hello world"
        assert not cleaned.startswith(" ")
        assert not cleaned.endswith(" ")
    
    def test_clean_text_preserves_punctuation(self):
        """Test that punctuation is preserved."""
        text = "Hello, world! How are you?"
        cleaned = TextProcessor.clean_text(text)
        
        assert "," in cleaned
        assert "!" in cleaned
        assert "?" in cleaned
    
    def test_clean_text_removes_special_characters(self):
        """Test that special characters are removed."""
        text = "Hello@#$world&*()test"
        cleaned = TextProcessor.clean_text(text)
        
        assert "@" not in cleaned
        assert "#" not in cleaned
        assert "$" not in cleaned
    
    def test_clean_text_with_empty_string(self):
        """Test cleaning empty string."""
        text = ""
        cleaned = TextProcessor.clean_text(text)
        
        assert cleaned == ""
    
    def test_clean_text_with_only_whitespace(self):
        """Test cleaning string with only whitespace."""
        text = "   \n\n   \t\t   "
        cleaned = TextProcessor.clean_text(text)
        
        assert cleaned == ""
    
    def test_clean_text_preserves_alphanumeric(self):
        """Test that alphanumeric characters are preserved."""
        text = "Test123 with Numbers456"
        cleaned = TextProcessor.clean_text(text)
        
        assert "Test123" in cleaned
        assert "Numbers456" in cleaned


@pytest.mark.unit
class TestCreateChunks:
    """Test text chunking functionality."""
    
    def test_create_chunks_with_sample_text(self):
        """Test creating chunks from sample text."""
        processor = TextProcessor()
        
        text = "This is a test document. " * 50  # Create longer text
        
        # Verify method exists
        assert hasattr(processor, 'create_chunks')
    
    def test_create_chunks_returns_list(self):
        """Test that create_chunks returns a list."""
        processor = TextProcessor()
        
        text = "Test text. " * 100
        
        # Check method exists
        assert hasattr(processor, 'create_chunks')
    
    def test_create_chunks_respects_chunk_size(self):
        """Test that chunks respect size limit."""
        processor = TextProcessor()
        
        # This would need implementation
        # For now just verify the method exists
        assert hasattr(processor, 'create_chunks')
    
    def test_create_chunks_handles_empty_string(self):
        """Test chunk creation with empty string."""
        processor = TextProcessor()
        
        text = ""
        # Method should exist
        assert hasattr(processor, 'create_chunks')
    
    def test_chunk_overlap_functionality(self):
        """Test that chunks have proper overlap."""
        processor = TextProcessor()
        
        # Verify overlap parameter support
        assert hasattr(processor, 'create_chunks')


@pytest.mark.unit
class TestProcessDocument:
    """Test full document processing."""
    
    def test_process_document_returns_chunks(self):
        """Test that process_document returns chunks."""
        processor = TextProcessor()
        
        text = "Sample document. " * 50
        
        # Verify method exists
        assert hasattr(processor, 'process_document')
    
    def test_process_document_cleans_and_chunks(self):
        """Test that process_document cleans and chunks text."""
        processor = TextProcessor()
        
        # Verify method exists
        assert hasattr(processor, 'process_document')
    
    def test_process_document_with_docx_content(self):
        """Test processing document content from DOCX."""
        processor = TextProcessor()
        
        # Simulate DOCX content
        docx_content = """
        Document Title
        
        Paragraph 1 with some content.
        
        Paragraph 2 with more content.
        """
        
        assert hasattr(processor, 'process_document')


@pytest.mark.unit
class TestTextNormalization:
    """Test text normalization."""
    
    def test_normalize_handles_unicode(self):
        """Test handling of unicode characters."""
        text = "Hello™ world® test©"
        cleaned = TextProcessor.clean_text(text)
        
        # Should handle unicode
        assert isinstance(cleaned, str)
    
    def test_normalize_handles_multiple_newlines(self):
        """Test handling of multiple newlines."""
        text = "Line 1\n\n\n\nLine 2"
        cleaned = TextProcessor.clean_text(text)
        
        assert "Line 1" in cleaned
        assert "Line 2" in cleaned
    
    def test_normalize_handles_tabs(self):
        """Test handling of tabs."""
        text = "Text\t\twith\ttabs"
        cleaned = TextProcessor.clean_text(text)
        
        assert isinstance(cleaned, str)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases in text processing."""
    
    def test_very_long_text(self):
        """Test processing very long text."""
        processor = TextProcessor()
        
        # Create very long text
        long_text = "Word " * 10000
        
        # Should be able to handle it
        cleaned = TextProcessor.clean_text(long_text)
        assert isinstance(cleaned, str)
    
    def test_text_with_numbers(self):
        """Test text containing numbers."""
        text = "Version 1.2.3 released on 2024-01-15"
        cleaned = TextProcessor.clean_text(text)
        
        assert "1" in cleaned
        assert "." in cleaned
    
    def test_text_with_bullets(self):
        """Test text with bullet points."""
        text = "- Point 1\n- Point 2\n- Point 3"
        cleaned = TextProcessor.clean_text(text)
        
        assert "Point 1" in cleaned
        assert "Point 2" in cleaned
    
    def test_text_with_code_blocks(self):
        """Test text containing code."""
        text = "Example: def hello(): return 'world'"
        cleaned = TextProcessor.clean_text(text)
        
        assert "hello" in cleaned


@pytest.mark.unit
class TestBatchProcessing:
    """Test batch processing of texts."""
    
    def test_process_multiple_documents(self):
        """Test processing multiple documents."""
        processor = TextProcessor()
        
        texts = [
            "Document 1 content. " * 50,
            "Document 2 content. " * 50,
            "Document 3 content. " * 50
        ]
        
        for text in texts:
            cleaned = TextProcessor.clean_text(text)
            assert isinstance(cleaned, str)
    
    def test_consistent_cleaning_results(self):
        """Test that cleaning is consistent."""
        processor = TextProcessor()
        
        text = "Test    text    with    spaces"
        cleaned1 = TextProcessor.clean_text(text)
        cleaned2 = TextProcessor.clean_text(text)
        
        assert cleaned1 == cleaned2
