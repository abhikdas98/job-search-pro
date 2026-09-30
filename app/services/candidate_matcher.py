from app.services.candidate_context import (
    retrieve_candidate_context
)

import re
import json
from langchain_groq import ChatGroq


def build_job_match_query(job: dict) -> str:
    """
    Build a semantic retrieval query from the structured
    requirements of a job.
    """

    skills = ", ".join(
        job.get("required_skills", [])
    )

    preferred_skills = ", ".join(
        job.get("preferred_skills", [])
    )

    responsibilities = " ".join(
        job.get("responsibilities", [])
    )

    keywords = ", ".join(
        job.get("keywords", [])
    )

    experience = job.get(
        "experience_required",
        ""
    )

    return f"""
    Find candidate experience, projects, skills, and
    professional background relevant to this job.

    Job title:
    {job.get("title", "")}

    Required skills:
    {skills}

    Preferred skills:
    {preferred_skills}

    Responsibilities:
    {responsibilities}

    Keywords:
    {keywords}

    Experience required:
    {experience}
    """


def retrieve_job_candidate_evidence(
    job: dict
) -> str:
    """
    Retrieve candidate evidence specifically relevant
    to this job.
    """

    query = build_job_match_query(job)

    return retrieve_candidate_context(
        query=query,
        top_k=5,
    )

def match_candidate(
        job: dict,
        candidate_evidance: str,
        llm: ChatGroq,
) -> dict:
    """
    Evaluate candidate fit against a specific job.

    The model must use only the retrieved candidate
    evidance and must not invent experience.
    """
    prompt = f"""

You are an AI job matching agent.

Evaluate how well the candidate matches the job.

IMPORTANT RULES:

- Use ONLY the candidate evidance provided below.
- Do not invent skills, projects, experience, or qualifications.
- Distinguish clearly between demonstrated skills and missing skills.
- A skill should only be considerred matched when there is
evidance supporting it.
- Consider required skills more important than preferred skills.
- Consider experience requirements separately.
- Return ONLY valid JSON.
- match_score must be an integer from 0 to 100.

JOB
===

Title:
{job.get("title", "")}

Company:
{job.get("company", "")}

Location:
{job.get("location", "")}

Required skills:
{job.get("required_skills", [])}

Preferred skills:
{job.get("preferred_skills", [])}

Experience required:
{job.get("experience_required", "")}

Responsibilities:
{job.get("responsibilities", [])}

Keywords:
{job.get("keywords", [])}

CANDIDATE EVIDENCE
==================

{candidate_evidance}

Return exactly this JSON structure:

{{
    "match_score: 0,
    "matched_skills: [],
    "missing_skills": [],
    "relevanta_evidance": "",
    "reasoning": "",
}}
"""

    response = llm.invoke(prompt)

    content = response.content

    # Remove accidental markdown code fences
    content = re.sub(
        r"```json\s*|\s*```",
        "",
        content,
        flags=re.IGNORECASE,
    ).strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "relevant_evidence": [],
            "experience_match": "",
            "reasoning": content,
        }

    return {
        "job_id": job.get("job_id"),
        "title": job.get("title"),
        "company": job.get("company"),
        **result,
    }