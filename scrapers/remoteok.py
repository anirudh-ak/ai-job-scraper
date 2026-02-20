import requests
import time
from utils import job_matches


# RemoteOK tag slugs that map to AI/ML roles. The API supports tag-based
# endpoints like /api?tags=machine-learning,ai which pre-filter at source.
_TAG_SEARCHES = [
    "machine-learning",
    "ai",
    "llm",
    "nlp",
    "deep-learning",
]


def fetch_remoteok(config):
    """Fetch jobs from RemoteOK API using tag-based endpoints.

    RemoteOK supports /api?tags=<tag> to pre-filter by role category.
    All RemoteOK jobs are remote and globally open unless stated otherwise.
    """
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}
    max_results = config.get("max_results_per_board") or 100
    seen_ids = set()
    jobs = []

    for tag in _TAG_SEARCHES:
        if len(jobs) >= max_results:
            break
        try:
            resp = requests.get(
                f"https://remoteok.com/api?tags={tag}",
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  RemoteOK tag={tag!r} failed: {e}")
            continue

        time.sleep(1)  # RemoteOK rate limits aggressively

        for item in data:
            if not isinstance(item, dict):
                continue
            if item.get("id") is None:
                continue

            job_id = item.get("id")
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = item.get("position") or item.get("title") or ""
            company = item.get("company") or ""
            location = item.get("location") or item.get("location_text") or "Worldwide"
            description = item.get("description") or ""
            tags = item.get("tags") or []

            url_field = item.get("url") or item.get("link") or ""
            if url_field and url_field.startswith("/"):
                url_field = "https://remoteok.com" + url_field

            job = {
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "url": url_field,
                "date_posted": item.get("date") or item.get("date_posted") or "",
                "description": (description or "").strip()[:1000],
                "tags": tags,
            }

            if job["title"] and job["company"] and job_matches(job, config):
                jobs.append(job)

            if len(jobs) >= max_results:
                break

    return jobs
