import os
from typing import List, Generator
from pathlib import Path
from docx import Document
import logging

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Service responsible for loading documents from the file system."""

    def __init__(self, base_path: str):
        """
        Initialize the document loader.

        Args:
            base_path: Root directory path to search for documents
        """
        self.base_path = Path(base_path)

        if not self.base_path.exists():
            raise ValueError(f"Path does not exist: {base_path}")

        if not self.base_path.is_dir():
            raise ValueError(f"Path is not a directory: {base_path}")

    def find_all_docx_files(self) -> List[Path]:
        """
        Recursively find all .docx files in the base path.

        Returns:
            List of Path objects pointing to .docx files
        """
        docx_files = []

        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".docx") and not file.startswith("~$"):
                    file_path = Path(root) / file
                    docx_files.append(file_path)

        logger.info(f"Found {len(docx_files)} .docx files")
        return docx_files

    def load_document(self, file_path: Path) -> str:
        """
        Load and extract text from a single .docx file.

        Args:
            file_path: Path to the .docx file

        Returns:
            Extracted text content
        """
        try:
            doc = Document(file_path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs]
            text = "\n".join(paragraphs)
            logger.info(f"Successfully loaded: {file_path.name}")
            return text
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return ""

    def load_all_documents(self) -> Generator[tuple[str, str], None, None]:
        """
        Load all documents from the base path.

        Yields:
            Tuple of (file_path, content)
        """
        docx_files = self.find_all_docx_files()

        for file_path in docx_files:
            content = self.load_document(file_path)
            if content:
                yield str(file_path), content
