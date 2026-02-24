# RAG Service - Project Summary

## What You're Getting

A complete, production-ready RAG (Retrieval-Augmented Generation) chatbot backend service with the following components:

### Core Features
✅ **Document Processing**: Recursively scans directories for .docx files
✅ **Text Cleaning**: Advanced preprocessing and normalization
✅ **Smart Chunking**: 500-character chunks with 50-character overlap
✅ **OpenAI Embeddings**: Uses `text-embedding-3-large` (best quality)
✅ **Vector Database**: Supabase with pgvector for fast similarity search
✅ **RAG Pipeline**: Context-aware responses using GPT-4
✅ **FastAPI**: Modern REST API with auto-generated docs
✅ **Streaming Support**: Real-time response streaming
✅ **Professional Architecture**: Follows SOLID principles and SRP throughout

## Project Structure

```
rag-service/
├── config/               # Configuration management
│   ├── settings.py      # Pydantic settings with .env support
│   └── __init__.py
├── models/              # Data models
│   ├── schemas.py       # Pydantic request/response models
│   └── __init__.py
├── services/            # Business logic (SRP compliant)
│   ├── document_loader.py    # Loads .docx files from directories
│   ├── text_processor.py     # Cleans and chunks text
│   ├── embedding_service.py  # OpenAI embedding creation
│   ├── vector_store.py       # Supabase vector operations
│   ├── rag_service.py        # RAG pipeline orchestration
│   ├── auth_service.py       # Authentication Rout Services
│   └── __init__.py
├── scripts/             # Utility scripts
│   ├── index_documents.py    # One-time document indexing
│   └── __init__.py
├── main.py              # FastAPI application entry point
│── auth_routes.py        # fastapi authentication Routes
├── example_usage.py     # Example Python client
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── supabase_setup.sql  # Database schema and functions
├── .gitignore          # Git ignore patterns
├── README.md           # Comprehensive documentation
├── QUICKSTART.md       # 5-minute setup guide
└── DEPLOYMENT.md       # Production deployment guide
```

## Architecture Highlights

### Single Responsibility Principle (SRP)
Each service class has one clear responsibility:
- `DocumentLoader`: Only handles file system operations
- `TextProcessor`: Only handles text cleaning and chunking
- `EmbeddingService`: Only handles OpenAI embedding creation
- `VectorStore`: Only handles Supabase operations
- `RAGService`: Only handles response generation
- `AuthService`: Only handles Authentication

### Clean Code Practices
- Type hints throughout
- Comprehensive docstrings
- Error handling at every level
- Logging for debugging and monitoring
- Configuration via environment variables
- No hardcoded values

## What You Need to Provide

1. **OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys
   - Add to `.env` file

2. **Supabase Project**
   - Create at: https://supabase.com
   - Run the provided SQL setup script
   - Add URL and key to `.env` file

3. **Documents Path**
   - Path to folder containing .docx files
   - Add to `.env` file as `DOCUMENTS_PATH`

That's it! Everything else is included.

## Authentication Endpoint

Post / Signup
Post / Login
Post / Refresh
Get /  Auth-me
Post / Forgot-Password
Post / Reset Password
Post / Change-Password

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns service status and version.

### 2. Indexing-documents (Embeding start from path Docs)
```
Post /Indexing-docs
```
store all embeding into a supabase.

### 3. upload-documents
```
Post /Upload Docs
```
upload a single docs convert into embeding and store into a supabase.

### 2. Chat (Standard)
```
POST /chat
Body: {
  "query": "Your question here",
  "top_k": 5,
  "similarity_threshold": 0.5
}
```
Returns complete answer with sources.

### 3. Chat (Streaming)
```
POST /chat/stream
Body: {
  "query": "Your question here",
  "top_k": 5
}
```
Returns streaming text response.

### Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Start (3 Steps)

1. **Setup**
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

2. **Run SQL Setup**
- Open Supabase SQL Editor
- Paste contents of `supabase_setup.sql`
- Execute

3. **Start**
```bash

uvicorn main:app --reload           # Start the API
```

Visit http://localhost:8000/docs to test!

## Key Features Explained

### Document Indexing
1. Scans directories recursively for .docx files
2. Extracts text from each document
3. Cleans and normalizes the text
4. Splits into 500-character chunks with 50-char overlap
5. Creates embeddings using OpenAI
6. Stores in Supabase with metadata

### Query Processing
1. User sends a question
2. Create embedding for the question
3. Search Supabase for similar chunks (cosine similarity)
4. Retrieve top K most similar chunks
5. Pass chunks as context to GPT-4
6. Generate answer using only the context
7. Return answer with source citations

### Why This Approach?
- **Accuracy**: Only answers from your documents
- **Transparency**: Shows which documents were used
- **Scalability**: Vector search is fast even with many documents
- **Flexibility**: Easy to add/remove documents by re-indexing

## Cost Considerations

### OpenAI Costs (Approximate)
- Embeddings: ~$0.13 per 1M tokens (~$0.0001 per document)
- Chat: ~$0.01 per 1K tokens (~$0.02-0.10 per query)

For 1000 documents and 100 queries/day:
- One-time indexing: ~$1-5
- Daily usage: ~$2-10
- Monthly: ~$60-300

### Optimization Tips
- Use `text-embedding-3-small` instead (3x cheaper)
- Use `gpt-3.5-turbo` instead of GPT-4 (10x cheaper)
- Cache common queries
- Adjust chunk sizes based on your needs

## Integration Examples

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"query": "What is the main topic?"}
)
print(response.json()["answer"])
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'What is the main topic?'})
});
const data = await response.json();
console.log(data.answer);
```

### cURL
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

## Production Deployment

See `DEPLOYMENT.md` for detailed instructions on:
- Docker deployment
- AWS EC2 deployment
- Cloud platform deployment (Railway, Render, Heroku)
- Security configuration
- Scaling strategies
- Monitoring setup

## Support & Documentation

- **README.md**: Comprehensive documentation
- **QUICKSTART.md**: Get started in 5 minutes
- **DEPLOYMENT.md**: Production deployment guide
- **example_usage.py**: Python client examples
- **Swagger Docs**: http://localhost:8000/docs

## Next Steps

1. Extract the zip file
2. Read QUICKSTART.md
3. Set up your environment
4. Index your documents
5. Start querying!

## Technical Stack

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn
- **AI**: OpenAI GPT-4 & text-embedding-3-large
- **Database**: Supabase (PostgreSQL + pgvector)
- **Document Processing**: python-docx
- **Validation**: Pydantic v2

## License & Usage

This is a complete, ready-to-use system. You can:
✅ Use it commercially
✅ Modify as needed
✅ Deploy to production
✅ Integrate with your applications

No attribution required, though appreciated!

---

**Questions?** Check the README.md for troubleshooting and detailed documentation.

**Ready to start?** Unzip and follow QUICKSTART.md!
