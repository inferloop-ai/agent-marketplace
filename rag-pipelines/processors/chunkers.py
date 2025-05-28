# rag-pipeline/processors/chunkers.py
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import re
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter
)
import nltk
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class BaseChunker(ABC):
    """Base class for text chunkers."""
    
    @abstractmethod
    async def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces."""
        pass

class RecursiveChunker(BaseChunker):
    """Recursive character text splitter."""
    
    async def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = splitter.split_text(text)
        
        result = []
        current_pos = 0
        
        for i, chunk in enumerate(chunks):
            start_pos = text.find(chunk, current_pos)
            end_pos = start_pos + len(chunk)
            
            result.append({
                'content': chunk,
                'start_char': start_pos,
                'end_char': end_pos,
                'chunk_index': i
            })
            
            current_pos = end_pos
        
        return result

class SemanticChunker(BaseChunker):
    """Semantic chunking based on sentence embeddings."""
    
    def __init__(self):
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Failed to load semantic model, falling back to simple chunking: {e}")
            self.model = None
    
    async def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        
        if not self.model:
            # Fallback to simple chunking
            return await RecursiveChunker().chunk_text(text, chunk_size, chunk_overlap)
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 1:
            return [{'content': text, 'start_char': 0, 'end_char': len(text), 'chunk_index': 0}]
        
        # Get sentence embeddings
        embeddings = self.model.encode(sentences)
        
        # Find semantic boundaries
        boundaries = self._find_semantic_boundaries(embeddings, sentences, chunk_size)
        
        # Create chunks based on boundaries
        chunks = []
        current_pos = 0
        
        for i, boundary in enumerate(boundaries):
            chunk_sentences = sentences[current_pos:boundary]
            chunk_text = ' '.join(chunk_sentences)
            
            start_char = text.find(chunk_sentences[0]) if chunk_sentences else 0
            end_char = start_char + len(chunk_text)
            
            chunks.append({
                'content': chunk_text,
                'start_char': start_char,
                'end_char': end_char,
                'chunk_index': i,
                'sentence_count': len(chunk_sentences)
            })
            
            # Apply overlap
            overlap_sentences = max(1, chunk_overlap // 100)  # Rough estimate
            current_pos = max(0, boundary - overlap_sentences)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            return nltk.sent_tokenize(text)
        except:
            # Simple fallback
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _find_semantic_boundaries(
        self, 
        embeddings: List, 
        sentences: List[str], 
        target_chunk_size: int
    ) -> List[int]:
        """Find optimal boundaries based on semantic similarity."""
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        boundaries = [0]
        current_chunk_size = 0
        last_boundary = 0
        
        for i in range(1, len(sentences)):
            current_chunk_size += len(sentences[i])
            
            # Check if we should create a boundary
            if current_chunk_size >= target_chunk_size:
                # Find the best boundary in the vicinity
                best_boundary = i
                min_similarity = float('inf')
                
                # Look at nearby sentences for semantic breaks
                start_search = max(last_boundary + 1, i - 3)
                end_search = min(len(sentences), i + 3)
                
                for j in range(start_search, end_search):
                    if j < len(embeddings) - 1:
                        similarity = cosine_similarity(
                            [embeddings[j]], [embeddings[j + 1]]
                        )[0][0]
                        
                        if similarity < min_similarity:
                            min_similarity = similarity
                            best_boundary = j + 1
                
                boundaries.append(best_boundary)
                last_boundary = best_boundary
                current_chunk_size = 0
        
        # Add final boundary
        if boundaries[-1] < len(sentences):
            boundaries.append(len(sentences))
        
        return boundaries

class FixedChunker(BaseChunker):
    """Fixed-size character chunking."""
    
    async def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to end at a word boundary
            if end < len(text):
                while end > start and text[end] not in [' ', '\n', '\t']:
                    end -= 1
                
                if end == start:  # No word boundary found
                    end = min(start + chunk_size, len(text))
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'content': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'chunk_index': chunk_index
                })
                chunk_index += 1
            
            # Move start position with overlap
            start = end - chunk_overlap
            if start <= 0:
                start = end
        
        return chunks

class DocumentBasedChunker(BaseChunker):
    """Document structure-based chunking (sections, paragraphs)."""
    
    async def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        
        # First try to split by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size, finalize current chunk
            if current_chunk and len(current_chunk) + len(paragraph) > chunk_size:
                chunks.append({
                    'content': current_chunk.strip(),
                    'start_char': current_start,
                    'end_char': current_start + len(current_chunk),
                    'chunk_index': chunk_index
                })
                
                chunk_index += 1
                current_start += len(current_chunk)
                current_chunk = ""
            
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
        
        # Add final chunk if it exists
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'start_char': current_start,
                'end_char': current_start + len(current_chunk),
                'chunk_index': chunk_index
            })
        
        return chunks

class ChunkerFactory:
    """Factory for creating chunkers."""
    
    def __init__(self):
        self.chunkers = {
            'fixed': FixedChunker(),
            'recursive': RecursiveChunker(),
            'semantic': SemanticChunker(),
            'document_based': DocumentBasedChunker()
        }
    
    def get_chunker(self, strategy: str) -> BaseChunker:
        """Get appropriate chunker for strategy."""
        chunker = self.chunkers.get(strategy.lower())
        
        if not chunker:
            logger.warning(f"Unknown chunking strategy {strategy}, using recursive")
            chunker = self.chunkers['recursive']
        
        return chunker

# rag-pipeline/embeddings/embedding_manager.py
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from ..config import settings

logger = logging.getLogger(__name__)

class BaseEmbeddingModel(ABC):
    """Base class for embedding models."""
    
    @abstractmethod
    async def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        pass

class SentenceTransformerEmbedding(BaseEmbeddingModel):
    """Sentence Transformers embedding model."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._dimension = None
    
    def _load_model(self):
        """Lazy load the model."""
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name)
                self._dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Loaded SentenceTransformer model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise
    
    async def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings."""
        self._load_model()
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            self._load_model()
        return self._dimension

class OpenAIEmbedding(BaseEmbeddingModel):
    """OpenAI embedding model."""
    
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        self.model_name = model_name
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self._dimension = 1536  # ada-002 dimension
    
    async def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings."""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            # Process in batches to avoid rate limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to encode texts with OpenAI: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

