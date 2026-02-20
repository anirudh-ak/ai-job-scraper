import requests
from utils import job_matches
import time


def fetch_himalayas(config):
    """Fetch AI/ML jobs from Himalayas.app using their public JSON API.

    Himalayas is a platform for remote-first companies with a free public API.
    They have ~113K jobs and explicitly allow scraping in robots.txt.
    """
    base_url = "https://himalayas.app/jobs/api"
    headers = {"User-Agent": "ai-job-scraper/1.0 (+https://github.com)"}
    
    jobs = []
    max_results = config.get("max_results_per_board") or 50
    limit = 20  # API max per request
    offset = 0
    
    # Himalayas API search doesn't reliably filter by keyword, so we fetch
    # broadly and rely on local title-based filtering. Use category param instead.
    search_query = None

    # Fetch up to 50 pages (1000 jobs) to find enough worldwide+matching titles.
    # Most jobs on Himalayas are country-restricted, so we need to scan broadly.
    max_pages = 50
    pages_fetched = 0

    try:
        while len(jobs) < max_results and pages_fetched < max_pages:
            url_params = f"limit={limit}&offset={offset}"
            resp = requests.get(
                f"{base_url}?{url_params}",
                headers=headers,
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()

            job_list = data.get("jobs", [])
            if not job_list:
                break

            for item in job_list:
                if len(jobs) >= max_results:
                    break

                if not _location_allowed(item, config):
                    continue

                job_data = _parse_himalayas_job(item)
                if job_data and job_matches(job_data, config):
                    jobs.append(job_data)

            offset += limit
            pages_fetched += 1

            # Rate limiting
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Error fetching from Himalayas: {e}")
    
    return jobs


def _location_allowed(item, config):
    """Return True only if the job has no location restrictions (truly worldwide).

    Empty locationRestrictions ([]) = open to everyone.
    Any non-empty list means the job is restricted to specific countries — skip it.
    """
    if not config.get("worldwide_only", True):
        return True  # location filtering disabled in config
    restrictions = item.get("locationRestrictions") or []
    return len(restrictions) == 0


def _parse_himalayas_job(item):
    """Parse a Himalayas API job response into our standard job dict."""
    try:
        title = item.get("title") or ""
        company = item.get("companyName") or ""
        
        # Location: use location restrictions if available (it's an array)
        location_restrictions = item.get("locationRestrictions", [])
        if isinstance(location_restrictions, list) and location_restrictions:
            location = ", ".join(str(x) for x in location_restrictions)
        else:
            location = "Remote"
        
        # Description: use full description or excerpt fallback
        description = item.get("description") or item.get("excerpt") or ""
        
        # Tags from categories
        tags = []
        categories = item.get("categories", [])
        if isinstance(categories, list):
            tags.extend(categories)
        
        # Seniority is an array, extract if present
        seniority = item.get("seniority", [])
        if isinstance(seniority, list) and seniority:
            tags.extend(seniority)
        
        if item.get("employmentType"):
            tags.append(item.get("employmentType"))
        
        # Application URL
        url = item.get("applicationLink") or ""
        
        # Publication date
        pub_date = item.get("pubDate") or ""
        
        job = {
            "title": title.strip(),
            "company": company.strip(),
            "location": location,
            "url": url,
            "date_posted": str(pub_date),
            "description": (description or "").strip()[:1000],
            "tags": tags,
        }
        
        # Only return if we have essential fields
        if job["title"] and job["company"]:
            return job
    
    except Exception:
        pass
    
    return None
