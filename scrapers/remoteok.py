import requests
from utils import job_matches


def fetch_remoteok(config):
    """Fetch jobs from RemoteOK API and return a list of job dicts.

    Each job dict contains: title, company, location, url, date_posted, description, tags
    """
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    jobs = []
    max_results = config.get("max_results_per_board") or 50

    # RemoteOK API returns a list where first element is often a meta object; skip entries without a company/position
    for item in data:
        if not isinstance(item, dict):
            continue
        # Skip the meta element
        if item.get("id") is None and item.get("company") is None and item.get("position") is None:
            continue

        title = item.get("position") or item.get("title") or ""
        company = item.get("company") or ""
        location = item.get("location") or item.get("location_text") or ""
        description = item.get("description") or item.get("tags_text") or ""
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
            "description": (description or "").strip(),
            "tags": tags,
        }

        if job_matches(job, config):
            jobs.append(job)

        if len(jobs) >= max_results:
            break

    return jobs
