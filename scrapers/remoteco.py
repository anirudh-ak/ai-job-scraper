import requests
from bs4 import BeautifulSoup
from utils import job_matches
import time


def fetch_remoteco(config):
    """Fetch jobs from remote.co using HTML scraping.

    remote.co is a job board with 100+ categories of remote jobs.
    No public API, but clean HTML structure and explicitly allows scraping in robots.txt.
    """
    base_url = "https://remote.co"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    # AI/ML/Data related categories
    categories = [
        "software-development-jobs",
        "data-science-jobs",
        "artificial-intelligence-jobs",
        "machine-learning-jobs",
    ]
    
    jobs = []
    max_results = config.get("max_results_per_board") or 50
    
    for category in categories:
        if len(jobs) >= max_results:
            break
        
        try:
            page = 1
            while len(jobs) < max_results:
                url = f"{base_url}/remote-jobs/{category}?page={page}"
                resp = requests.get(url, headers=headers, timeout=15)
                resp.raise_for_status()
                
                soup = BeautifulSoup(resp.content, "html.parser")
                
                # Look for job listings/cards
                job_elements = soup.find_all("a", {"class": lambda x: x and "job-item" in x})
                
                if not job_elements:
                    # Try alternate selector
                    job_elements = soup.find_all("div", {"class": lambda x: x and "job-card" in x})
                
                if not job_elements:
                    break  # No more jobs on this page
                
                for elem in job_elements:
                    if len(jobs) >= max_results:
                        break
                    
                    job_data = _parse_remoteco_job(elem, base_url)
                    if job_data and job_matches(job_data, config):
                        jobs.append(job_data)
                
                page += 1
                time.sleep(2)  # Be respectful with rate limiting
        
        except Exception as e:
            print(f"Error scraping {category}: {e}")
            continue
    
    return jobs


def _parse_remoteco_job(element, base_url):
    """Extract job data from a remote.co job listing element."""
    try:
        # Get title
        title_elem = element.find(["h2", "h3", "strong"])
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # Get company
        company_elem = element.find("span", {"class": lambda x: x and "company" in (x or "").lower()})
        if not company_elem:
            company_elem = element.find("div", {"class": lambda x: x and "company" in (x or "").lower()})
        company = company_elem.get_text(strip=True) if company_elem else ""
        
        # Get URL
        url = ""
        url_elem = element.find("a", href=True)
        if url_elem:
            url = url_elem.get("href", "")
            if url and not url.startswith("http"):
                url = base_url + url
        
        # Get location
        location_elem = element.find("span", {"class": lambda x: x and "location" in (x or "").lower()})
        if not location_elem:
            location_elem = element.find("div", {"class": lambda x: x and "location" in (x or "").lower()})
        location = location_elem.get_text(strip=True) if location_elem else "Remote"
        
        # Get salary (optional)
        salary_elem = element.find("span", {"class": lambda x: x and "salary" in (x or "").lower()})
        salary = salary_elem.get_text(strip=True) if salary_elem else ""
        
        # Get date posted
        date_elem = element.find("span", {"class": lambda x: x and "date" in (x or "").lower()})
        date_posted = date_elem.get_text(strip=True) if date_elem else ""
        
        # Extract tags/badges
        tags = []
        for badge in element.find_all("span", {"class": lambda x: x and ("badge" in x or "tag" in x)}):
            tag_text = badge.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)
        
        # Get full text as fallback description
        description = element.get_text(separator=" ", strip=True)[:500]
        
        job = {
            "title": title.strip(),
            "company": company.strip(),
            "location": location,
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
