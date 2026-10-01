import json
import re
import time

from langchain_groq import ChatGroq
from app.services.candidate_context import retrieve_candidate_context

MAX_MATCH_RETRIES = 3


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
        top_k=3,
    )


def _rate_limit_fallback(job: dict, error: Exception) -> dict:
    """Return a safe result when the LLM cannot be called."""
    return {
        "job_id": job.get("job_id"),
        "title": job.get("title"),
        "company": job.get("company"),
        "match_score": 0,
        "skill_assessment": [],
        "matched_skills": [],
        "claimed_skills": [],
        "missing_skills": [],
        "experience_match": {
            "status": "unknown",
            "evidence": "Candidate matching was unavailable.",
        },
        "relevant_evidence": [],
        "reasoning": (
            "Candidate matching was skipped because the LLM rate limit "
            f"was reached: {error}"
        ),
    }


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

Use ONLY the candidate evidence below.
Never invent experience.

Classify important required skills as:
- demonstrated = concrete professional/project usage
- claimed = mentioned but insufficient concrete evidence
- missing = no supporting evidence

Required skills matter more than preferred skills.
Consider experience separately.

Return ONLY valid JSON.
match_score must be an integer from 0 to 100.

JOB
===
Title: {job.get("title", "")}
Company: {job.get("company", "")}
Location: {job.get("location", "")}
Required skills: {job.get("required_skills", [])}
Preferred skills: {job.get("preferred_skills", [])}
Experience required: {job.get("experience_required", "")}
Responsibilities: {job.get("responsibilities", [])}
Keywords: {job.get("keywords", [])}

CANDIDATE EVIDENCE
==================
{candidate_evidence}

Return:

{{
    "match_score": 0,
    "skill_assessment": [
        {{
            "skill": "python",
            "status": "demonstrated",
            "evidence": "Concrete evidence"
        }}
    ],
    "matched_skills": [],
    "claimed_skills": [],
    "missing_skills": [],
    "experience_match": {{
        "status": "strong|partial|weak|unknown",
        "evidence": "Evidence"
    }},
    "relevant_evidence": [],
    "reasoning": "Concise explanation"
}}

matched_skills = demonstrated only.
claimed_skills = claimed only.
missing_skills = missing only.
Keep reasoning concise.
"""

    for attempt in range(1, MAX_MATCH_RETRIES + 1):
        try:
            response = llm.invoke(
                prompt,
                max_tokens=1200,
            )
            break

        except Exception as error:
            error_text = str(error).lower()
            is_rate_limit = (
                "429" in error_text
                or "rate_limit" in error_text
            )

            if not is_rate_limit:
                raise

            if attempt >= MAX_MATCH_RETRIES:
                print(
                    f"⚠️ Groq rate limit persisted for "
                    f"{job.get('title')} @ {job.get('company')}. "
                    "Using fallback match result and continuing."
                )
                return _rate_limit_fallback(job, error)

            retry_match = re.search(
                r"try again in\s+([0-9]+(?:\.[0-9]+)?)s",
                str(error),
                flags=re.IGNORECASE,
            )

            if retry_match:
                delay = float(retry_match.group(1)) + 0.5
            else:
                delay = min(2 ** attempt, 10)

            print(
                f"⏳ Groq rate limit hit. "
                f"Retrying in {delay:.1f}s..."
            )
            time.sleep(delay)

    content = response.content.strip()

    content = re.sub(
        r"^```(?:json)?\s*",
        "",
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(r"\s*```$", "", content).strip()

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
                "The candidate matcher returned invalid structured output."
            ),
        }

    return {
        "job_id": job.get("job_id"),
        "title": job.get("title"),
        "company": job.get("company"),
        "match_score": result.get("match_score", 0),
        "skill_assessment": result.get("skill_assessment", []),
        "matched_skills": result.get("matched_skills", []),
        "claimed_skills": result.get("claimed_skills", []),
        "missing_skills": result.get("missing_skills", []),
        "experience_match": result.get(
            "experience_match",
            {"status": "unknown", "evidence": ""},
        ),
        "relevant_evidence": result.get("relevant_evidence", []),
        "reasoning": result.get("reasoning", ""),
    }