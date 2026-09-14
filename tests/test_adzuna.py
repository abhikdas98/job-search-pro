from app.tools.job_search.adzuna import AdzunaJobSource


source = AdzunaJobSource()

jobs = source.search(
    query="Generative AI Engineer",
    location="Bangalore",
)

for job in jobs:
    print("=" * 80)
    print(f"Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"Location: {job.location}")
    print(f"URL: {job.url}")
    print(f"Source: {job.source}")
    print(f"Posted: {job.posted_at}")