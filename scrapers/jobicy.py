import requests
from utils import job_matches
import html


def fetch_jobicy(config):
    """Fetch jobs from Jobicy API.

    Jobicy is a remote-only job board with a free public API.
    Supports ?tag= for keyword filtering at the API level.
    Docs: https://jobicy.com/jobs-rss-feed
    """
    base_url = "https://jobicy.com/api/v2/remote-jobs"
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}
    max_results = config.get("max_results_per_board") or 50

    # Jobicy ?tag= accepts a single term per request.
    # Use broad terms that return the most relevant results.
    search_tags = ["machine learning", "artificial intelligence", "generative AI"]

    seen_ids = set()
    jobs = []

    for tag in search_tags:
        if len(jobs) >= max_results:
            break
        try:
            resp = requests.get(
                base_url,
                params={"count": 50, "tag": tag},
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  Jobicy tag={tag!r} failed: {e}")
            continue

        for item in data.get("jobs", []):
            if not isinstance(item, dict):
                continue

            job_id = item.get("id")
            if job_id and job_id in seen_ids:
                continue
            if job_id:
                seen_ids.add(job_id)

            title = html.unescape(item.get("jobTitle") or "")
            company = html.unescape(item.get("companyName") or "")
            location = item.get("jobGeo") or "Remote"
            description = html.unescape(item.get("jobExcerpt") or item.get("jobDescription") or "")
            url = item.get("url") or ""
            date_posted = item.get("pubDate") or ""
            tags = []
            if item.get("jobIndustry"):
                if isinstance(item["jobIndustry"], list):
                    tags.extend(item["jobIndustry"])
                else:
                    tags.append(str(item["jobIndustry"]))
            if item.get("jobType"):
                tags.append(str(item["jobType"]))

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

    return jobs
