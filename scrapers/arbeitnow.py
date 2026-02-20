import requests
import time
from utils import job_matches


def fetch_arbeitnow(config):
    """Fetch jobs from Arbeitnow public API.

    Arbeitnow has a free public API with remote filtering and keyword search.
    Only returns jobs where remote=true. Uses a single broad search term to
    avoid rate-limiting from rapid multi-term requests.
    Docs: https://arbeitnow.com/api
    """
    base_url = "https://arbeitnow.com/api/job-board-api"
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}
    max_results = config.get("max_results_per_board") or 50

    # Single broad term to avoid rate-limiting — local filter handles precision
    search_terms = ["AI engineer"]

    seen_slugs = set()
    jobs = []

    for term in search_terms:
        if len(jobs) >= max_results:
            break

        page = 1
        while len(jobs) < max_results and page <= 3:  # cap at 3 pages to avoid rate limiting
            try:
                resp = requests.get(
                    base_url,
                    params={"search": term, "remote": "true", "page": page},
                    headers=headers,
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"  Arbeitnow term={term!r} page={page} failed: {e}")
                break
            time.sleep(1)  # be respectful, avoid 429s

            items = data.get("data", [])
            if not items:
                break

            for item in items:
                if not isinstance(item, dict):
                    continue

                # Skip non-remote jobs (extra safety check)
                if not item.get("remote"):
                    continue

                slug = item.get("slug") or ""
                if slug and slug in seen_slugs:
                    continue
                if slug:
                    seen_slugs.add(slug)

                title = item.get("title") or ""
                company = item.get("company_name") or ""
                location = item.get("location") or "Remote"
                description = item.get("description") or ""
                url = item.get("url") or ""
                date_posted = str(item.get("created_at") or "")
                tags = item.get("tags") or []

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

            # Check if there are more pages
            meta = data.get("meta", {})
            links = data.get("links", {})
            if not links.get("next"):
                break
            page += 1

    return jobs
