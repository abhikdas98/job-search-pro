from app.models.job import Job
from app.tools.job_search.adzuna import AdzunaJobSource

def search_jobs(
    target_roles: list[str],
    locations: list[str],
) -> list[Job]:
    """
    Search for jobs based on target roles and locations.

    This is initially a mock implementation.
    Later this function will call real job sources/APIs.
    """
    """jobs = Job(
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
    )"""

    source = AdzunaJobSource()

    jobs: list[Job] = []
    for role in target_roles:
        for location in locations:
            results = source.search(query=role, location=location)
            jobs.extend(results)

    return jobs