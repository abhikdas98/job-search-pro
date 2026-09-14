import os
from datetime import datetime
from typing import Any

import httpx
from dotenv import load_dotenv

from app.models.job import Job

load_dotenv()

class AdzunaJobSource:
    """
    Job source for retrieving the job listings from the Adzuna API.
    """

    BASE_URL = "https://api.adzuna.com/v1/api"

    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")

        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna API credentials are not set in the environment variables.")

    def search(
            self,
            query: str,
            location: str,
            country: str = "in",
            page: int = 1,
            results_per_page: int = 20,
    ) -> list[Job]:
        """
        Search Adzuna for jobs and convert the results
        into our standardized Job model.
        """

        url = (
            f"{self.BASE_URL}/jobs"
            f"/{country}/search/{page}"
        )

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": results_per_page,
            "what": query,
            "where": location,
            "content-type": "application/json",
        }

        if location:
            params["where"] = location

        try:
            response = httpx.get(
                url,
                params=params,
                timeout=20.0,
                )
            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Adzuna API request failed: {exc}"
            ) from exc

        data = response.json()

        return [
            self._normalize_job(job)
            for job in data.get("results", [])
        ]

    @staticmethod
    def _normalize_job(job: dict[str, Any]) -> Job:
        """
        Convert an Adzuna job response into our
        standardized Job model.
        """
        company = job.get("company") or {}
        location = job.get("location") or {}

        posted_at = None
        created = job.get("created")

        if created:
            try:
                posted_at = datetime.fromisoformat(
                    created.replace("Z", "+00:00")
                    )
            except ValueError:
                posted_at = None

        return Job(
            id = job.get("id", ""),
            title = job.get("title", ""),
            company = company.get("display_name", "Unknown"),
            location = location.get("display_name", "Unknown"),
            url = job.get("redirect_url", ""),
            description = job.get("description", ""),
            source = "adzuna",
            posted_at = posted_at,
        )
    