# rag-pipeline/.env.example
# RAG Pipeline Configuration

# Server
RAG_HOST=0.0.0.0
RAG_PORT=8090
RAG_DEBUG=true

# Vector Database (Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_SIZE=1536
QDRANT_DISTANCE=Cosine

# Alternative Vector Databases
CHROMA_PERSIST_DIRECTORY=./chroma_db
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
WEAVIATE_URL=http://localhost:8080

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
HUGGINGFACE_API_KEY=

# Document Processing
MAX_FILE_SIZE=50MB
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
ENABLE_OCR=false
OCR_LANGUAGE=eng

# Search & Retrieval
DEFAULT_TOP_K=5
HYBRID_SEARCH_ALPHA=0.5
ENABLE_RERANKING=true
RERANK_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_pipeline
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=

# Processing
MAX_WORKERS=4
BATCH_SIZE=32
ENABLE_ASYNC=true

