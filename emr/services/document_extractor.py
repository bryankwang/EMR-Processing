import json
import PyPDF2
from typing import Optional, Dict, Any, Union
import os

class DocumentExtractor:
    """Handles extraction of content from both PDF and JSON files for GPT processing."""
    
    @staticmethod
    def extract_content(file_path: str) -> Optional[str]:
        """
        Extract content from either a PDF or JSON file and convert to string for GPT processing.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Extracted content as string (text for PDFs, JSON string for JSON files)
            None: If extraction fails
        """
        try:
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return DocumentExtractor._extract_pdf(file_path)
            elif file_ext == '.json':
                return DocumentExtractor._extract_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            # Log the error
            print(f"Error extracting content from {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_pdf(pdf_path: str) -> Optional[str]:
        """
        Extract text content from a PDF file.
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting PDF content: {str(e)}")
            return None
    
    @staticmethod
    def _extract_json(json_path: str) -> Optional[str]:
        """
        Extract content from a JSON file and convert to string for GPT processing.
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                content = json.load(file)
                # Convert JSON to formatted string for GPT processing
                return json.dumps(content, indent=2)
        except Exception as e:
            print(f"Error extracting JSON content: {str(e)}")
            return None