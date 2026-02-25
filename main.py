from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from scripts.index_documents import index_documents
from auth_routes import router as auth_router, get_current_user
from services import TextProcessor, EmbeddingService, VectorStore
from fastapi import BackgroundTasks

from fastapi import UploadFile, File
import logging
from config import settings

# from config import settings
print("SUPABASE URL:", settings.supabase_url)
print("SUPABASE KEY starts with:", settings.supabase_key[:10])

from models import ChatRequest, ChatResponse, HealthResponse, ErrorResponse
from services import EmbeddingService, VectorStore, RAGService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation API for document-based Q&A",
    version="1.0.0",
)
# Include authentication router
app.include_router(auth_router)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (singleton pattern)
embedding_service = None
vector_store = None
rag_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global embedding_service, vector_store, rag_service

    logger.info("Initializing services...")

    try:
        embedding_service = EmbeddingService(
            api_key=settings.openai_api_key, model=settings.embedding_model
        )

        vector_store = VectorStore(
            supabase_url=settings.supabase_url, supabase_key=settings.supabase_key
        )

        rag_service = RAGService(
            api_key=settings.openai_api_key, model=settings.chat_model
        )

        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/index-documents")
async def trigger_indexing(background_tasks: BackgroundTasks):
    """Route to run indexing script"""
    background_tasks.add_task(index_documents)
    return {"message": "Indexing started"}


@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    # current_user: dict = Depends(get_current_user)
):
    """Upload single document and index it"""

    # File read karo
    content = await file.read()

    # Docx parse karo
    from docx import Document
    from io import BytesIO

    doc = Document(BytesIO(content))
    text = "\n".join([para.text for para in doc.paragraphs])

    # Services initialize
    text_processor = TextProcessor()
    embedding_service = EmbeddingService(
        settings.openai_api_key, settings.embedding_model
    )
    vector_store = VectorStore(settings.supabase_url, settings.supabase_key)

    # Process
    chunks = text_processor.process_document(text)
    indexed = 0

    for idx, chunk in enumerate(chunks):
        embedding = embedding_service.create_embedding(chunk)
        success = vector_store.insert_document(
            chunk,
            embedding,
            file.filename,
            {"chunk_index": idx, "total_chunks": len(chunks)},
        )
        if success:
            indexed += 1

    return {"filename": file.filename, "total_chunks": len(chunks), "indexed": indexed}


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def chat(request: ChatRequest):
    """
    Chat endpoint for question answering using RAG.

    This endpoint:
    1. Creates an embedding for the user's query
    2. Searches for similar documents in the vector store
    3. Generates a response using retrieved context

    Args:
        request: ChatRequest containing query and search parameters

    Returns:
        ChatResponse with answer and source information
    """
    try:
        logger.info(f"Received query: {request.query}")

        # Create query embedding
        query_embedding = embedding_service.create_embedding(request.query)

        # Search for similar documents
        similar_docs = vector_store.search_similar(
            query_embedding=query_embedding,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
        )

        if not similar_docs:
            return ChatResponse(
                query=request.query,
                answer="I couldn't find any relevant information to answer your question. Please try rephrasing or ask something else.",
                sources=[],
                num_sources=0,
            )

        # Generate response using RAG
        answer = rag_service.generate_response(
            query=request.query, context_documents=similar_docs
        )

        # Prepare sources for response
        sources = [
            {
                "content": (
                    doc.get("content", "")[:200] + "..."
                    if len(doc.get("content", "")) > 200
                    else doc.get("content", "")
                ),
                "source_file": doc.get("source_file", "Unknown"),
                "similarity": doc.get("similarity", 0),
            }
            for doc in similar_docs
        ]

        return ChatResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            num_sources=len(similar_docs),
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing your request: {str(e)}",
        )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint for real-time response generation.

    Args:
        request: ChatRequest containing query and search parameters

    Returns:
        StreamingResponse with generated text
    """
    try:
        logger.info(f"Received streaming query: {request.query}")

        # Create query embedding
        query_embedding = embedding_service.create_embedding(request.query)

        # Search for similar documents
        similar_docs = vector_store.search_similar(
            query_embedding=query_embedding,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
        )

        if not similar_docs:

            async def no_results_generator():
                yield "I couldn't find any relevant information to answer your question."

            return StreamingResponse(no_results_generator(), media_type="text/plain")

        # Generate streaming response
        def generate():
            for chunk in rag_service.generate_response_streaming(
                query=request.query, context_documents=similar_docs
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Error processing streaming chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing your request: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
