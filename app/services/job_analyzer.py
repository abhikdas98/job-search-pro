import re
from app.models.job import Job

known_skills = [
    "python",
    "sql",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "scikit-learn",
    "xgboost",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "generative ai",
    "genai",
    "llm",
    "llms",
    "rag",
    "langchain",
    "langgraph",
    "agentic ai",
    "multi-agent",
    "prompt engineering",
    "fastapi",
    "flask",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "mongodb",
    "mysql",
    "postgresql",
    "kafka",
    "mlflow",
    "power bi",
    "excel",
]

PREFERRED_SECTION_MARKERS = [
    "preferred",
    "preferred qualifications",
    "nice to have",
    "good to have",
    "desired",
    "bonus",
    "plus",
]


REQUIRED_SECTION_MARKERS = [
    "required",
    "required skills",
    "requirements",
    "must have",
    "must-have",
    "qualifications",
    "minimum qualifications",
]


RESPONSIBILITY_MARKERS = [
    "responsibilities",
    "responsibility",
    "what you'll do",
    "what you will do",
    "key responsibilities",
    "role responsibilities",
]

def extract_skills(text: str) -> list[str]:
    """Extract known technical skills from the job text"""

    text_lower = text.lower()
    found = []

    for skill in known_skills:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        if re.search(pattern, text_lower):
            found.append(skill)
    return found

def extract_experience(text: str) -> str | None:
    """
    Extract common experience requirements such as:
    '2-3 years', '3+ years', 5 years, etc.
    """
    patterns = [
        r"\b\d+\s*-\s*\d+\s+years?\b",
        r"\b\d+\s*\+\s*years?\b",
        r"\b\d+\s+years?\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags= re.IGNORECASE
        )
        
        if match:
            return match.group(0)
    return None

def _find_section(
        text: str,
        markers: list[str]
) -> str:
    """
    Return a small section of text around a matching marker.

    This is intentionally lightweight. It gives us a better signal
    for distinguishing required vs preferred skills without relying
    on an LLM yet.
    """
    text_lower = text.lower()

    for marker in markers:
        index = text_lower.find(marker)

        if index == -1:
            continue

        start = max(0, index - 100)
        end = min(len(text), index + 1200)

        return text[start:end]

    return ""

def extract_required_skills(text: str) -> list[str]:
    """
    Rxtract skills from the requirements-related sections.

    If no explicit requirements section exists, fallback to
    the skills found in the complete job description.
    """
    section = _find_section(
        text,
        REQUIRED_SECTION_MARKERS,
    )

    if section:
        skills = extract_skills(section)

        if skills:
            return skills

    return extract_skills(text)

def extract_preferred_skills(text: str) -> list[str]:
    """Extract skills from the preferred/nice-to-have section."""

    section = _find_section(
        text,
        PREFERRED_SECTION_MARKERS,
    )

    if not section:
        return []
    
    return extract_skills(section)

def extract_responsibilities(text: str) -> list[str]:
    """
    Extract simple bullet-style responsibilities from a
    responsibility section.
    """
    section = _find_section(
        text,
        RESPONSIBILITY_MARKERS,
    )

    if not section:
        return []
    
    lines = section.splitlines()

    responsibilities = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        #Remove common bullet characters.
        line = re.sub(
            r"^[•\-*▪◦]+\s*",
            "",
            line
        )

        if len(line) < 25:
            continue

        if len(line) > 250:
            line = line[:250].rstrip() + "..."

        responsibilities.append(line)

        if len(responsibilities) >= 8:
            break

    return responsibilities

def extract_keywords(text: str) -> list[str]:
    """
    Extract high-level AI/engineering keywords from the job.
    """
    keyword_patterns = [
        "ai",
        "artificial intelligence",
        "generative ai",
        "genai",
        "llm",
        "llms",
        "rag",
        "agentic ai",
        "machine learning",
        "deep learning",
        "nlp",
        "computer vision",
        "prompt engineering",
        "ai agents",
        "multi-agent",
        "mcp",
        "model deployment",
        "mlops",
        "llmops",
        "cloud",
        "api",
        "microservices",
    ]

    found = []

    text_lower = text.lower()

    for keyword in keyword_patterns:
        if keyword in text_lower:
            found.append(keyword)
    return found

def analyze_job(job: Job) -> dict:
    """Convert a job object into structured job requirements"""

    text = f"""
        {job.title}
        {job.description}
        """

    required_skills = extract_required_skills(text)
    preferred_skills = extract_preferred_skills(text)

    # Prevent the same skill from appearing in both lists.
    preferred_skills = [
        skill
        for skill in preferred_skills
        if skill not in required_skills
    ]

    return {
        "job_id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_required": extract_experience(text),
        "responsibilities": extract_responsibilities(text),
        "keywords": extract_keywords(text),
        "description": job.description,
    }