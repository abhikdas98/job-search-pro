from typing_extensions import TypedDict
from app.models.job import Job

class State(TypedDict):
    user_request: str
    user_profile: dict
    jobs: list[Job]
    selected_jobs: list[Job]