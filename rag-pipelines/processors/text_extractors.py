# rag-pipeline/processors/text_extractors.py
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, BinaryIO
import PyPDF2
import docx
from bs4 import BeautifulSoup
import json
import csv
import io

logger = logging.getLogger(__name__)

class BaseTextExtractor(ABC):
    """Base class for text extractors."""
    
    @abstractmethod
    async def extract(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        """Extract text and metadata from file."""
        pass

class PDFExtractor(BaseTextExtractor):
    """Extract text from PDF files."""
    
    async def extract(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        try:
            pdf_reader = PyPDF2.PdfReader(file_content)
            
            text_content = []
            metadata = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text_content.append(page_text)
                metadata.append({
                    'page_number': page_num + 1,
                    'char_count': len(page_text),
                    'word_count': len(page_text.split())
                })
            
            full_text = '\n\n'.join(text_content)
            
            return {
                'content': full_text,
                'page_count': len(pdf_reader.pages),
                'word_count': len(full_text.split()),
                'metadata': {
                    'pages': metadata,
                    'pdf_metadata': pdf_reader.metadata._get_object() if pdf_reader.metadata else {}
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {filename}: {e}")
            raise

class DOCXExtractor(BaseTextExtractor):
    """Extract text from DOCX files."""
    
    async def extract(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        try:
            doc = docx.Document(file_content)
            
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            
            full_text = '\n\n'.join(paragraphs)
            
            # Extract document properties
            doc_props = {}
            if doc.core_properties:
                doc_props = {
                    'title': doc.core_properties.title,
                    'author': doc.core_properties.author,
                    'subject': doc.core_properties.subject,
                    'created': str(doc.core_properties.created) if doc.core_properties.created else None,
                    'modified': str(doc.core_properties.modified) if doc.core_properties.modified else None
                }
            
            return {
                'content': full_text,
                'word_count': len(full_text.split()),
                'metadata': {
                    'paragraph_count': len(paragraphs),
                    'document_properties': doc_props
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX {filename}: {e}")
            raise

class PlainTextExtractor(BaseTextExtractor):
    """Extract text from plain text files."""
    
    async def extract(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        try:
            content = file_content.read().decode('utf-8', errors='ignore')
            
            return {
                'content': content,
                'word_count': len(content.split()),
                'metadata': {
                    'line_count': len(content.splitlines()),
                    'char_count': len(content)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from plain text {filename}: {e}")
            raise

class HTMLExtractor(BaseTextExtractor):
    """Extract text from HTML files."""
    
    async def extract(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        try:
            content = file_content.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract metadata
            title = soup.find('title')
            meta_description = soup.find('meta', attrs={'name': 'description'})
            
            return {
                'content': text,
                'word_count': len(text.split()),
                'metadata': {
                    'title': title.string if title else None,
                    'description': meta_description.get('content') if meta_description else None,
                    'html_structure': {
                        'headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                        'paragraphs': len(soup.find_all('p')),
                        'links': len(soup.find_all('a')),
                        'images': len(soup.find_all('img'))
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from HTML {filename}: {e}")
            raise

class JSONExtractor(BaseTextExtractor):
    """Extract text from JSON files."""
    
    async def extract(self, file_content: BinaryIO, filename: str) -> Dict[str, Any]:
        try:
            content = file_content.read().decode('utf-8', errors='ignore')
            data = json.loads(content)
            
            # Convert JSON to readable text
            text = self._json_to_text(data)
            
            return {
                'content': text,
                'word_count': len(text.split()),
                'metadata': {
                    'json_structure': self._analyze_json_structure(data),
                    'total_keys': self._count_keys(data)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from JSON {filename}: {e}")
            raise
    
    def _json_to_text(self, data: Any, level: int = 0) -> str:
        """Convert JSON data to readable text."""
        lines = []
        indent = "  " * level
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent}{key}:")
                    lines.append(self._json_to_text(value, level + 1))
                else:
                    lines.append(f"{indent}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                lines.append(f"{indent}Item {i + 1}:")
                lines.append(self._json_to_text(item, level + 1))
        else:
            lines.append(f"{indent}{data}")
        
        return '\n'.join(lines)
    
    def _analyze_json_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze JSON structure."""
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': len(data),
                'nested_objects': sum(1 for v in data.values() if isinstance(v, dict)),
                'arrays': sum(1 for v in data.values() if isinstance(v, list))
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'item_types': list(set(type(item).__name__ for item in data))
            }
        else:
            return {'type': type(data).__name__}
    
    def _count_keys(self, data: Any) -> int:
        """Count total number of keys in nested structure."""
        if isinstance(data, dict):
            return len(data) + sum(self._count_keys(v) for v in data.values())
        elif isinstance(data, list):
            return sum(self._count_keys(item) for item in data)
        else:
            return 0

class TextExtractorFactory:
    """Factory for creating text extractors."""
    
    def __init__(self):
        self.extractors = {
            'application/pdf': PDFExtractor(),
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DOCXExtractor(),
            'application/msword': DOCXExtractor(),
            'text/plain': PlainTextExtractor(),
            'text/markdown': PlainTextExtractor(),
            'text/html': HTMLExtractor(),
            'application/json': JSONExtractor(),
            'text/csv': PlainTextExtractor(),
        }
    
    def get_extractor(self, file_type: str) -> BaseTextExtractor:
        """Get appropriate extractor for file type."""
        extractor = self.extractors.get(file_type)
        
        if not extractor:
            # Default to plain text for unknown types
            logger.warning(f"No specific extractor for {file_type}, using plain text")
            extractor = self.extractors['text/plain']
        
        return extractor