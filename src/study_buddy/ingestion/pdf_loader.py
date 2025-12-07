import pdfplumber
import re
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PDFLoader:
    """Handles PDF loading and preprocessing"""
    
    def __init__(self):
        self.supported_extensions = [".pdf"]
    
    def load_pdf(self, pdf_path: str | Path) -> str:
        """
        Load and extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted and preprocessed text
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a PDF
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if pdf_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be a PDF. Got: {pdf_path.suffix}")
        
        logger.info(f"Loading PDF: {pdf_path}")
        
        text_content = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    
                    if page_text:
                        # Add page marker for better context
                        text_content.append(f"[Page {page_num}]\n{page_text}")
                    else:
                        logger.warning(f"No text extracted from page {page_num}")
        
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {e}")
            raise
        
        if not text_content:
            raise ValueError("No text could be extracted from the PDF")
        
        full_text = "\n\n".join(text_content)
        
        # Preprocess the text
        preprocessed_text = self.preprocess_text(full_text)
        
        logger.info(f"Successfully loaded PDF with {len(preprocessed_text)} characters")
        
        return preprocessed_text
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess extracted text to improve quality.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and preprocessed text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove standalone page numbers that appear after [Page X] markers
        text = re.sub(r'(\[Page \d+\])\s*\d+\s*', r'\1 ', text)
        
        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('–', '-')
        text = text.replace('—', '-')
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove excessive newlines but preserve paragraph structure
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_pdf_metadata(self, pdf_path: str | Path) -> Dict[str, Optional[str]]:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        pdf_path = Path(pdf_path)
        metadata = {
            "filename": pdf_path.name,
            "title": None,
            "author": None,
            "subject": None,
            "creator": None,
            "producer": None,
            "num_pages": 0
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata["num_pages"] = len(pdf.pages)
                
                # Extract PDF metadata
                if pdf.metadata:
                    metadata["title"] = pdf.metadata.get("Title")
                    metadata["author"] = pdf.metadata.get("Author")
                    metadata["subject"] = pdf.metadata.get("Subject")
                    metadata["creator"] = pdf.metadata.get("Creator")
                    metadata["producer"] = pdf.metadata.get("Producer")
        
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {e}")
        
        return metadata
