import requests
import time
from utils import job_matches


# AI/ML companies with confirmed Greenhouse job boards that have remote listings.
# Slug = the subdomain used in boards-api.greenhouse.io/v1/boards/<slug>/jobs
_COMPANIES = [
    "anthropic",
    "xai",           # xAI (Elon Musk's AI company)
    "databricks",
    "runwayml",
    "dataiku",
    "vercel",
    "snorkelai",
    "typeface",
    "comet",
]


def fetch_greenhouse(config):
    """Fetch remote AI/ML jobs from Greenhouse-hosted company job boards.

    Greenhouse is an ATS used by many tech/AI companies. Their public API
    at boards-api.greenhouse.io requires no authentication.
    We query each known company board and filter for remote roles.
    """
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}
    max_results = config.get("max_results_per_board") or 100
    seen_ids = set()
    jobs = []

    for slug in _COMPANIES:
        if len(jobs) >= max_results:
            break
        try:
            resp = requests.get(
                f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  Greenhouse {slug!r} failed: {e}")
            continue

        time.sleep(0.3)

        for item in data.get("jobs", []):
            if not isinstance(item, dict):
                continue

            job_id = item.get("id")
            if job_id and job_id in seen_ids:
                continue
            if job_id:
                seen_ids.add(job_id)

            title = item.get("title") or ""
            company = item.get("company_name") or slug
            location = item.get("location", {}).get("name") or ""

            # Only keep remote/worldwide roles
            if not _is_remote(location):
                continue

            url = item.get("absolute_url") or ""
            date_posted = item.get("first_published") or item.get("updated_at") or ""

            job = {
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "url": url,
                "date_posted": date_posted,
                "description": "",  # Greenhouse job detail requires a second API call; skip for speed
                "tags": [],
            }

            if job["title"] and job["company"] and job_matches(job, config):
                jobs.append(job)

            if len(jobs) >= max_results:
                break

    return jobs


def _is_remote(location):
    """Return True if the location indicates a globally open remote role.

    Accepts: "Remote", "Worldwide", "Remote - India", distributed, etc.
    Rejects: "Remote - California", "Remote - US", "New York (Remote)" — these
    are US/region-restricted even though they contain the word "remote".
    """
    loc = (location or "").lower()
    if not any(kw in loc for kw in ["remote", "worldwide", "anywhere", "distributed"]):
        return False

    # Reject if restricted to a specific US state or region
    us_states = [
        "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
        "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
        "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
        "maine", "maryland", "massachusetts", "michigan", "minnesota",
        "mississippi", "missouri", "montana", "nebraska", "nevada",
        "new hampshire", "new jersey", "new mexico", "new york", "north carolina",
        "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
        "rhode island", "south carolina", "south dakota", "tennessee", "texas",
        "utah", "vermont", "virginia", "washington", "west virginia",
        "wisconsin", "wyoming", "washington d.c.", "washington, d.c.",
    ]
    # Also reject city-specific locations in the US
    us_cities = ["san francisco", "new york", "seattle", "austin", "boston", "chicago"]

    for state in us_states + us_cities:
        if state in loc:
            return False

    return True
