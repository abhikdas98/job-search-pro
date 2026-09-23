import os
from pathlib import Path
from app.workflows.state import State
from app.services.request_parser import RequestParser
from app.services.job_search import search_jobs as job_search_tool
from app.services.filter_jobs import filtered_jobs as job_filter_tool
from app.services.rank_jobs import rank_jobs as rank_filter_tool
from app.ui.streamlit.load_ui import LoadStreamlitUI
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig
from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retriever import RAGRetrieverService


def parse_request_node(state: State, config: RunnableConfig) -> dict:
    """Parses the user request into a structured UserProfile"""
    user_request = state["user_request"]
    candidate_resume_context = state["candidate_context"]

    llm = ChatGroq(model=config["configurable"].get("model"), api_key=os.getenv("GROQ_API_KEY"))
    parser = RequestParser(llm=llm)
    user_profile = parser.parse(user_request, candidate_resume_context)

    return {
        "user_profile": user_profile
    }


def job_search_node(state: State) -> dict:
    """Searches job using the user's parsed preference"""

    user_profile = state["user_profile"]
    target_roles = user_profile.target_roles
    locations = user_profile.locations

    jobs = job_search_tool(
        target_roles=target_roles,
        locations=locations
    )

    return {
        "jobs": jobs
    }


def job_filter_node(state: State) -> dict:
    filtered_jobs = job_filter_tool(
        jobs=state["jobs"],
        user_profile=state["user_profile"]
    )

    return {
        "selected_jobs": filtered_jobs
    }


def rank_jobs_node(state: State) -> dict:
    ranked_jobs = rank_filter_tool(
        jobs=state["selected_jobs"],
        user_profile=state["user_profile"]
    )

    return {
        "selected_jobs": ranked_jobs
    }

def candidate_context_node(state: State):
    """
    Queries the local FAISS index using the user_request to extract 
    relevant candidate profile/resume text context.
    """
    PROJECT_ROOT = Path(__file__).resolve().parent
    search_query = state.get("user_request", "")

    #Define absolute folder path
    FILE_INDEX_PATH = PROJECT_ROOT / "data" / "faiss_index"

    #Load the existing index cached in the local disk without reca;culating the embeddings
    embeds = EmbeddingService.get_embedding_model("huggingface")
    db_service = VectorStoreService(index_dir=FILE_INDEX_PATH, embedding_model=embeds)

    try:
        db_instance = db_service.load_index()

    except FileNotFoundError:
        # Fallback guard rule: If the index folder is empty, return an empty context safely
        print(f"⚠️ FAISS Index folder at '{FILE_INDEX_PATH}' is missing text indices.")
        return {"candidate_context": "No resume context files initialized."}

    #Run the semantic search lookup parameters
    retriever = RAGRetrieverService(db_instance)
    retrieved_context = retriever.retrieve_as_formatted_string(search_query, top_k=3)

    return {
        "candidate_context": retrieved_context
    }