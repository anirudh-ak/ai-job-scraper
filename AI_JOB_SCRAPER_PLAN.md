# AI Job Scraper - Project Plan

## Project Goal
Build a quick-and-dirty Python script that scrapes remote AI jobs from multiple sources and outputs results to a CSV file for manual review.

## User Requirements
- **Remote work** (non-negotiable)
- **AI-related roles** (consulting, engineering, building - flexible)
- **Future-proof positions**
- **Private** (no LinkedIn activity visible to employer)

## Core Features (v1)
1. Scrape multiple job boards for remote positions
2. **Configurable filtering** via config.json - job keywords, location, roles, exclusions
3. Output to CSV with: Job Title, Company, Location, URL, Date Posted, Description snippet
4. Run locally on-demand (no deployment, no scheduling yet)

## Out of Scope (v1)
- Auto-applying to jobs
- Fancy UI/dashboard
- Exception handling (unless it breaks core functionality)
- Test cases
- Deployment/hosting
- Email alerts
- Database storage

## Tech Stack
- Python 3.x
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `selenium` (optional) - For JavaScript-heavy sites
- `pandas` - CSV output
- `config.json` - User-editable configuration file

## Job Boards to Target

### Phase 1 (MVP)
1. **RemoteOK** - API available, easy to scrape
2. **We Work Remotely** - Clean HTML structure
3. **AngelList/Wellfound** - Startup jobs

### Phase 2 (After MVP works)
4. **Indeed** - Largest job board
5. **LinkedIn Jobs** - Comprehensive but needs careful scraping
6. **Himalayas** - Remote-first companies
7. **RemoteLeads** - Curated remote positions

## Tasks Breakdown

### Task 1: Project Setup
- [ ] Create project directory structure
- [ ] Set up virtual environment
- [ ] Install dependencies (requests, beautifulsoup4, pandas, selenium if needed)
- [ ] Create requirements.txt
- [ ] Create default config.json with AI job search parameters

### Task 2: Build RemoteOK Scraper
- [ ] Research RemoteOK structure/API
- [ ] Write scraper function for RemoteOK
- [ ] Filter using keywords from config.json
- [ ] Test with sample output

### Task 3: Build We Work Remotely Scraper
- [ ] Research WWR HTML structure
- [ ] Write scraper function for WWR
- [ ] Filter using keywords from config.json
- [ ] Test with sample output

### Task 4: Build AngelList Scraper
- [ ] Research AngelList structure
- [ ] Write scraper function
- [ ] Filter using keywords from config.json
- [ ] Test with sample output

### Task 5: Data Aggregation & Deduplication
- [ ] Combine results from all scrapers
- [ ] Remove duplicate jobs (same company + title)
- [ ] Sort by date posted (newest first)

### Task 6: CSV Output
- [ ] Format data into pandas DataFrame
- [ ] Export to CSV with proper columns
- [ ] Add timestamp to filename (e.g., `ai_jobs_2026-02-16.csv`)

### Task 7: Main Script & CLI
- [ ] Create main.py that orchestrates all scrapers
- [ ] Add simple command-line interface (optional: choose specific boards)
- [ ] Add progress indicators (print statements)

### Task 8: Basic Testing
- [ ] Run end-to-end and verify CSV output
- [ ] Check that links are valid
- [ ] Verify no obvious broken scraping

## Configuration (config.json)

The script will read from a `config.json` file that allows customization:

```json
{
  "job_keywords": ["AI", "machine learning", "ML", "NLP", "LLM", "GenAI", "generative AI", "artificial intelligence"],
  "location_keywords": ["remote", "work from home", "WFH", "anywhere"],
  "role_keywords": ["engineer", "consultant", "architect", "developer", "analyst", "scientist", "researcher"],
  "exclude_keywords": ["intern", "junior", "entry level"],
  "min_salary": null,
  "max_results_per_board": 50
}
```

**Benefits:**
- Reusable for different job searches (just edit the JSON)
- Easy to add/remove keywords without touching code
- Can share configs with friends looking for different roles
- No command-line complexity

## Success Criteria
- Script runs without crashing
- Finds at least 20-30 relevant jobs per run
- CSV is readable and links work
- Takes less than 5 minutes to run
- User can manually review and apply to jobs

## Future Enhancements (Post-v1)
- Add more job boards
- Schedule daily runs (cron job or Task Scheduler)
- Email/Slack notifications for new jobs
- Simple HTML dashboard for better visual review
- Track application status
- Auto-apply for Easy Apply jobs (LinkedIn, Indeed)
- Filter by salary range, experience level
- Company research (funding, size, culture)

## Timeline Estimate
- **Setup + Task 1-3:** 1 weekend (4-6 hours)
- **Task 4-6:** 1 weekend (3-4 hours)
- **Task 7-8:** 1-2 hours

**Total:** 2 weekends, ~10 hours of coding

## Notes
- Start with RemoteOK since it has an API - easiest to prove concept
- If a site is too hard to scrape, skip it and move to next
- Focus on getting something working, then iterate
- User is in India/Mumbai timezone - consider this for "date posted" filtering
- **Config file makes this reusable** - can search for Product Manager, DevOps, Data Science jobs by just editing config.json
