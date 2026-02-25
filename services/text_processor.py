import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class TextProcessor:
    """Service responsible for cleaning and processing text."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        # Remove excessive whitespace
        text = re.sub(r" +", " ", text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s.,;:!?()-]", "", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    # @staticmethod
    # def create_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    #     """
    #     Split text into chunks with overlap.

    #     Args:
    #         text: Text to chunk
    #         chunk_size: Maximum size of each chunk in characters
    #         overlap: Number of characters to overlap between chunks

    #     Returns:
    #         List of text chunks
    #     """
    #     if not text:
    #         return []

    #         # PEHLE CHECK KARO document size
    #     if len(text) > 10_000_000:  # 10MB se bara
    #         logger.warning(f"Text too large ({len(text)} chars), truncating...")
    #         text = text[:10_000_000]

    #     chunks = []
    #     start = 0
    #     text_length = len(text)

    #     while start < text_length:
    #         end = start + chunk_size

    #         # Find the last sentence boundary within the chunk
    #         if end < text_length:
    #             # Look for sentence endings
    #             for boundary in ['. ', '! ', '? ', '\n']:
    #                 last_boundary = text.rfind(boundary, start, end)
    #                 if last_boundary != -1:
    #                     end = last_boundary + 1
    #                     break

    #         chunk = text[start:end].strip()
    #         if chunk:
    #             chunks.append(chunk)

    #         # Move start position with overlap
    #         start = end - overlap if end < text_length else end

    #     logger.info(f"Created {len(chunks)} chunks from text")
    #     return chunks

    # text_processor.py me PURA create_chunks replace karo:

    # text_processor.py me PURA create_chunks replace karo:

    # @staticmethod
    # def create_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    #     """Split text into chunks with overlap."""
    #     if not text:
    #         return []

    #     # Size check
    #     text_length = len(text)
    #     logger.info(f"Processing text of length: {text_length:,} characters")

    #     # Agar 5MB se bara to skip karo
    #     if text_length > 5_000_000:
    #         logger.error(f"Text too large ({text_length:,} chars), skipping...")
    #         return []

    #     chunks = []
    #     start = 0
    #     max_chunks = 50000  # Safety limit

    #     while start < text_length and len(chunks) < max_chunks:
    #         end = min(start + chunk_size, text_length)

    #         if end < text_length:
    #             for boundary in ['. ', '! ', '? ', '\n']:
    #                 last_boundary = text.rfind(boundary, start, end)
    #                 if last_boundary != -1 and last_boundary > start:
    #                     end = last_boundary + 1
    #                     break

    #         chunk = text[start:end].strip()
    #         if chunk:
    #             chunks.append(chunk)

    #         start = end - overlap if end < text_length else end

    #         # Infinite loop protection
    #         if start <= end - chunk_size - overlap:
    #             break

    #     logger.info(f"Created {len(chunks)} chunks")
    #     return chunks

    @staticmethod
    def create_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into chunks with overlap."""
        if not text:
            return []

        text_length = len(text)
        logger.info(f"Text length: {text_length:,} characters")

        chunks = []
        start = 0
        iteration_count = 0  # DEBUG

        while start < text_length:
            iteration_count += 1

            # SAFETY CHECK
            if iteration_count > 1000:
                logger.error(f"Too many iterations! Breaking at {len(chunks)} chunks")
                break

            end = min(start + chunk_size, text_length)

            # Sentence boundary
            if end < text_length:
                for boundary in [". ", "! ", "? ", "\n"]:
                    last_boundary = text.rfind(boundary, start, end)
                    if last_boundary > start:
                        end = last_boundary + 1
                        break

            chunk = text[start:end].strip()
            if chunk and len(chunk) > 10:
                chunks.append(chunk)
                logger.debug(f"Chunk {len(chunks)}: start={start}, end={end}")  # DEBUG

            # Move forward
            start = end - overlap if overlap < end - start else end

            if start < 0 or start >= text_length:
                break

        logger.info(f"Created {len(chunks)} chunks in {iteration_count} iterations")
        return chunks

    def process_document(
        self, content: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[str]:
        """
        Process a document: clean and chunk it.

        Args:
            content: Raw document content
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of processed text chunks
        """
        cleaned_text = self.clean_text(content)
        chunks = self.create_chunks(cleaned_text, chunk_size, overlap)
        return chunks
