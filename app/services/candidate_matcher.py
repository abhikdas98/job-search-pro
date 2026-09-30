def build_job_match_query(job: dict) -> str:
    """
    Build a retrieval query from the structured job requirements.
    """

    skills = ", ".join(
        job.get("required_skills", [])
    )

    preferred = ", ".join(
        job.get("preferred_skills", [])
    )

    responsibilities = " ".join(
        job.get("responsibilities", [])
    )

    keywords = ", ".join(
        job.get("keywords", [])
    )

    return f"""
    Candidate experience relevant to this job.

    Job title:
    {job.get("title", "")}

    Required skills:
    {skills}

    Preferred skills:
    {preferred}

    Responsibilities:
    {responsibilities}

    Keywords:
    {keywords}

    Experience requirement:
    {job.get("experience_required", "")}

    Find evidence from the candidate's resume, professional
    experience, and projects that is relevant to these requirements.
    """