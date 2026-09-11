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
    Parse the user request into a structured UserProfile
    """
    def __init__(self, llm):
        self.llm = llm

    def parse(self, user_request: str) -> UserProfile:
        prompt = f""""
        Extract the following job-search preferences from the following user request.

        User request:
        {user_request}

        Extract:
        -target_roles 
        -locations
        -remote_preference
        -experience_years
        -skills
        -employment_type
        -minimum_salary

        Only extract information stated or clearly implied.
        If list fields (target_roles, locations, skills) have no information, return an empty array []. Do NOT use null.
        If information is missing, leave it empty/null.
        """

        structured_llm = self.llm.with_structured_output(UserProfile)
        return structured_llm.invoke(prompt)