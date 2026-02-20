# AI Job Scraper (v1)

Quick script to scrape remote AI jobs (MVP).

Usage

- Create and activate a Python virtual environment (optional but recommended).

On Windows PowerShell:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Edit `config.json` to change keywords, locations, and max results.

- Run the script:

```powershell
python main.py
```

- Output CSV will be written to `outputs/ai_jobs_YYYY-MM-DD.csv`.

Notes

- v1 currently includes a RemoteOK scraper.
- Future work: add other boards, CLI flags, scheduling, better deduplication.
