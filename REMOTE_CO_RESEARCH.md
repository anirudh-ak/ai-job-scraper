# Remote.co Scraping Research Report

## Executive Summary
**Remote.co has NO public API** but features a predictable URL structure with minimal anti-bot protection on job listing pages. The site is fully scrapable via HTML parsing with careful rate limiting.

---

## 1. API Availability

### Finding: NO PUBLIC API
- ❌ No documented public API
- ❌ No GraphQL endpoint
- ❌ No REST API endpoint

### robots.txt Restrictions
```
Disallow:/ej/api/*      # Internal API (blocked)
Disallow:/eb/api/*      # Internal API (blocked)
```
These internal APIs exist but are explicitly blocked from scraping. Attempting to access these will violate robots.txt.

---

## 2. HTML/DOM Structure

### Job Listing Cards
Each job on category pages has this structure:
```html
<!-- Company Logo -->
<img src="data:image/gif;..." alt="CompanyName">

<!-- Job Title (links to detail page) -->
<a href="/job-details/[slug-with-uuid]">Job Title</a>

<!-- Company Name -->
<h3>Company Name</h3>

<!-- Remote Level -->
<span>100% Remote Work</span> | <span>Hybrid Remote Work</span>

<!-- Employment Type -->
<span>Full-Time</span> | <span>Part-Time</span>

<!-- Location -->
<span>Remote, US National</span>

<!-- Salary (optional) -->
<span>$70 - $80 Hourly</span>
<span>$120,000 Annually</span>

<!-- Date Posted -->
<span>TodayNEW!</span> | <span>Yesterday</span>

<!-- Save Job Button (requires signup) -->
<a href="/signup">Save Job</a>
```

### Individual Job Detail Page Structure
```
Title: {job_title}
Company: {company_name}
Company Link: /company/{company_slug}

Metadata:
- Date Posted: Today/Yesterday
- Remote Work Level: 100% Remote, Hybrid, etc.
- Location: {location}
- Job Schedule: Full-Time, Part-Time, Freelance
- Salary: {salary_range_or_hourly}

Job Content:
- About the Role
  - Job Title
  - Type (e.g., "Consulting")
  - Category (e.g., "Development")
  - Industry
  - Workplace Type
  - Reference ID
  - Description
  - Responsibilities
  - Experience Requirements

Benefits (if listed):
- Health Insurance
- Dental Insurance
- Vision Insurance
- Life Insurance
- Retirement Savings
- Disability
- Paid Illness Leave

Categories (tags): Multiple linked categories

External Apply Link: Links to external job source (Workable, ATS, etc.)
```

---

## 3. URL Patterns & Predictability

### Base URLs
```
Homepage: https://remote.co/
Job Listings: https://remote.co/remote-jobs
Categories: https://remote.co/remote-jobs/categories
```

### Category Pages (PREDICTABLE PATTERN)
```
Pattern: https://remote.co/remote-jobs/[category-slug]
Examples:
- https://remote.co/remote-jobs/developer
- https://remote.co/remote-jobs/accounting
- https://remote.co/remote-jobs/customer-service
- https://remote.co/remote-jobs/sales
- https://remote.co/remote-jobs/marketing
- https://remote.co/remote-jobs/data-science
```

### Pagination (PREDICTABLE PATTERN)
```
Pattern: https://remote.co/remote-jobs/[category-slug]?page=N
Examples:
- https://remote.co/remote-jobs/developer?page=1
- https://remote.co/remote-jobs/developer?page=2
- https://remote.co/remote-jobs/developer?page=33
- https://remote.co/remote-jobs/developer?page=34
```

### Individual Job Pages (UUID IN URL)
```
Pattern: https://remote.co/job-details/[slug-with-uuid]
Examples:
- https://remote.co/job-details/senior-shopify-development-lead-61d7d61a-aadc-4292-b797-b7f23680210c
- https://remote.co/job-details/senior-analyst-revenue-operations-7e175f6d-97c1-42b4-9e66-108e7d87265b
```

### Company Pages (ACCESSIBLE)
```
Pattern: https://remote.co/company/[company-slug]
Example:
- https://remote.co/company/mozilla
```

---

## 4. Anti-Bot Protection

