"""
Example usage script for the RAG Chatbot API.
This demonstrates how to interact with the API from Python.
"""

import requests
import json


class RAGChatbotClient:
    """Simple client for interacting with the RAG Chatbot API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> dict:
        """Check if the API is healthy."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def chat(
        self, query: str, top_k: int = 5, similarity_threshold: float = 0.5
    ) -> dict:
        """
        Send a chat query to the API.

        Args:
            query: The question to ask
            top_k: Number of similar documents to retrieve
            similarity_threshold: Minimum similarity score

        Returns:
            Response dictionary with answer and sources
        """
        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "query": query,
                "top_k": top_k,
                "similarity_threshold": similarity_threshold,
            },
        )
        response.raise_for_status()
        return response.json()

    def chat_stream(
        self, query: str, top_k: int = 5, similarity_threshold: float = 0.5
    ):
        """
        Send a streaming chat query to the API.

        Args:
            query: The question to ask
            top_k: Number of similar documents to retrieve
            similarity_threshold: Minimum similarity score

        Yields:
            Response text chunks
        """
        response = requests.post(
            f"{self.base_url}/chat/stream",
            json={
                "query": query,
                "top_k": top_k,
                "similarity_threshold": similarity_threshold,
            },
            stream=True,
        )
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def main():
    """Example usage of the RAG Chatbot API."""

    # Initialize client
    client = RAGChatbotClient()

    # 1. Health check
    print("=" * 60)
    print("1. Health Check")
    print("=" * 60)
    try:
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Version: {health['version']}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the API server is running!")
        return

    # 2. Standard chat query
    print("=" * 60)
    print("2. Standard Chat Query")
    print("=" * 60)

    query = "What are the main topics covered in the documents?"
    print(f"Query: {query}\n")

    try:
        response = client.chat(query, top_k=5, similarity_threshold=0.5)

        print(f"Answer:\n{response['answer']}\n")
        print(f"Number of sources used: {response['num_sources']}")

        if response["sources"]:
            print("\nSources:")
            for i, source in enumerate(response["sources"], 1):
                print(f"\n  [{i}] Similarity: {source['similarity']:.2f}")
                print(f"      File: {source['source_file']}")
                print(f"      Preview: {source['content'][:100]}...")

        print()
    except Exception as e:
        print(f"Error: {e}\n")

    # 3. Streaming chat query
    print("=" * 60)
    print("3. Streaming Chat Query")
    print("=" * 60)

    query = "Can you summarize the key points?"
    print(f"Query: {query}\n")
    print("Streaming response:")

    try:
        for chunk in client.chat_stream(query, top_k=3):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"\nError: {e}\n")

    # 4. Multiple queries example
    print("=" * 60)
    print("4. Multiple Queries Example")
    print("=" * 60)

    queries = [
        "What is the purpose of this document?",
        "Are there any requirements mentioned?",
        "What are the conclusions?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        try:
            response = client.chat(query, top_k=3, similarity_threshold=0.6)
            print(f"Answer: {response['answer'][:200]}...")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
