import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.embeddings import Embeddings

class EmbeddingService:
    """
    Class to instantiate and manage different text embedding models.
    """
    @staticmethod
    def get_embedding_model(provider: str = "huggingface") -> Embeddings:
        """
        Returns an instance of a LangChain compatible Embedding class.
        Supported providers: 'huggingface' (Local), 'openai', 'ollama'
        """
        provider_lower = provider.lower()
        
        if provider == "huggingface":
            from langchain_huggingface import HuggingFaceEmbeddings
            print("🧬 Initializing Local HuggingFace Embeddings (bge-small-en-v1.5)...")
            return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        elif provider == "openai":
            from langchain_openai import OpenAIEmbeddings
            print("🧬 Initializing OpenAI Embeddings (text-embedding-3-small)...")
            return OpenAIEmbeddings(model="text-embedding-3-small")
        elif provider == "ollama":
            from langchain_community.embeddings import OllamaEmbeddings
            print("🧬 Initializing Local Ollama Embeddings...")
            return OllamaEmbeddings(model="nomic-embed-text")
        else:
            raise ValueError(
                f"Unsupported embedding provider: '{provider}'. "
                f"Choose from 'huggingface', 'openai', or 'ollama'."
            )