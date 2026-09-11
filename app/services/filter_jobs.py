from app.models.job import Job
from app.workflows.state import State

def filtered_jobs(
        jobs: list[Job],
        user_profile: State["user_profile"]
) -> list[Job]:
    """
    Filter jobs based on the user's explicit preferences.

    Args:
        jobs: List of normalized Job objects.
        user_profile: Structured user preferences.

    Returns:
        List of jobs that satisfy the user's basic requirements.
    """

    filtered_jobs = []
    target_roles = [
        role.lower() for role in user_profile.target_roles
    ]
    locations = [
        location.lower() for location in user_profile.locations
    ]


    for job in jobs:
        #Job role filter
        if target_roles:
            job_title = job.title.lower()

            role_match = any(
                role in job_title for role in target_roles
            )
            if not target_roles:
                continue

        #Location filter
        if locations:
            job_location = job.location.lower()

            location_match = any(
                location in job_location for location in locations
            )
            if not locations:
                continue

        #Jobs passed all the filters
        filtered_jobs.append(Job)

    return filtered_jobs