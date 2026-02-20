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
    
    # Build a search query from the first few job_keywords to pre-filter at API level
    job_keys = config.get("job_keywords") or []
    search_query = " OR ".join(job_keys[:5]) if job_keys else "AI"

    try:
        while len(jobs) < max_results:
            resp = requests.get(
                f"{base_url}?limit={limit}&offset={offset}&q={requests.utils.quote(search_query)}",
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
                
                job_data = _parse_himalayas_job(item)
                if job_data and job_matches(job_data, config):
                    jobs.append(job_data)
            
            offset += limit
            
            # Rate limiting - reduced for faster execution
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Error fetching from Himalayas: {e}")
    
    return jobs


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
