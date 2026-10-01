import json
import re

from langchain_groq import ChatGroq
from app.services.candidate_context import retrieve_candidate_context


def build_job_match_query(job: dict) -> str:
    """Build a semantic retrieval query for one specific job."""

    skills = ", ".join(job.get("required_skills", []))
    preferred_skills = ", ".join(job.get("preferred_skills", []))
    responsibilities = " ".join(job.get("responsibilities", []))
    keywords = ", ".join(job.get("keywords", []))
    experience = job.get("experience_required", "")

    return f"""
Find candidate evidence relevant to this specific job.

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

Prioritize concrete evidence of:
- professional experience
- projects actually built
- technologies actually used
- responsibilities actually performed

Do not treat a stated interest alone as hands-on experience.
"""


def retrieve_job_candidate_evidence(job: dict) -> str:
    """Retrieve candidate evidence specifically relevant to one job."""

    query = build_job_match_query(job)

    return retrieve_candidate_context(
        query=query,
        top_k=5,
    )


def match_candidate(
    job: dict,
    candidate_evidence: str,
    llm: ChatGroq,
) -> dict:
    """
    Evaluate candidate fit against a specific job.

    Evidence classification:
    - demonstrated: concrete evidence of usage/work
    - claimed: mentioned as a skill, interest, or knowledge,
      but insufficient concrete evidence
    - missing: no supporting evidence
    """

    prompt = f"""
You are an evidence-based candidate-job matching agent.

Your task is to evaluate the candidate against the job.

CRITICAL RULES:

1. Use ONLY the candidate evidence supplied below.
2. NEVER invent candidate experience.
3. Do NOT treat a general interest as demonstrated experience.
4. Do NOT treat a technology appearing in a skills list as
   automatically demonstrated.
5. A skill is "demonstrated" only when the evidence indicates
   the candidate actually used it in professional work or a
   concrete project.
6. A skill is "claimed" when it is listed as a skill, interest,
   learning area, or general capability but there is insufficient
   concrete evidence of usage.
7. A skill is "missing" when there is no supporting evidence.
8. Required skills matter more than preferred skills.
9. Consider the experience requirement separately.
10. Do not penalize the candidate for information that simply
    isn't present unless the job explicitly requires it.
11. Return ONLY valid JSON.
12. match_score must be an integer from 0 to 100.

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

{candidate_evidence}


For every important required skill, classify it as:

- demonstrated
- claimed
- missing

Use this exact JSON structure:

{{
    "match_score": 0,

    "skill_assessment": [
        {{
            "skill": "python",
            "status": "demonstrated",
            "evidence": "Concrete evidence from the candidate context"
        }}
    ],

    "matched_skills": [],
    "claimed_skills": [],
    "missing_skills": [],

    "experience_match": {{
        "status": "strong|partial|weak|unknown",
        "evidence": "Evidence supporting this assessment"
    }},

    "relevant_evidence": [],

    "reasoning": "Concise explanation of the overall match."
}}

IMPORTANT:

matched_skills must contain ONLY skills whose status is
"demonstrated".

claimed_skills must contain ONLY skills whose status is
"claimed".

missing_skills must contain ONLY skills whose status is
"missing".
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    # Remove accidental markdown code fences.
    content = re.sub(
        r"^```(?:json)?\s*",
        "",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r"\s*```$",
        "",
        content,
    ).strip()

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        print("⚠️ Candidate matcher returned invalid JSON:")
        print(content)

        result = {
            "match_score": 0,
            "skill_assessment": [],
            "matched_skills": [],
            "claimed_skills": [],
            "missing_skills": [],
            "experience_match": {
                "status": "unknown",
                "evidence": "",
            },
            "relevant_evidence": [],
            "reasoning": (
                "The candidate matcher returned invalid "
                "structured output."
            ),
        }

    # Normalize the output so downstream nodes can rely
    # on a predictable schema.
    return {
        "job_id": job.get("job_id"),
        "title": job.get("title"),
        "company": job.get("company"),
        "match_score": result.get("match_score", 0),
        "skill_assessment": result.get(
            "skill_assessment",
            [],
        ),
        "matched_skills": result.get(
            "matched_skills",
            [],
        ),
        "claimed_skills": result.get(
            "claimed_skills",
            [],
        ),
        "missing_skills": result.get(
            "missing_skills",
            [],
        ),
        "experience_match": result.get(
            "experience_match",
            {
                "status": "unknown",
                "evidence": "",
            },
        ),
        "relevant_evidence": result.get(
            "relevant_evidence",
            [],
        ),
        "reasoning": result.get(
            "reasoning",
            "",
        ),
    }