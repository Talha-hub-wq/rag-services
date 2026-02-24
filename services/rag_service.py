from typing import List, Dict, Any
import openai
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service responsible for retrieval-augmented generation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the RAG service.
        
        Args:
            api_key: OpenAI API key
            model: Chat model to use
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = """You are a helpful assistant that answers questions based solely on the provided context.

IMPORTANT INSTRUCTIONS:
1. Only use information from the provided context to answer questions
2. If the answer cannot be found in the context, clearly state that you don't have enough information
3. Do not make up or infer information that is not explicitly stated in the context
4. Be concise and accurate in your responses
5. If relevant, cite which part of the context you're using

Always maintain a professional and helpful tone."""
    
    def generate_response(self, query: str, context_documents: List[Dict[str, Any]]) -> str:
        """
        Generate a response using retrieved context.
        
        Args:
            query: User's question
            context_documents: Retrieved relevant documents
            
        Returns:
            Generated response
        """
        # Build context from retrieved documents
        context_parts = []
        for idx, doc in enumerate(context_documents, 1):
            content = doc.get('content', '')
            source = doc.get('source_file', 'Unknown')
            similarity = doc.get('similarity', 0)
            
            context_parts.append(
                f"[Document {idx}] (Source: {source}, Relevance: {similarity:.2f})\n{content}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        if not context:
            return "I don't have any relevant information to answer your question."
        
        # Create the user message with context and query
        user_message = f"""Context Information:
{context}

---

Question: {query}

Please answer the question based only on the context information provided above."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated response for query: {query[:50]}...")
            return answer
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error while processing your question: {str(e)}"
    
    def generate_response_streaming(self, query: str, context_documents: List[Dict[str, Any]]):
        """
        Generate a streaming response using retrieved context.
        
        Args:
            query: User's question
            context_documents: Retrieved relevant documents
            
        Yields:
            Response chunks
        """
        # Build context from retrieved documents
        context_parts = []
        for idx, doc in enumerate(context_documents, 1):
            content = doc.get('content', '')
            source = doc.get('source_file', 'Unknown')
            similarity = doc.get('similarity', 0)
            
            context_parts.append(
                f"[Document {idx}] (Source: {source}, Relevance: {similarity:.2f})\n{content}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        if not context:
            yield "I don't have any relevant information to answer your question."
            return
        
        user_message = f"""Context Information:
{context}

---

Question: {query}

Please answer the question based only on the context information provided above."""
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error generating streaming response: {str(e)}")
            yield f"I encountered an error while processing your question: {str(e)}"
