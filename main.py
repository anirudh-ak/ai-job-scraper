import json
import time
import os
from scrapers.remoteok import fetch_remoteok
from scrapers.himalayas import fetch_himalayas
import pandas as pd


def dedupe(jobs):
    seen = set()
    out = []
    for j in jobs:
        key = (j.get("company", "").lower(), j.get("title", "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out


def save_csv(jobs):
    df = pd.DataFrame(jobs)
    ts = time.strftime("%Y-%m-%d_%H-%M-%S")
    outdir = "outputs"
    os.makedirs(outdir, exist_ok=True)
    filename = f"ai_jobs_{ts}.csv"
    path = os.path.join(outdir, filename)
    df.to_csv(path, index=False)
    return path


def main():
    with open("config.json") as f:
        config = json.load(f)

    all_jobs = []

    print("Fetching RemoteOK...")
    try:
        r_jobs = fetch_remoteok(config)
        print(f"RemoteOK: found {len(r_jobs)} jobs (pre-dedup)")
        all_jobs.extend(r_jobs)
    except Exception as e:
        print("RemoteOK fetch failed:", e)

    print("Fetching Himalayas...")
    try:
        him_jobs = fetch_himalayas(config)
        print(f"Himalayas: found {len(him_jobs)} jobs (pre-dedup)")
        all_jobs.extend(him_jobs)
    except Exception as e:
        print("Himalayas fetch failed:", e)

    all_jobs = dedupe(all_jobs)

    if not all_jobs:
        print("No jobs found. Try relaxing your filters in `config.json`.")
        return

    path = save_csv(all_jobs)
    print(f"Saved {len(all_jobs)} jobs to {path}")


if __name__ == "__main__":
    main()
