# rag-pipeline/processors/document_processor.py
import logging
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, BinaryIO
from uuid import UUID

from ..models import DocumentMetadata, DocumentChunk, ChunkingStrategy
from .text_extractors import TextExtractorFactory
from .chunkers import ChunkerFactory
from ..config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing orchestrator."""
    
    def __init__(self):
        self.text_extractor_factory = TextExtractorFactory()
        self.chunker_factory = ChunkerFactory()
    
    async def process_document(
        self,
        file_content: BinaryIO,
        filename: str,
        document_id: UUID,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[DocumentMetadata, List[DocumentChunk]]:
        """Process a document and return metadata and chunks."""
        
        try:
            # Detect file type
            file_type = self._detect_file_type(filename, file_content)
            file_size = len(file_content.read())
            file_content.seek(0)  # Reset file pointer
            
            logger.info(f"Processing document: {filename} ({file_type}, {file_size} bytes)")
            
            # Extract text content
            text_extractor = self.text_extractor_factory.get_extractor(file_type)
            extracted_data = await text_extractor.extract(file_content, filename)
            
            # Create document metadata
            metadata = DocumentMetadata(
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                page_count=extracted_data.get('page_count'),
                word_count=extracted_data.get('word_count'),
                language=extracted_data.get('language'),
                tags=custom_metadata.get('tags', []) if custom_metadata else [],
                category=custom_metadata.get('category') if custom_metadata else None,
                source=custom_metadata.get('source') if custom_metadata else None,
                author=custom_metadata.get('author') if custom_metadata else None,
                chunking_strategy=chunking_strategy
            )
            
            # Chunk the text
            chunker = self.chunker_factory.get_chunker(chunking_strategy)
            chunks = await chunker.chunk_text(
                text=extracted_data['content'],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                metadata=extracted_data.get('metadata', {})
            )
            
            # Create DocumentChunk objects
            document_chunks = []
            for i, chunk_data in enumerate(chunks):
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=i,
                    content=chunk_data['content'],
                    start_char=chunk_data.get('start_char'),
                    end_char=chunk_data.get('end_char'),
                    page_number=chunk_data.get('page_number'),
                    word_count=len(chunk_data['content'].split()),
                    char_count=len(chunk_data['content']),
                    previous_chunk=chunks[i-1]['content'][:100] + "..." if i > 0 else None,
                    next_chunk=chunks[i+1]['content'][:100] + "..." if i < len(chunks)-1 else None
                )
                document_chunks.append(chunk)
            
            # Update metadata with chunk info
            metadata.chunk_count = len(document_chunks)
            
            logger.info(f"Document processed successfully: {len(document_chunks)} chunks created")
            
            return metadata, document_chunks
            
        except Exception as e:
            logger.error(f"Failed to process document {filename}: {e}")
            raise
    
    def _detect_file_type(self, filename: str, file_content: BinaryIO) -> str:
        """Detect file type from filename and content."""
        # First try to get MIME type from filename
        mime_type, _ = mimetypes.guess_type(filename)
        
        if mime_type:
            return mime_type
        
        # Fallback to file extension
        extension = Path(filename).suffix.lower()
        
        extension_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.ppt': 'application/vnd.ms-powerpoint'
        }
        
        return extension_map.get(extension, 'application/octet-stream')