### robots.txt Analysis
**Severity: LOW**

```plaintext
Sitemap: https://remote.co/sitemap_index.xml

User-agent: *
Disallow: /wp-admin/
Disallow: /wp-content/plugins/advanced-custom-fields/
Disallow: *wp-admin.old*
Disallow: *?categories=*
Disallow: *?useclocation=*
Disallow: /visitor/v4/visits
Disallow: /ej/api/*
Disallow: /eb/api/*

Allow: /wp-admin/admin-ajax.php
```

### Key Points:
- ✅ Job listing pages (`/remote-jobs/*`) are NOT blocked
- ✅ Job detail pages (`/job-details/*`) are NOT blocked
- ❌ Category filters (`?categories=*`) are blocked
- ❌ Location filters (`?useclocation=*`) are blocked
- ❌ Internal APIs (`/ej/api/*`, `/eb/api/*`) are blocked
- ⚠️ Analytics tracking endpoint (`/visitor/v4/visits`) is blocked

### Other Anti-Bot Measures
- ❓ No visible CAPTCHA on job listing pages
- ❓ No rate limiting headers detected (use caution, add delays)
- ❓ No JavaScript rendering required (static HTML)
- ✅ Pages are fully crawlable with standard HTTP requests

**Recommendation:** Respect robots.txt - stick to `/remote-jobs/*` and `/job-details/*` URLs only.

---

## 5. Available Categories & Filters

### Comprehensive Category List (100+ categories)
Remote.co categorizes jobs into extensive categories accessible at: `https://remote.co/remote-jobs/[category-slug]`

**Sample Categories Include:**
```
Accounting
Administrative
Analyst
Advertising
Animals & Wildlife
Art & Design
Appointment Setting
Auditing
Back End Developer
Banking
Bilingual
Bookkeeping
Business Development
Call Center
Case Management
Chemistry
Clinical Research
Coaching
Collections
Communications
Consulting
Content Writer
Copywriting
Customer Service
Cyber Security
Data Entry
Data Science
Dental
Design
Developer
Ecommerce
Economics
Editing
Education
Engineering
Environmental
Event Planning
Fashion & Beauty
Federal Government
Film
French
Front End Developer
Full Stack Developer
Fundraising
German
Government
Grant Writing
Graphic Design
Healthcare
Healthcare Administration
Human Resources & Recruiting
Human Services
Insurance
International
IT
Japanese
Java Developer
Journalism
Legal
Library
Marketing
Math
Medical Billing
Medical Coding
Music
Non Profit
Nursing
Nutrition
Operations
Pharmaceutical
Photography
Product Manager
Programming
Project Manager
Proofreading
Public Relations
Publishing
Python
QA (Quality Assurance)
Real Estate
Research & Development
Risk Management
Ruby on Rails
Sales
Social Media
Social Work
Software Engineer
Spanish
Sports & Fitness
SQL
System Administration
Teaching
Tech Support
Transcription
Translator
Travel & Hospitality
Tutoring
UI/UX Design
Underwriting
Video Editing
Video Game
Virtual Assistant
Web Developer
Writing
```

### No Built-in Filtering Parameters
- ❌ Category filtering via query parameters is blocked (`?categories=*`)
- ❌ Location filtering via query parameters is blocked (`?useclocation=*`)
- ✅ Must navigate to category-specific URLs directly

---

## 6. Job Structure & Data Fields

### Extracted Job Data Per Listing
```python
{
    "title": str,                    # Job title
    "company": str,                  # Company name
    "company_url": str,              # /company/[slug]
    "job_url": str,                  # /job-details/[slug-uuid]
    "date_posted": str,              # "Today", "Yesterday", or date
    "remote_level": str,             # "100% Remote" or "Hybrid Remote"
    "location": str,                 # "Remote, US National" or location
    "employment_type": str,          # "Full-Time", "Part-Time", "Freelance"
    "salary": str,                   # "$70-$80 Hourly" or "$120,000 Annually"
    "job_type": str,                 # "Employee", "Contractor", "Freelance"
    "categories": list[str],         # e.g., ["Developer", "Full Stack Developer"]
    "description": str,              # Job description text
    "responsibilities": list[str],   # Job duties
    "requirements": list[str],       # Required experience/skills
    "benefits": list[str],           # Health insurance, 401k, etc.
    "apply_url": str,                # External ATS/career page URL
    "reference_id": str              # Internal job reference ID
}
```

