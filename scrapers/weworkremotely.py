import requests
from bs4 import BeautifulSoup
from utils import job_matches
import time


def fetch_weworkremotely(config):
    """Fetch jobs from We Work Remotely by HTML scraping.

    We Work Remotely doesn't have a public API for browsing jobs, so we scrape
    their category/search pages and extract job listings from the HTML.
    """
    base_url = "https://weworkremotely.com"
    
    # Target categories that likely have AI/tech jobs
    categories = [
        "remote-software-development-jobs",  # Largest pool, includes AI roles
        "remote-devops-jobs",                 # Infrastructure engineers
        "remote-data-science-jobs",           # Data science roles
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://weworkremotely.com/",
    }
    
    jobs = []
    max_results = config.get("max_results_per_board") or 50
    
    for category in categories:
        if len(jobs) >= max_results:
            break
            
        try:
            url = f"{base_url}/categories/{category}"
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # Find job listing containers - typically <a> tags with specific classes
            # Job listings are in article/section containers with job data
            job_listings = soup.find_all("a", {"class": lambda x: x and "job-card" in x})
            
            if not job_listings:
                # Try alternate selector if the first one fails
                job_listings = soup.find_all("a", href=lambda x: x and "/remote-jobs/" in x)
            
            for listing in job_listings:
                if len(jobs) >= max_results:
                    break
                
                job_data = _parse_job_listing(listing, base_url)
                if job_data and job_matches(job_data, config):
                    jobs.append(job_data)
            
            # Be respectful with rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"Error scraping {category}: {e}")
            continue
    
    return jobs


def _parse_job_listing(element, base_url):
    """Extract job data from a job listing HTML element."""
    try:
        # Extract URL
        url = element.get("href", "")
        if not url.startswith("http"):
            url = base_url + url
        
        # Extract title (usually in h2 or strong tag)
        title_elem = element.find(["h2", "strong", "a"])
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # Extract company name (often in a separate element with specific class)
        company_elem = element.find("span", {"class": lambda x: x and "company" in (x or "").lower()})
        if not company_elem:
            company_elem = element.find("strong")
        company = company_elem.get_text(strip=True) if company_elem else ""
        
        # Extract posted date
        date_elem = element.find("span", {"class": lambda x: x and "date" in (x or "").lower()})
        date_posted = date_elem.get_text(strip=True) if date_elem else ""
        
        # Extract employment type/tags
        tags = []
        for tag_elem in element.find_all("span", {"class": lambda x: x and "badge" in (x or "").lower()}):
            tag_text = tag_elem.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)
        
        # Location is typically "Remote" or specific region
        location_elem = element.find("span", {"class": lambda x: x and "location" in (x or "").lower()})
        location = location_elem.get_text(strip=True) if location_elem else "Remote"
        
        # Get all text as description fallback
        description = element.get_text(separator=" ", strip=True)[:500]
        
        job = {
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip() or "Remote",
            "url": url,
            "date_posted": date_posted,
            "description": description,
            "tags": tags,
        }
        
        # Only return if we have essential fields
        if job["title"] and job["company"]:
            return job
        
    except Exception:
        pass
    
    return None

