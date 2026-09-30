from app.core.paths import FAISS_INDEX_DIR
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retriever import RAGRetrieverService


def retrieve_candidate_context(
    query: str,
    top_k: int = 3,
) -> str:
    """
    Retrieve candidate evidence from the local FAISS knowledge base.

    This is the reusable candidate retrieval layer used by:
    - candidate_context_node
    - future job-specific candidate matching
    """

    embeds = EmbeddingService.get_embedding_model(
        "huggingface"
    )

    db_service = VectorStoreService(
        index_dir=FAISS_INDEX_DIR,
        embedding_model=embeds,
    )

    try:
        db_instance = db_service.load_index()

    except FileNotFoundError:
        print(
            f"⚠️ FAISS Index folder at "
            f"'{FAISS_INDEX_DIR}' is missing text indices."
        )

        return "No resume context files initialized."

    retriever = RAGRetrieverService(db_instance)

    retrieved_context = retriever.retrieve_as_formatted_string(
        query,
        top_k=top_k,
    )

    return retrieved_context