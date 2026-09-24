from pathlib import Path
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document

class RAGRetrieverService:
    """
    Service layer responsible for running semantic search queries 
    agains"""
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve_relevant_context(self, query: str, top_k: int = 4) -> list[Document]:
        """
        Performs a semantic similarity search against the FAISS vector database
        and returns the top K most matching document chunks.
        """
        if not self.vector_store:
            raise ValueError("Vector store index is not initialized or loaded")

        # Query the FAISS database engine directly using MMR lookups
        matching_chunks = self.vector_store.max_marginal_relevance_search(
            query=query,
            k=top_k,
            fetch_k=10,
            lambda_mult=0.5
            )

        print(f"✨ Found {len(matching_chunks)} relevant source text segments")

        unique_chunks = []
        seen = set()

        for doc in matching_chunks:
            source = doc.metadata.get("source", "unknown")

            Content = doc.page_content.strip()

            key = (source, Content)

            if key not in seen:
                seen.add(key)
                unique_chunks.append(doc)

        return unique_chunks
        

    def retrieve_as_formatted_string(self, query: str, top_k: int = 4) -> str:
        """
        Retrieves matching chunks and joins them together into a single clean string.
        Perfect for injecting directly into LLM prompts.
        """
        chunks = self.retrieve_relevant_context(query, top_k=top_k)

        # Flatten structural chunks into a coherent background payload text window
        formatted_context = "\n\n---\n\n".join(
            f"[Source: {doc.metadata.get('source', 'Unknown')} (Page: {doc.metadata.get('page', 1)})]\n{doc.page_content}"
            for doc in chunks
        )

        return formatted_context