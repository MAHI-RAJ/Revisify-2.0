"""Parser for DOC/DOCX documents"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DOCXParser:
    """Parser for Word documents using python-docx"""

    def __init__(self):
        self.supported_extensions = [".docx", ".doc"]

    def parse(self, filepath):
        """Extract text and paragraph blocks from DOCX"""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"DOCX file not found: {filepath}")

        if filepath.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Not a DOC/DOCX file: {filepath}")

        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")

        doc = Document(str(filepath))
        paragraphs = []
        full_text_parts = []

        for idx, para in enumerate(doc.paragraphs, start=1):
            text = para.text.strip()
            if text:
                paragraphs.append({"paragraph_number": idx, "text": text})
                full_text_parts.append(text)

        full_text = "\n\n".join(full_text_parts)

        return {
            "text": full_text,
            "pages": paragraphs,  # aligned key name for chunking
            "total_pages": len(paragraphs)
        }

