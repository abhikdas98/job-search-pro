import os
from app.workflows.state import State
from app.services.request_parser import RequestParser
from app.services.job_search import search_jobs as job_search_tool
from app.services.filter_jobs import filtered_jobs as job_filter_tool
from app.services.rank_jobs import rank_jobs as rank_filter_tool
from app.ui.streamlit.load_ui import LoadStreamlitUI
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig


def parse_request_node(state: State, config: RunnableConfig) -> dict:
    """Parses the user request into a structured UserProfile"""
    user_request = state["user_request"]

    llm = ChatGroq(model=config["configurable"].get("model"), api_key=os.getenv("GROQ_API_KEY"))
    parser = RequestParser(llm=llm)
    user_profile = parser.parse(user_request)

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