class EmbeddingManager:
    """Manages different embedding models."""
    
    def __init__(self):
        self.models = {}
        self.default_model = None
    
    def register_model(self, name: str, model: BaseEmbeddingModel):
        """Register an embedding model."""
        self.models[name] = model
        if self.default_model is None:
            self.default_model = name
    
    def get_model(self, name: Optional[str] = None) -> BaseEmbeddingModel:
        """Get embedding model by name."""
        if name is None:
            name = self.default_model
            
        if name not in self.models:
            raise ValueError(f"Embedding model {name} not found")
        
        return self.models[name]
    
    async def encode_texts(
        self, 
        texts: List[str], 
        model_name: Optional[str] = None
    ) -> List[List[float]]:
        """Encode texts using specified model."""
        model = self.get_model(model_name)
        return await model.encode(texts)

# Global embedding manager
embedding_manager = EmbeddingManager()

# Register default models
embedding_manager.register_model(
    "sentence-transformers", 
    SentenceTransformerEmbedding(settings.embedding_model)
)

if settings.openai_api_key:
    embedding_manager.register_model("openai", OpenAIEmbedding())

# rag-pipeline/vector_stores/qdrant_store.py
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from ..config import settings
from ..models import DocumentChunk, SearchResult

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    """Qdrant vector database implementation."""
    
    def __init__(self):
        self.client = None
        self.async_client = None
    
    async def connect(self):
        """Connect to Qdrant."""
        try:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=30
            )
            
            # Test connection
            collections = self.client.get_collections()
            logger.info(f"Connected to Qdrant successfully. Collections: {len(collections.collections)}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
    
    async def create_collection(
        self, 
        collection_name: str, 
        vector_size: int = 1536,
        distance: str = "Cosine"
    ):
        """Create a new collection."""
        try:
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclidean": Distance.EUCLID,
                "Dot": Distance.DOT
            }
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, Distance.COSINE)
                )
            )
            
            logger.info(f"Created collection: {collection_name}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Collection {collection_name} already exists")
            else:
                logger.error(f"Failed to create collection {collection_name}: {e}")
                raise
    
    async def add_chunks(
        self, 
        collection_name: str, 
        chunks: List[DocumentChunk], 
        embeddings: List[List[float]]
    ):
        """Add document chunks to collection."""
        try:
            points = []
            
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=str(chunk.id),
                    vector=embedding,
                    payload={
                        "document_id": str(chunk.document_id),
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "word_count": chunk.word_count,
                        "char_count": chunk.char_count,
                        "page_number": chunk.page_number,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char
                    }
                )
                points.append(point)
            
            # Insert points in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
            
            logger.info(f"Added {len(chunks)} chunks to collection {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to add chunks to collection {collection_name}: {e}")
            raise
    
    async def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar chunks."""
        try:
            # Build filters
            query_filter = None
            if filters:
                conditions = []
                
                for key, value in filters.items():
                    if isinstance(value, list):
                        conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchAny(any=value)
                            )
                        )
                    else:
                        conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchValue(value=value)
                            )
                        )
                
                if conditions:
                    query_filter = models.Filter(must=conditions)
            
            # Perform search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter,
                with_payload=True
            )
            
            # Convert to SearchResult objects
            results = []
            for result in search_results:
                payload = result.payload
                
                search_result = SearchResult(
                    chunk_id=UUID(result.id),
                    document_id=UUID(payload["document_id"]),
                    content=payload["content"],
                    score=result.score,
                    filename=payload.get("filename", ""),
                    page_number=payload.get("page_number"),
                    chunk_index=payload["chunk_index"],
                    tags=payload.get("tags", []),
                    category=payload.get("category"),
                    author=payload.get("author")
                )
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search collection {collection_name}: {e}")
            raise
    
    async def delete_document(self, collection_name: str, document_id: UUID):
        """Delete all chunks for a document."""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=str(document_id))
                            )
                        ]
                    )
                )
            )
            
            logger.info(f"Deleted chunks for document {document_id} from collection {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            info = self.client.get_collection(collection_name)
            
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "status": info.status
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {e}")
            raise
    
    async def list_collections(self) -> List[str]:
        """List all collections."""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise

# rag-pipeline/main.py
import time
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import (
    DocumentUpload, DocumentResponse, SearchRequest, SearchResponse,
    ProcessingJob, CollectionInfo, HealthResponse, ErrorResponse
)
from .processors.document_processor import DocumentProcessor
from .embeddings.embedding_manager import embedding_manager
from .vector_stores.qdrant_store import QdrantVectorStore

# Setup logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Global instances
document_processor = DocumentProcessor()
vector_store = QdrantVectorStore()
processing_jobs: Dict[UUID, ProcessingJob] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    logger.info("🚀 Starting RAG Pipeline Server...")
    
    try:
        await vector_store.connect()
        logger.info("✅ Vector store connected")
        
        app.state.start_time = time.time()
        logger.info("✅ RAG Pipeline Server started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start RAG Pipeline Server: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down RAG Pipeline Server...")
    logger.info("✅ RAG Pipeline Server shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="RAG Pipeline Server",
    description="Comprehensive Retrieval-Augmented Generation pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check vector store connection
        collections = await vector_store.list_collections()
        
        # Calculate uptime
        uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime=uptime,
            vector_store_connected=True,
            database_connected=True,
            redis_connected=True,
            total_documents=0,  # TODO: Implement actual count
            total_chunks=0,     # TODO: Implement actual count
            active_jobs=len([job for job in processing_jobs.values() if job.status == "processing"])
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Document upload and processing
@app.post("/documents", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    collection_name: str = Form(...),
    chunking_strategy: str = Form("recursive"),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    tags: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    author: Optional[str] = Form(None)
):
    """Upload and process a document."""
    try:
        # Validate file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Generate IDs
        document_id = uuid4()
        job_id = uuid4()
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Create processing job
        job = ProcessingJob(
            id=job_id,
            document_id=document_id,
            collection_name=collection_name,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        processing_jobs[job_id] = job
        
        # Custom metadata
        custom_metadata = {
            "tags": tag_list,
            "category": category,
            "source": source,
            "author": author
        }
        
        # Start background processing
        background_tasks.add_task(
            process_document_task,
            file,
            document_id,
            job_id,
            custom_metadata
        )
        
        return DocumentResponse(
            document_id=document_id,
            filename=file.filename,
            status="processing",
            metadata=None,  # Will be set after processing
            job_id=job_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_document_task(
    file: UploadFile,
    document_id: UUID,
    job_id: UUID,
    custom_metadata: Dict[str, Any]
):
    """Background task to process document."""
    job = processing_jobs.get(job_id)
    if not job:
        logger.error(f"Processing job {job_id} not found")
        return
    
    try:
        # Update job status
        job.status = "processing"
        job.started_at = time.time()
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        metadata, chunks = await document_processor.process_document(
            file_content,
            file.filename,
            document_id,
            job.chunking_strategy,
            job.chunk_size,
            job.chunk_overlap,
            custom_metadata
        )
        
        # Generate embeddings
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_manager.encode_texts(chunk_texts)
        
        # Ensure collection exists
        await vector_store.create_collection(
            collection_name=job.collection_name,
            vector_size=len(embeddings[0]) if embeddings else 1536
        )
        
        # Store in vector database
        await vector_store.add_chunks(job.collection_name, chunks, embeddings)
        
        # Update job
        job.status = "completed"
        job.completed_at = time.time()
        job.total_chunks = len(chunks)
        job.processed_chunks = len(chunks)
        
        logger.info(f"Successfully processed document {document_id}: {len(chunks)} chunks")
        
    except Exception as e:
        logger.error(f"Failed to process document {document_id}: {e}")
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = time.time()

# Search endpoints
@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search documents using RAG pipeline."""
    try:
        start_time = time.time()
        
        # Generate query embedding
        query_embeddings = await embedding_manager.encode_texts([request.query])
        query_embedding = query_embeddings[0]
        
        # Build filters
        filters = {}
        if request.filters:
            filters.update(request.filters)
        if request.tags:
            filters["tags"] = request.tags
        if request.category:
            filters["category"] = request.category
        
        # Perform vector search
        results = await vector_store.search(
            collection_name=request.collection_name,
            query_embedding=query_embedding,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            filters=filters if filters else None
        )
        
        search_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time,
            collection_name=request.collection_name,
            top_k=request.top_k,
            hybrid_search_used=False,  # TODO: Implement hybrid search
            reranking_used=False       # TODO: Implement reranking
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Collection management
@app.get("/collections", response_model=List[str])
async def list_collections():
    """List all collections."""
    try:
        return await vector_store.list_collections()
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}", response_model=CollectionInfo)
async def get_collection_info(collection_name: str):
    """Get information about a collection."""
    try:
        info = await vector_store.get_collection_info(collection_name)
        
        return CollectionInfo(
            name=collection_name,
            document_count=0,  # TODO: Implement actual count
            chunk_count=info.get("points_count", 0),
            total_size_bytes=0,  # TODO: Implement actual size
            created_at=datetime.now(),  # TODO: Store actual creation time
            updated_at=datetime.now(),
            embedding_model=settings.embedding_model,
            vector_store="qdrant",
            avg_chunk_size=0.0,  # TODO: Calculate actual average
            languages=[],
            categories=[],
            tags=[]
        )
        
    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Job status
@app.get("/jobs/{job_id}", response_model=ProcessingJob)
async def get_job_status(job_id: UUID):
    """Get processing job status."""
    job = processing_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )