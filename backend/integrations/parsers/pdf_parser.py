from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    """Parser for PDF documents"""
    
    def __init__(self):
        self.supported_extensions = [".pdf"]
    
    def parse(self, filepath):
        """
        Extract text from PDF file
        
        Args:
            filepath: Path to PDF file
        
        Returns:
            Dict with 'text' (str) and 'pages' (list of page dicts with 'page_number' and 'text')
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"PDF file not found: {filepath}")
        
        if filepath.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {filepath}")
        
        try:
            # Try pdfplumber first (better for tables and structured content)
            return self._parse_with_pdfplumber(filepath)
        except ImportError:
            try:
                # Fallback to pypdf
                return self._parse_with_pypdf(filepath)
            except ImportError:
                raise ImportError(
                    "No PDF parser available. Install one with: "
                    "pip install pdfplumber OR pip install pypdf"
                )
    
    def _parse_with_pdfplumber(self, filepath):
        """Parse PDF using pdfplumber"""
        try:
            import pdfplumber
            
            full_text = ""
            pages_data = []
            
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        full_text += f"\n\n--- Page {page_num} ---\n\n{text}"
                        pages_data.append({
                            "page_number": page_num,
                            "text": text
                        })
            
            return {
                "text": full_text.strip(),
                "pages": pages_data,
                "total_pages": len(pages_data)
            }
        except Exception as e:
            logger.error(f"pdfplumber parsing error: {str(e)}")
            raise
    
    def _parse_with_pypdf(self, filepath):
        """Parse PDF using pypdf (fallback)"""
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(filepath)
            full_text = ""
            pages_data = []
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text:
                    full_text += f"\n\n--- Page {page_num} ---\n\n{text}"
                    pages_data.append({
                        "page_number": page_num,
                        "text": text
                    })
            
            return {
                "text": full_text.strip(),
                "pages": pages_data,
                "total_pages": len(pages_data)
            }
        except Exception as e:
            logger.error(f"pypdf parsing error: {str(e)}")
            raise
    
    def is_scanned(self, filepath):
        """
        Check if PDF is scanned (image-based, requires OCR)
        
        Args:
            filepath: Path to PDF file
        
        Returns:
            bool: True if PDF appears to be scanned
        """
        try:
            import pdfplumber
            
            with pdfplumber.open(filepath) as pdf:
                # Check first few pages
                for page in pdf.pages[:3]:
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        return False  # Has extractable text
                return True  # No extractable text, likely scanned
        except:
            # If pdfplumber not available, assume not scanned
            return False
    
    def extract_metadata(self, filepath):
        """Extract PDF metadata"""
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(filepath)
            metadata = reader.metadata or {}
            
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "total_pages": len(reader.pages)
            }
        except:
            return {}