---

## 7. Best Scraping Approach

### RECOMMENDED: HTML Parsing (BeautifulSoup)

**Advantages:**
- ✅ Straightforward implementation
- ✅ No JavaScript rendering needed
- ✅ Fast performance
- ✅ Low resource usage
- ✅ Respects robots.txt when used properly

**Disadvantages:**
- ⚠️ Must parse pagination manually
- ⚠️ Need to handle category discovery
- ⚠️ May require DOM inspection updates if markup changes

### Step-by-Step Scraping Process

#### 1. Discover Categories
```
GET https://remote.co/remote-jobs/categories
Parse HTML to extract category links
Extract slug from each link pattern: /remote-jobs/[slug]
```

#### 2. For Each Category, Scrape All Pages
```
FOR EACH category_slug IN categories:
    page = 1
    LOOP:
        GET https://remote.co/remote-jobs/{category_slug}?page={page}
        Parse job listings from this page
        Check if next page exists
        IF no next page or empty page:
            BREAK
        INCREMENT page
        WAIT 2-5 seconds (rate limit)
```

#### 3. Extract Job Details
From listing pages, extract:
- Job title
- Company name
- Remote level
- Location
- Employment type
- Salary
- Job URL
- Posted date

#### 4. Get Full Job Details (Optional)
```
FOR EACH job_url IN collected_jobs:
    GET {job_url}
    Parse full details:
        - Description
        - Responsibilities
        - Requirements
        - Benefits
        - Apply URL
    WAIT 1-3 seconds (rate limit)
```

---

## 8. Recommended Scraping Configuration

### Rate Limiting (CRITICAL)
```python
# Recommended delays
DELAY_BETWEEN_CATEGORY_PAGES = 2-5 seconds
DELAY_BETWEEN_JOB_DETAILS = 1-3 seconds
DELAY_BETWEEN_CATEGORIES = 5 seconds

# Total jobs estimate
ESTIMATED_JOBS = 100,000+ (site claims "100k+ jobs")
ESTIMATED_TIME = 1-2 weeks with respectful rate limiting
```

### HTTP Headers (Appear Natural)
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

### Parsing Library Recommendations
```python
# Option 1: BeautifulSoup4 (Recommended - simple & effective)
from bs4 import BeautifulSoup
import requests

# Option 2: Scrapy (For larger projects)
# Framework for large-scale scraping

# Option 3: Selenium (NOT recommended - slow, overkill)
# Only if site loads jobs with JavaScript
```

---

## 9. Legal & Ethical Considerations

### robots.txt Compliance
✅ **ALLOWED:**
- Scraping `/remote-jobs/*` pages
- Scraping `/job-details/*` pages
- Scraping `/remote-jobs/categories` page
- Following external job links

❌ **BLOCKED (Do NOT scrape):**
- `/ej/api/*` endpoints
- `/eb/api/*` endpoints
- Pages with `?categories=` parameters
- Pages with `?useclocation=` parameters

### Terms of Service
- Check Remote.co's TOS regarding scraping
- Consider reaching out to Remote.co for commercial use
- Use scraped data for **non-commercial purposes** or with permission

### Ethical Scraping Best Practices
1. ✅ Respect robots.txt
2. ✅ Add appropriate rate limiting (2-5 sec between requests)
3. ✅ Use a descriptive User-Agent
4. ✅ Cache results to avoid redundant requests
5. ✅ Don't overload servers
6. ✅ Consider legal implications of use
7. ✅ Credit Remote.co if publishing data

---

## 10. Implementation Example (Python)

