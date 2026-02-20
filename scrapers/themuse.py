import requests
from utils import job_matches


# The Muse categories most relevant to AI/ML roles
_CATEGORIES = [
    "Data Science",
    "Software Engineer",
]

# Only surface mid/senior roles
_LEVELS = [
    "Senior Level",
    "Manager",
]


def fetch_themuse(config):
    """Fetch jobs from The Muse public API.

    The Muse has a free public API that supports category and level filtering.
    No API key required for basic access.
    Docs: https://www.themuse.com/developers/api/v2
    """
    base_url = "https://www.themuse.com/api/public/jobs"
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}
    max_results = config.get("max_results_per_board") or 50

    seen_ids = set()
    jobs = []

    for category in _CATEGORIES:
        if len(jobs) >= max_results:
            break
        for level in _LEVELS:
            if len(jobs) >= max_results:
                break

            page = 0
            while len(jobs) < max_results and page < 3:  # cap at 3 pages per combo
                try:
                    resp = requests.get(
                        base_url,
                        params={"category": category, "level": level, "page": page},
                        headers=headers,
                        timeout=15,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as e:
                    print(f"  TheMuse category={category!r} level={level!r} page={page} failed: {e}")
                    break

                results = data.get("results", [])
                if not results:
                    break

                for item in results:
                    if not isinstance(item, dict):
                        continue

                    job_id = item.get("id")
                    if job_id and job_id in seen_ids:
                        continue
                    if job_id:
                        seen_ids.add(job_id)

                    title = item.get("name") or ""
                    company = item.get("company", {}).get("name") or ""

                    # Location: The Muse returns a list of location dicts
                    locations = item.get("locations") or []
                    location_names = [loc.get("name", "") for loc in locations if loc.get("name")]
                    location = ", ".join(location_names) if location_names else "Remote"

                    # The Muse isn't remote-only; include jobs with "Remote" or
                    # "Flexible" in location, or jobs with no location specified.
                    # The job title filter is the primary quality signal.
                    is_remote = (
                        not location_names
                        or any("remote" in ln.lower() or "flexible" in ln.lower()
                               for ln in location_names)
                    )
                    if not is_remote:
                        continue

                    description = item.get("contents") or ""
                    url = item.get("refs", {}).get("landing_page") or ""
                    date_posted = item.get("publication_date") or ""

                    # Tags from categories
                    tags = [c.get("name", "") for c in (item.get("categories") or [])]

                    job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location,
                        "url": url,
                        "date_posted": date_posted,
                        "description": description.strip()[:1000],
                        "tags": tags,
                    }

                    if job["title"] and job["company"] and job_matches(job, config):
                        jobs.append(job)

                    if len(jobs) >= max_results:
                        break

                # Move to next page if there is one
                if page >= data.get("page_count", 1) - 1:
                    break
                page += 1

    return jobs
