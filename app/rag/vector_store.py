import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

class VectorStoreService:
    """
    Service responsible for building, saving, loading, and updating 
    a local FAISS Vector database index.
    """
    def __init__(self, index_dir: str | Path, embedding_model: Embeddings):
        self.index_dir = Path(str(index_dir))
        self.embeddings = embedding_model
        self.vector_store = None

    def build_index(self, chunks: list[Document]) -> FAISS:
            """
            Builds a fresh FAISS index from the supplied chunks.
            Existing local index is replaced.
            """
    
            if not chunks:
                print("⚠️ No chunks provided to index.")
                return None
    
            print("🏗️ Creating a fresh vector index...")
    
            self.vector_store = FAISS.from_documents(
                chunks,
                self.embeddings
            )
    
            self.index_dir.mkdir(parents=True, exist_ok=True)
    
            self.vector_store.save_local(
                str(self.index_dir)
            )
    
            print(
            f"💾 FAISS vector database successfully saved to: "
            f"'{self.index_dir}'"
            )
    
            return self.vector_store
    

    def load_index(self) -> FAISS:
        """
        Loads the persisted FAISS database from disk. Throws an error if index files are missing.
        """
        if not self.index_dir.exists() or not (self.index_dir / "index.faiss").exists():
            raise FileNotFoundError(f"No FAISS index files found inside storage directory: '{self.index_dir}'")
        self.vector_store = FAISS.load_local(
            folder_path = str(self.index_dir),
            embeddings = self.embeddings,
            allow_dangerous_deserialization = True
        )

        return self.vector_store


    