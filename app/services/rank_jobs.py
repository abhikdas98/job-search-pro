from app.models.job import Job, RankedJob


def get_profile_value(user_profile, field, default=None):
    return getattr(user_profile, field, default)


def rank_jobs(
    jobs: list,
    match_results: list[dict],
    user_profile: dict,
) -> list[dict]:
    """
    Rank jobs using candidate-job match results.

    Primary signal:
        - LLM-generated candidate match score

    Secondary signals:
        - Target role alignment
        - Location alignment
    """

    match_lookup = {
        str(result.get("job_id")): result
        for result in match_results
        if result.get("job_id") is not None
    }

    ranked_jobs = []

    for item in jobs:

        # --------------------------------------------------
        # Convert Job/Pydantic object into dictionary
        # --------------------------------------------------

        if isinstance(item, Job):
            job_dict = item.model_dump()

        elif hasattr(item, "model_dump"):
            job_dict = item.model_dump()

        elif isinstance(item, dict):
            job_dict = item

        else:
            continue

        job_id = str(
            job_dict.get("id")
            or job_dict.get("job_id")
        )

        match_result = match_lookup.get(job_id)

        # --------------------------------------------------
        # If no candidate match exists, skip the job
        # --------------------------------------------------

        if not match_result:
            continue

        # --------------------------------------------------
        # Candidate match score
        # --------------------------------------------------

        match_score = float(
            match_result.get("match_score", 0)
        )

        # --------------------------------------------------
        # Role alignment
        # --------------------------------------------------

        role_score = calculate_role_score(
            job_dict,
            user_profile
        )

        # --------------------------------------------------
        # Location alignment
        # --------------------------------------------------

        location_score = calculate_location_score(
            job_dict,
            user_profile
        )

        # --------------------------------------------------
        # Final ranking score
        # --------------------------------------------------
        #
        # Candidate-job fit is intentionally dominant.
        #
        # 80% → candidate match
        # 10% → role alignment
        # 10% → location alignment
        #
        # --------------------------------------------------

        final_score = (
            match_score * 0.80
            + role_score * 0.10
            + location_score * 0.10
        )

        final_score = round(final_score, 2)

        # --------------------------------------------------
        # Recreate Job model
        # --------------------------------------------------

        try:
            job = Job(**job_dict)

        except Exception:
            print(
                f"⚠️ Could not convert job "
                f"{job_id} into Job model."
            )
            continue

        ranked_job = RankedJob(
            job=job,
            score=final_score,
        )

        ranked_jobs.append({
            "job": ranked_job.job.model_dump(),
            "score": ranked_job.score,
            "match_score": match_score,
            "role_score": role_score,
            "location_score": location_score,
            "matched_skills": match_result.get(
                "matched_skills",
                []
            ),
            "claimed_skills": match_result.get(
                "claimed_skills",
                []
            ),
            "missing_skills": match_result.get(
                "missing_skills",
                []
            ),
            "experience_match": match_result.get(
                "experience_match",
                {}
            ),
            "reasoning": match_result.get(
                "reasoning",
                ""
            ),
            "relevant_evidence": match_result.get(
                "relevant_evidence",
                []
            ),
        })

    # ------------------------------------------------------
    # Highest score first
    # ------------------------------------------------------

    ranked_jobs.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked_jobs


def calculate_role_score(
    job: dict,
    user_profile: dict,
) -> float:

    target_roles = get_profile_value(
        user_profile,
        "target_roles",
        []
    )

    if not target_roles:
        return 0.0

    job_title = (
        job.get("title")
        or ""
    ).lower()

    for role in target_roles:

        role = role.lower().strip()

        if role in job_title:
            return 100.0

    return 0.0


def calculate_location_score(
    job: dict,
    user_profile: dict,
) -> float:

    locations = get_profile_value(
        user_profile,
        "locations",
        []
    )

    if not locations:
        return 0.0

    job_location = (
        job.get("location")
        or ""
    ).lower()

    for location in locations:

        if location.lower().strip() in job_location:
            return 100.0

    return 0.0
