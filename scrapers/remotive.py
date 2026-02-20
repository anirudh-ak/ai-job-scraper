import requests
from utils import job_matches


def fetch_remotive(config):
    """Fetch jobs from Remotive API and return a list of job dicts.

    Remotive provides a free API for remote jobs with fields like:
    title, company_name, url, location, description, tags (category, sub_category)
    """
    url = "https://remotive.io/api/remote-jobs"
    # Use API-level search to pre-filter results before local filtering.
    # Remotive supports ?search= (free text) and ?category= (slug).
    # We search for "AI" which covers most relevant listings.
    params = {
        "limit": (config.get("max_results_per_board") or 50) * 3,  # fetch more to allow post-filter
        "search": "AI OR machine learning OR LLM OR GenAI",
        "category": "software-dev",  # narrows to tech roles
    }
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    jobs = []
    max_results = config.get("max_results_per_board") or 50

    for item in data.get("jobs", []):
        if not isinstance(item, dict):
            continue

        title = item.get("title") or ""
        company = item.get("company_name") or ""
        location = item.get("location") or ""
        description = item.get("description") or ""
        
        # Remotive has category/sub_category; add them as pseudo-tags
        tags = []
        if item.get("category"):
            tags.append(item.get("category"))
        if item.get("sub_category"):
            tags.append(item.get("sub_category"))

        url_field = item.get("url") or ""

        job = {
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": url_field,
            "date_posted": item.get("published_at") or item.get("created_at") or "",
            "description": (description or "").strip(),
            "tags": tags,
        }

        if job_matches(job, config):
            jobs.append(job)

        if len(jobs) >= max_results:
            break

    return jobs
