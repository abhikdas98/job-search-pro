from app.models.job import Job


def filtered_jobs(
    jobs: list[Job],
    user_profile
) -> list[Job]:
    """
    Filter jobs based on the user's explicit preferences.
    """

    filtered = []

    target_roles = [
        role.lower()
        for role in user_profile.target_roles
    ]

    locations = [
        location.lower()
        for location in user_profile.locations
    ]

    for job in jobs:

        # Role filter
        if target_roles:
            job_title = job.title.lower()

            role_match = any(
                role in job_title
                for role in target_roles
            )

            if not role_match:
                continue

        # Location filter
        if locations:
            job_location = job.location.lower()

            location_match = any(
                location in job_location
                for location in locations
            )

            if not location_match:
                continue

        filtered.append(job)

    return filtered