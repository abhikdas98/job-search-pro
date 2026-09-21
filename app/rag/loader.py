import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document

class DocumentLoader:
    """
    Service responsible for fetching and parsing both PDF and Markdown documents
    from a local directory source.
    """
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    def load_all_documents(self) -> list[Document]:
        """
        Scans the directory for both .pdf and .md files and loads them.
        """
        if not self.data_dir.exists():
            raise FileNotFoundError(f"The specified path {self.data_dir} does not exist.")

        all_documents = []

        pdf_loader = DirectoryLoader(
            str(self.data_dir),
            glob = "**/*.pdf",
            loader_cls = PyPDFLoader,
            show_progress = True
        )

        pdf_docs = pdf_loader.load()
        all_documents.extend(pdf_docs)
        print(f"Loaded {len(pdf_docs)} PDF document pages.")

        md_loader = DirectoryLoader(
            str(self.data_dir),
            glob = "**/*.md",
            loader_cls = TextLoader,
            show_progress = True
        )

        md_docs = md_loader.load()
        all_documents.extend(md_docs)
        print(f"Loaded {len(md_docs)} Markdown document pages.")

        return all_documents