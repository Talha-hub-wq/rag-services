# RAG Chatbot Service

A professional, production-ready Retrieval-Augmented Generation (RAG) chatbot service built with FastAPI, OpenAI, and Supabase. This service processes local Word documents, creates embeddings, stores them in a vector database, and provides an API for intelligent Q&A based on the document content.

## 🚀 Features

- **Document Processing**: Recursively scans directories for .docx files
- **Text Cleaning**: Advanced text preprocessing and normalization
- **Intelligent Chunking**: Creates optimal 500-character chunks with overlap
- **OpenAI Embeddings**: Uses `text-embedding-3-large` for high-quality embeddings
- **Vector Search**: Supabase with pgvector for efficient similarity search
- **RAG Pipeline**: Context-aware responses using GPT-4
- **FastAPI**: Modern, fast API with automatic documentation
- **CORS Support**: Ready for frontend integration
- **Streaming Support**: Real-time response streaming
- **Professional Architecture**: Follows SOLID principles and SRP

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
│── auth_routes.py        # RAG pipeline orchestration
├── example_usage.py     # Example Python client
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── supabase_setup.sql  # Database schema and functions
├── .gitignore          # Git ignore patterns
├── README.md           # Comprehensive documentation
├── QUICKSTART.md       # 5-minute setup guide
└── DEPLOYMENT.md       # Production deployment guide
```

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.9+
- OpenAI API key
- Supabase account and project
- Word documents (.docx) in a local directory

### 2. Installation

```bash
# Extract the zip file
unzip rag-service.zip
cd rag-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Supabase Setup

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `supabase_setup.sql`
4. Execute the SQL script
5. Note your Supabase URL and service key from **Project Settings > API**

### 4. Environment Configuration

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

Required environment variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-key-here

# Document Path
DOCUMENTS_PATH=/path/to/your/documents/folder

# Optional: Model Configuration
EMBEDDING_MODEL=text-embedding-3-large
CHAT_MODEL=gpt-4-turbo-preview
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

<!-- ### 5. Index Your Documents

Run the indexing script to process and store your documents:

```bash
# Make sure your virtual environment is activated
python scripts/index_documents.py
```

This will:
- Scan your documents directory recursively
- Load all .docx files
- Clean and chunk the text
- Create embeddings using OpenAI
- Store everything in Supabase

**Note**: The first run may take a while depending on the number of documents. -->

### 6. Start the API Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation


### Interactive Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints
## Authentication Endpoint

Post / Signup
Post / Login
Post / Refresh
Get /  Auth-me
Post / Forgot-Password
Post / Reset Password
Post / Change-Password

## Default Endpoint

#### 1. Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

#### 2. Chat (Standard)

```bash
POST /chat
Content-Type: application/json

{
  "query": "What is the main topic of the documents?",
  "top_k": 5,
  "similarity_threshold": 0.5
}
```

Response:
```json
{
  "query": "What is the main topic of the documents?",
  "answer": "Based on the documents, the main topic is...",
  "sources": [
    {
      "content": "Document excerpt...",
      "source_file": "/path/to/document.docx",
      "similarity": 0.85
    }
  ],
  "num_sources": 5
}
```

#### 3. Chat (Streaming)

```bash
POST /chat/stream
Content-Type: application/json

{
  "query": "Explain the key concepts",
  "top_k": 3
}
```

Returns a streaming text response.

## 🔧 Configuration Options

### Chunk Size

Adjust in `.env`:
```env
CHUNK_SIZE=500        # Characters per chunk
CHUNK_OVERLAP=50      # Overlap between chunks
```

### Search Parameters

In API requests:
- `top_k`: Number of similar documents to retrieve (1-20)
- `similarity_threshold`: Minimum similarity score (0.0-1.0)

### Models

You can change the models in `.env`:
```env
EMBEDDING_MODEL=text-embedding-3-large  # Best quality
CHAT_MODEL=gpt-4-turbo-preview          # Most capable
```

Or use smaller/faster models:
```env
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-3.5-turbo
```

## 🎯 Usage Examples

### Python Client

```python
import requests

# Chat request
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "query": "What are the main requirements?",
        "top_k": 5,
        "similarity_threshold": 0.6
    }
)

data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {data['num_sources']}")
```

### JavaScript/TypeScript Client

```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'What are the key points?',
    top_k: 5,
    similarity_threshold: 0.5
  })
});

const data = await response.json();
console.log('Answer:', data.answer);
```

### cURL

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is discussed in the documents?",
    "top_k": 5
  }'
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use environment-specific configurations** for development/production
3. **Rotate API keys regularly**
4. **Configure CORS** properly in `main.py` for production:
   ```python
   allow_origins=["https://yourdomain.com"]  # Replace * with specific domains
   ```
5. **Use HTTPS** in production
6. **Rate limiting**: Consider adding rate limiting middleware

## 🐛 Troubleshooting

### Documents not found
- Check `DOCUMENTS_PATH` in `.env`
- Ensure path is absolute
- Verify .docx files exist in subdirectories

### Embedding errors
- Verify OpenAI API key is correct
- Check API quota and billing
- Ensure internet connectivity

### Supabase connection errors
- Verify Supabase URL and key
- Check if pgvector extension is enabled
- Ensure SQL setup script was executed

### Low similarity scores
- Try lowering `similarity_threshold`
- Increase `top_k` to get more results
- Consider re-indexing with different chunk sizes

## 📊 Performance Tips

1. **Batch processing**: The indexing script processes documents efficiently
2. **Caching**: Consider adding Redis for frequently asked questions
3. **Index tuning**: Adjust Supabase IVFFlat lists parameter for your data size
4. **Model selection**: Use smaller models for faster responses if acceptable
5. **Chunk size**: Experiment with different sizes (300-800 works well)

## 🔄 Re-indexing Documents

To update the index after adding new documents:

```bash
# This will add new documents to existing index
python scripts/index_documents.py
```

To completely rebuild the index:
1. Clear the Supabase table: `DELETE FROM documents;`
2. Run the indexing script again

## 📝 Logging

Logs are printed to console with timestamps. To save logs:

```bash
python scripts/index_documents.py 2>&1 | tee indexing.log
uvicorn main:app --log-config logging.ini
```

## 🤝 Integration Example

```html
<!-- Simple chatbot integration -->
<script>
async function askQuestion(query) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query})
  });
  const data = await response.json();
  return data.answer;
}

// Usage
const answer = await askQuestion('What is the main topic?');
console.log(answer);
</script>
```

## 📄 License

This project is provided as-is for your use.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check Supabase and OpenAI documentation

## 🎉 You're All Set!

Your RAG chatbot service is ready to use. Start by indexing your documents and then make queries through the API!
