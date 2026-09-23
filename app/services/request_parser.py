from typing import Optional
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    """Structured representation of the user's job search preference"""
    target_roles: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    remote_preference: str | None = Field(default=None, description="Remote, Hybrid, or On-site preference if stated")
    experience_years: str | None = Field(default=None)
    skills: list[str] = Field(default_factory=list, description="List of skills if stated")
    employment_type: str | None = Field(default=None, description="Full-time, Part-time, Contract, etc.")
    minimum_salary: str | None = Field(default=None, description="Minimum salary expectation if stated")

class RequestParser:
    """
    Parse the user request and resume context into a structured UserProfile
    """
    def __init__(self, llm):
        self.llm = llm

    #  UPDATED: Accepting both user_request and resume_context parameters
    def parse(self, user_request: str, resume_context: str) -> UserProfile:
        prompt = f"""
        You are an expert HR data parsing agent. Your task is to extract job-search preferences 
        by combining the raw user input request with the background context extracted from the candidate's profile/resume.

        User Request:
        "{user_request}"

        Retrieved Candidate Resume Context (RAG):
        {resume_context}

        Extraction Instructions:
        1. target_roles: Extract roles explicitly requested in the chat message, supplemented by matching experience fields in the resume context.
        2. locations: Look at where the candidate wants to apply based on their request.
        3. skills: Cross-reference skills requested in the chat with the candidate's actual skills listed in the resume context. Extract relevant technical strings.
        4. experience_years: Look up years of experience inside the resume context if not explicitly mentioned in the request message.
        5. If list fields (target_roles, locations, skills) have no information, return an empty array []. Do NOT use null.
        6. If any scalar fields (remote_preference, experience_years, employment_type, minimum_salary) are missing, return null.
        
        Only extract information stated or clearly implied across either text context blocks.
        """

        structured_llm = self.llm.with_structured_output(UserProfile)
        return structured_llm.invoke(prompt)
