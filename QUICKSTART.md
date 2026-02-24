# Quick Start Guide

Get your RAG Chatbot running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Setup Supabase

1. Create a new project at https://supabase.com
2. Go to SQL Editor
3. Copy & paste the contents of `supabase_setup.sql`
4. Click "Run"
5. Get your credentials from Project Settings > API

## Step 3: Configure Environment

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-key-here
DOCUMENTS_PATH=/path/to/your/documents
```



## Step 4: Start the API

```bash
uvicorn main:app --reload
```

## Step 5: Test It!

Open http://localhost:8000/docs in your browser and try the `/chat` endpoint.

Or run the example:
```bash
python example_usage.py
```
## Authentication Endpoints


## API Endpoints

- **Health**: `GET /health`
- **index-documents**: `POST /Indexing-docs`
- **upload-documents**: `POST /upload-docs`
- **Chat**: `POST /chat`
- **Stream**: `POST /chat/stream`

## Example Request

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this about?",
    "top_k": 5
  }'
```

## Troubleshooting

**"Documents not found"**
- Check your DOCUMENTS_PATH in .env
- Make sure you have .docx files in that directory

**"OpenAI API error"**
- Verify your API key is correct
- Check you have credits in your OpenAI account

**"Supabase error"**
- Make sure you ran the SQL setup script
- Check your Supabase URL and key
- Verify pgvector extension is enabled

## Next Steps

1. Try different queries in the Swagger UI
2. Adjust `chunk_size` and `similarity_threshold` for better results
3. Integrate with your frontend application
4. Check README.md for advanced configuration

## Need Help?

See the full README.md for detailed documentation.
