from app.models.job import Job, RankedJob
import re

def rank_jobs(
        jobs: list[Job],
        user_profile: dict
) -> list[Job]:
    """
    Rank jobs based on the user's preferences and requirements.

    Args:
        jobs: List of normalized Job objects.
        user_profile: Structured user preferences.
        """

    ranked_jobs = []
    for job in jobs:
        #Calculate score based on the user's preferences and requirements
        job_score = calculate_job_score(job, user_profile)

        ranked_jobs.append(RankedJob(job=job, score=job_score))

    ranked_jobs.sort(key=lambda ranked_job: ranked_job.score, reverse=True)
    return ranked_jobs

def calculate_job_score(job: Job, user_profile: dict) -> float:
    role_score = calculate_role_score(job, user_profile)
    skill_score = calculate_skill_score(job, user_profile)
    experience_score = calculate_experience_score(job, user_profile)
    location_score = calculate_location_score(job, user_profile)

    total_score =(
        
        role_score * 0.4 +
        skill_score * 0.3 +
        experience_score * 0.2 +
        location_score * 0.1
    )

    return round(total_score, 2)

def calculate_role_score(
        job: Job,
        user_profile: dict
) -> float:
    target_roles = user_profile.get("target_roles", [])
    if not target_roles:
        return 0.0

    job_title = job.title.lower()
    role_match = any(
        role.lower() in job_title for role in target_roles
    )
    return 1.0 if role_match else 0.0

def calculate_skill_score(
        job: Job,
        user_profile: dict
) -> float:
    user_skills = user_profile.get("skills", [])
    if not user_skills:
        return 0.0

    job_text = (
        f"{job.title} {job.description}"
    ).lower()

    pattern = rf"\b{re.escape(user_skills.lower())}\b"

    if re.search(pattern, job_text):
        total_matches += 1

        return total_matches / len(user_skills) * 1.0

    return 0.0

def calculate_experience_score(
        job: Job,
        user_profile: dict
) -> float:
    user_experience = user_profile.get("experience", None)

    if not user_experience:
        return 0.0

    job_text = (
        f"{job.title} {job.description}"
    ).lower()

    if user_experience.lower() in job_text:
        return 1.0
    return 0.0

def calculate_location_score(
        job: Job,
        user_profile: dict
) -> float:
    preferred_location = user_profile.get("locations", [])

    if not preferred_location:
        return 0.0
    job_location = job.location.lower()

    for location in preferred_location:
        if location.lower() in job_location:
            return 1.0
    return 0.0