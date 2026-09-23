import streamlit as st
from app.ui.streamlit.load_ui import LoadStreamlitUI
from app.workflows.graph import GraphBuilder

import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq

from pathlib import Path
from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStoreService
from app.rag.retriever import RAGRetrieverService

def seed_rag_database_once():
    PROJECT_ROOT = Path(__file__).resolve().parent
    FILE_DIR = PROJECT_ROOT / "data" / "knowledge_base"
    FILE_INDEX_PATH = PROJECT_ROOT / "data" / "faiss_index"

    FILE_DIR.mkdir(parents=True, exist_ok=True)

    loader_service = DocumentLoader(FILE_DIR)
    docs = loader_service.load_all_documents()

    if not docs:
        print(f"⚠️ Seeding aborted: No files found inside source folder '{FILE_DIR}'.")
        return

    splitter_service = DocumentSplitter()
    chunks = splitter_service.split_documents(docs)

    embeds = EmbeddingService.get_embedding_model("huggingface")
    db_service = VectorStoreService(index_dir=FILE_INDEX_PATH, embedding_model=embeds)

    print(f"🏗️ Generating semantic text embeddings for database seeding...")
    db_service.build_or_update_index(chunks)

    print(f"✅ Seeding finished successfully! Index saved at: '{FILE_INDEX_PATH}'")

def load_agenticai_app():
    """
    Loads and runs the LangGraph Agentic AI Application with Streamlist UI.
    This functoin initializes the UI, handles user input, loads LLM model,
    sets up the graph based on the selected use case, and displays the output
    while handling the exceptions for robustness.
    """
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI")

    user_message = st.chat_input("Enter your message:")

    if user_message:
        #Display user message in chat message container
        st.chat_message("user").write(user_message)

        api_key = os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
        
        model = ChatGroq(model=user_input.get("selected_groq_model"), api_key=os.getenv("GROQ_API_KEY"))

        config = {"configurable": {
            "model": user_input.get("selected_groq_model"),
        }}

        final_graph = GraphBuilder().basic_job_search_agent()
        result = final_graph.invoke({
            "user_request": user_message,
            "llm": model
        }, config=config)

        print(result["jobs"])
        # Inside app/main.py where you process the graph result

        # 1. Safely extract whatever the graph returned (jobs or selected_jobs)
        raw_jobs_data = result.get("selected_jobs") or result.get("jobs") or []

        # 2. Convert to a standard list if it came back as a Tuple
        if isinstance(raw_jobs_data, tuple):
            jobs_list = list(raw_jobs_data)
        else:
            jobs_list = raw_jobs_data

        st.chat_message("assistant").write(f"Found {len(jobs_list)} matching job positions:")

        # 3. Loop through and render them dynamically on the screen
        for item in jobs_list:
            # Handle if the item is a RankedJob dictionary or object wrapper
            if isinstance(item, dict) and "job" in item:
                job_data = item["job"]
                score = item.get("score")
            elif hasattr(item, "job"):
                job_data = item.job
                score = getattr(item, "score", None)
            else:
                job_data = item
                score = None

            # 4. Safely extract attributes checking both Pydantic Object properties or Dict keys
            title = getattr(job_data, "title", None) or job_data.get("title", "Unknown Position")
            company = getattr(job_data, "company", None) or job_data.get("company", "Unknown Company")
            location = getattr(job_data, "location", None) or job_data.get("location", "N/A")
            url = getattr(job_data, "url", None) or job_data.get("url", "#")
            desc = getattr(job_data, "description", None) or job_data.get("description", "No description provided.")

            # 5. Render clean visual cards on your Streamlit interface
            with st.container(border=True):
                match_badge = f"🎯 **Match Score:** {int(score * 100)}%" if score is not None else ""
                st.subheader(f"{title} @ {company}")
                st.markdown(f"📍 **Location:** {location} | {match_badge}")
                st.write(desc)
                # Convert HttpUrl objects safely to pure strings for the link component
                st.link_button("View Job Posting 🚀", url=str(url))