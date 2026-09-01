from datetime import datetime
from pydantic import BaseModel, HttpUrl


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    url: HttpUrl
    description: str
    source: str
    posted_at: datetime | None = None