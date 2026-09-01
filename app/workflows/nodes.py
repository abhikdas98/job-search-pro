from app.workflows.state import State
from app.services.job_search import search_jobs as job_search_tool
from app.services.filter_jobs import filtered_jobs as job_filter_tool
from app.services.rank_jobs import rank_jobs as rank_filter_tool

def job_search_node(state: State) -> dict:
    """Searches job using the user's parsed preference"""

    user_profile = state["user_profile"]
    target_roles = user_profile.get("target_role", [])
    locations = user_profile.get("locations", [])

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