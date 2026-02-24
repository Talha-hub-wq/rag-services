from pydantic import BaseModel, Field , EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., description="User's question", min_length=1)
    top_k: int = Field(default=5, description="Number of similar documents to retrieve", ge=1, le=20)
    similarity_threshold: float = Field(
        default=0.5, 
        description="Minimum similarity score for retrieval", 
        ge=0.0, 
        le=1.0
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    num_sources: int = Field(..., description="Number of source documents retrieved")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class IndexStatus(BaseModel):
    """Status of document indexing process."""
    status: str = Field(..., description="Indexing status")
    total_documents: int = Field(..., description="Total documents found")
    total_chunks: int = Field(..., description="Total chunks created")
    indexed_chunks: int = Field(..., description="Successfully indexed chunks")
    failed_chunks: int = Field(default=0, description="Failed chunks")
    message: str = Field(..., description="Status message")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")



class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