### Basic Scraper Skeleton
```python
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict

class RemoteCoScraper:
    BASE_URL = "https://remote.co"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    RATE_LIMIT = 3  # seconds between requests
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.jobs = []
    
    def get_categories(self) -> List[str]:
        """Scrape all job categories"""
        url = f"{self.BASE_URL}/remote-jobs/categories"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        categories = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and '/remote-jobs/' in href:
                slug = href.split('/remote-jobs/')[-1]
                if slug not in ['categories']:
                    categories.append(slug)
        
        return list(set(categories))  # Remove duplicates
    
    def scrape_category(self, category: str):
        """Scrape all jobs in a category"""
        page = 1
        while True:
            url = f"{self.BASE_URL}/remote-jobs/{category}?page={page}"
            
            try:
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"Error scraping {url}: {e}")
                break
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            job_links = soup.find_all('a', {'href': lambda x: x and '/job-details/' in x})
            
            if not job_links:
                break  # No more jobs
            
            for link in job_links:
                job_url = link.get('href')
                title = link.get_text(strip=True)
                
                self.jobs.append({
                    'title': title,
                    'url': f"{self.BASE_URL}{job_url}" if job_url.startswith('/') else job_url,
                    'category': category
                })
            
            time.sleep(self.RATE_LIMIT)
            page += 1
    
    def scrape_job_details(self, job_url: str) -> Dict:
        """Scrape detailed job information"""
        try:
            resp = self.session.get(job_url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error scraping {job_url}: {e}")
            return {}
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        job_data = {
            'url': job_url,
            'title': soup.find('h1') and soup.find('h1').get_text(strip=True),
            'company': soup.find('h2') and soup.find('h2').get_text(strip=True),
            'description': '',
            'requirements': [],
        }
        
        # Extract description
        for section in soup.find_all(['section', 'div']):
            text = section.get_text(strip=True)
            if 'About the Role' in text or 'Description' in text:
                job_data['description'] = text
                break
        
        time.sleep(self.RATE_LIMIT)
        return job_data

# Usage
if __name__ == "__main__":
    scraper = RemoteCoScraper()
    
    # Get categories
    print("Discovering categories...")
    categories = scraper.get_categories()
    print(f"Found {len(categories)} categories")
    
    # Scrape a specific category
    print("\nScraping developer jobs...")
    scraper.scrape_category('developer')
    print(f"Found {len(scraper.jobs)} jobs")
    
    # Get full details for first job
    if scraper.jobs:
        print("\nScraping job details...")
        job_details = scraper.scrape_job_details(scraper.jobs[0]['url'])
        print(job_details)
```

---

## 11. Summary Table

| Aspect | Finding | Scraping Feasibility |
|--------|---------|---------------------|
| Public API | None | ❌ Not Available |
| HTML Structure | Predictable & consistent | ✅ Easy to Parse |
| URL Patterns | Highly predictable | ✅ Easy to Construct |
| Pagination | Query parameter `?page=N` | ✅ Straightforward |
| Anti-Bot Protection | Minimal (robots.txt only) | ✅ Low Difficulty |
| JavaScript Required | No | ✅ No Rendering Needed |
| Rate Limiting | Not detected, add delays | ⚠️ Proceed Cautiously |
| robots.txt Compliance | Respectful blocking | ✅ Follow Rules |
| Average Jobs | 100,000+ across all categories | ✅ Large Dataset |
| Estimated Scrape Time | 1-2 weeks with rate limiting | - |

---

## Conclusion

**Remote.co is scrapable via HTML parsing with these characteristics:**

✅ **Advantages:**
- Highly predictable URL structure
- No JavaScript rendering needed
- No public API to compete with
- 100+ discoverable job categories
- Comprehensive job data available
- robots.txt allows job listing pages

⚠️ **Challenges:**
- Must scrape category-by-category
- No official API for batch operations
- Requires manual pagination
- Must implement rate limiting
- Large dataset (100,000+ jobs)

🎯 **Best Approach:**
1. Use **BeautifulSoup** for HTML parsing
2. Discover categories from `/remote-jobs/categories`
3. Scrape category pages with pagination
4. Optionally fetch individual job detail pages
5. Implement 2-5 second delays between requests
6. Cache results to avoid re-scraping
7. Respect robots.txt restrictions

---

## Additional Resources

- **robots.txt:** https://remote.co/robots.txt
- **Sitemap:** https://remote.co/sitemap_index.xml
- **Categories:** https://remote.co/remote-jobs/categories
- **All Jobs:** https://remote.co/remote-jobs

---

*Report Generated: February 20, 2026*
*Scope: Comprehensive research for AI Job Scraper project*
