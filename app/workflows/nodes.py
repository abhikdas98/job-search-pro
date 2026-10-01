import os
from app.workflows.state import State
from app.services.request_parser import RequestParser
from app.services.job_search import search_jobs as job_search_tool
from app.services.filter_jobs import filtered_jobs as job_filter_tool
from app.services.rank_jobs import rank_jobs as rank_filter_tool
from app.ui.streamlit.load_ui import LoadStreamlitUI
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig
from app.rag.loader import DocumentLoader
from app.services.candidate_context import retrieve_candidate_context
from app.services.job_analyzer import analyze_job
from app.services.candidate_matcher import (
    retrieve_job_candidate_evidence,
    match_candidate,
)

MAX_JOBS_TO_MATCH = 8


def parse_request_node(state: State, config: RunnableConfig) -> dict:
    """Parses the user request into a structured UserProfile"""
    user_request = state["user_request"]
    candidate_resume_context = state["candidate_context"]

    llm = ChatGroq(model=config["configurable"].get(
        "model"), api_key=os.getenv("GROQ_API_KEY"))
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
    """
    Rank filtered jobs using candidate-job match results.
    """

    ranked_jobs = rank_filter_tool(
        jobs=state["selected_jobs"],
        match_results=state["match_results"],
        user_profile=state["user_profile"],
    )

    print("\n" + "=" * 80)
    print("🏆 FINAL JOB RANKING")
    print("=" * 80)

    for index, job in enumerate(ranked_jobs, start=1):

        job_data = job["job"]

        print(
            f"{index}. "
            f"{job_data.get('title')} @ "
            f"{job_data.get('company')}"
        )

        print(
            f"   Final Score: {job['score']}"
        )

        print(
            f"   Match Score: "
            f"{job['match_score']}"
        )

        print(
            f"   Matched Skills: "
            f"{job['matched_skills']}"
        )

        print(
            f"   Missing Skills: "
            f"{job['missing_skills']}"
        )

        print("-" * 80)

        print(
            "RANKING PROFILE TYPE:",
            type(state["user_profile"])
        )

        print(
            "TARGET ROLES:",
            state["user_profile"].target_roles
        )

    return {
        "selected_jobs": ranked_jobs
    }


def candidate_context_node(state: State):
    """
    Retrieves candidate profile/resume context from the
    local FAISS knowledge base using the user's request.
    """

    search_query = state.get(
        "user_request",
        "",
    )

    retrieved_context = retrieve_candidate_context(
        query=search_query,
        top_k=3,
    )

    print("\n" + "=" * 80)
    print("🔎 CANDIDATE CONTEXT")
    print("=" * 80)
    print(retrieved_context)
    print("=" * 80)
    print(
        f"📏 Context length: "
        f"{len(retrieved_context)} characters"
    )
    print("=" * 80 + "\n")

    return {
        "candidate_context": retrieved_context
    }


def analyze_jobs_node(state: State) -> dict:
    """
    Analysze the selected jobs and return structured requirements
    """

    jobs = state.get("selected_jobs", [])

    analyzed_jobs = [
        analyze_job(job) for job in jobs
    ]

    print(
        f"🔍 Analyzed {len(analyzed_jobs)} jobs"
    )

    print("\n" + "=" * 80)
    print("🔍 ANALYZED JOBS")
    print("=" * 80)

    for job in analyzed_jobs:
        print(job)

    print("=" * 80 + "\n")

    return {
        "analyzed_jobs": analyzed_jobs
    }


def match_candidate_node(
        state: State,
        config: RunnableConfig
) -> dict:
    """
    Match the candidate against each analyzed job using
    job-specific RAG evidence.
    """

    analyzed_jobs = state.get("analyzed_jobs", [])

    jobs_to_match = analyzed_jobs[:MAX_JOBS_TO_MATCH]

    if len(analyzed_jobs) > MAX_JOBS_TO_MATCH:
        print(
            f"⚠️ {len(analyzed_jobs)} jobs available, but only "
            f"{MAX_JOBS_TO_MATCH} will be sent to the LLM matcher "
            f"for this run."
        )

    llm = ChatGroq(
        model=config["configurable"].get("model"),
        api_key=os.getenv("GROQ_API_KEY"),
    )

    match_results = []

    for job in jobs_to_match:
        print("\n" + "=" * 80)
        print(
            f"🧩 MATCHING CANDIDATE → "
            f"{job.get('title')} @ "
            f"{job.get('company')}"
        )
        print("=" * 80)

        # Retrieve evidence specifically for this job
        candidate_evidence = (
            retrieve_job_candidate_evidence(job)
        )

        print("\n📚 JOB-SPECIFIC CANDIDATE EVIDENCE")
        print("-" * 80)
        print(candidate_evidence)

        # Evaluate candidate against the job
        result = match_candidate(
            job=job,
            candidate_evidence=candidate_evidence,
            llm=llm,
        )

        match_results.append(result)

        print("\n🎯 MATCH RESULT")
        print("-" * 80)
        print(result)

    print("\n" + "=" * 80)
    print(
        f"✅ Candidate matching completed for "
        f"{len(match_results)} jobs"
    )
    print("=" * 80 + "\n")

    return {
        "match_results": match_results
    }
