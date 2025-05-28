# rag-pipeline/README.md
# RAG Pipeline System

A comprehensive Retrieval-Augmented Generation (RAG) pipeline system for processing, indexing, and retrieving documents for AI agents.

## Features

- **Multi-format Document Processing**: PDF, DOCX, TXT, HTML, Markdown
- **Advanced Chunking**: Semantic and recursive text splitting
- **Vector Storage**: Support for Qdrant, Chroma, Pinecone, Weaviate
- **Multiple Embeddings**: OpenAI, HuggingFace, Local models
- **Hybrid Search**: Vector + BM25 search combination
- **Document Metadata**: Rich metadata extraction and filtering
- **Async Processing**: High-performance async operations
- **API Interface**: RESTful API for easy integration
- **Monitoring**: Built-in metrics and health checks

## Installation

```bash
cd rag-pipeline
pip install -r requirements.txt
```

## Quick Start

1. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Start vector database (Qdrant):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

3. Run the RAG pipeline server:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8090 --reload
```

4. Upload and process documents:
```bash
curl -X POST "http://localhost:8090/documents" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.pdf" \
  -F "collection_name=my_docs"
```

5. Search documents:
```bash
curl -X POST "http://localhost:8090/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "collection_name": "my_docs"}'
```

## API Documentation

Visit `http://localhost:8090/docs` for interactive API documentation.




