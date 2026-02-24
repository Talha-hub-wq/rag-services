-- RAG Service - Supabase Setup Script
-- Run this in your Supabase SQL Editor to set up the vector store

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documents table
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- text-embedding-3-large produces 3072 dimensions
    metadata JSONB DEFAULT '{}'::jsonb,
    source_file TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create an index for vector similarity search using cosine distance
CREATE INDEX documents_embedding_idx 
ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Create an index on source_file for faster lookups
CREATE INDEX IF NOT EXISTS documents_source_file_idx 
ON documents(source_file);

-- Create an index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS documents_created_at_idx 
ON documents(created_at DESC);

-- Create a function to search for similar documents using cosine similarity
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),  -- 3072 se 1536
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    source_file TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.source_file,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant necessary permissions (adjust role name as needed)
-- GRANT USAGE ON SCHEMA public TO anon, authenticated;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO anon, authenticated;
-- GRANT EXECUTE ON FUNCTION match_documents TO anon, authenticated;

-- Create a function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents BIGINT,
    total_size_mb NUMERIC,
    earliest_document TIMESTAMP WITH TIME ZONE,
    latest_document TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_documents,
        ROUND((pg_total_relation_size('documents')::NUMERIC / (1024*1024)), 2) AS total_size_mb,
        MIN(created_at) AS earliest_document,
        MAX(created_at) AS latest_document
    FROM documents;
END;
$$;

-- Comment on table and columns
COMMENT ON TABLE documents IS 'Stores document chunks with their vector embeddings for RAG';
COMMENT ON COLUMN documents.id IS 'Unique identifier for each document chunk';
COMMENT ON COLUMN documents.content IS 'Text content of the document chunk';
COMMENT ON COLUMN documents.embedding IS 'Vector embedding of the content (3072 dimensions for text-embedding-3-large)';
COMMENT ON COLUMN documents.metadata IS 'Additional metadata as JSON (chunk_index, total_chunks, etc.)';
COMMENT ON COLUMN documents.source_file IS 'Path to the source document file';
COMMENT ON COLUMN documents.created_at IS 'Timestamp when the document was indexed';

-- Example queries to test the setup:

-- Check if extension is enabled
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- Count documents
-- SELECT COUNT(*) FROM documents;

-- Test similarity search (after indexing documents)
-- SELECT * FROM match_documents(
--     query_embedding := (SELECT embedding FROM documents LIMIT 1),
--     match_threshold := 0.5,
--     match_count := 5
-- );

-- Get statistics
-- SELECT * FROM get_document_stats();


-- create a new table  for authentication Routes in Supabase

-- Users table

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Password reset tokens table
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;