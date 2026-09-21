from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentSplitter:
    """
    Handles chunking long raw text elements into semantically cohesive document sections.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            add_start_index=True,
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
         """
        Accepts a list of full text documents and breaks them down into standard chunks.
        """
         if not documents:
             return []
         chunks = self.splitter.split_documents(documents)
         print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
         return chunks