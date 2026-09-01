from app.models.job import Job

def search_jobs(
    target_roles: list[str],
    locations: list[str],
) -> list[Job]:
    """
    Search for jobs based on target roles and locations.

    This is initially a mock implementation.
    Later this function will call real job sources/APIs.
    """
    jobs = Job(
        id="job_001",
        title="Generative AI Engineer",
        company="Example AI",
        location="Bangalore, India",
        url="https://example.com/jobs/001",
        description=(
            "Build LLM applications, RAG pipelines, "
            "and agentic AI systems using Python."
        ),
        source="mock",
    ),
    Job(
        id="job_002",
        title="AI Engineer",
        company="Tech Solutions",
        location="Hyderabad, India",
        url="https://example.com/jobs/002",
        description=(
            "Develop machine learning and generative AI "
            "applications using Python and LLMs."
        ),
        source="mock",
    )

    """user_request = state.get("user_request", "")
    user_profile = state.get("user_profile", {})

    target_roles = user_profile.get("target_roles", [])
    locations = user_profile.get("locations", [])

    jobs = [{"job_role": user_request, "target_roles": target_roles, "locations": locations}]"""

    return jobs