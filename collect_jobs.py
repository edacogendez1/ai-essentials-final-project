
import csv
import time
import requests
from bs4 import BeautifulSoup
from html import unescape
from pathlib import Path
from datetime import datetime, timezone

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True
)

session.mount(
    "https://",
    HTTPAdapter(max_retries=retries)
)

BASE_DIR = Path(__file__).parent


def clean_text(raw_text):
    return BeautifulSoup(
        unescape(raw_text or ""), "html.parser"
    ).get_text(separator=" ", strip=True)


def get_greenhouse_jobs(company, board_id):
    url = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{board_id}/jobs"
    )

    response = session.get(
    url,
    params={"content": "true"},
    timeout=60
)
    response.raise_for_status()

    jobs = []

    for job in response.json().get("jobs", []):
        jobs.append({
            "company": company,
            "ats": "greenhouse",
            "job_id": str(job.get("id", "")),
            "job_title": job.get("title", ""),
            "location": (job.get("location") or {}).get("name", ""),
            "description": clean_text(job.get("content", "")),
            "job_url": job.get("absolute_url", "")
        })

    return jobs


def get_lever_jobs(company, board_id):
    url = f"https://api.lever.co/v0/postings/{board_id}"

    jobs = []
    batch_size = 20
    skip = 0

    for page in range(100):
        response = session.get(
            url,
            params={
                "mode": "json",
                "limit": batch_size,
                "skip": skip
            },
            timeout=60
        )
        response.raise_for_status()

        batch = response.json()

        if not batch:
            break

        for job in batch:
            description = job.get("descriptionPlain", "")

            if not description:
                html_parts = [job.get("description", "")]

                for section in job.get("lists", []):
                    html_parts.append(section.get("content", ""))

                description = clean_text(" ".join(html_parts))

            jobs.append({
                "company": company,
                "ats": "lever",
                "job_id": str(job.get("id", "")),
                "job_title": job.get("text", ""),
                "location": (job.get("categories") or {}).get(
                    "location", ""
                ),
                "description": description,
                "job_url": job.get("hostedUrl", "")
            })

        if len(batch) < batch_size:
            break

        skip += batch_size
        time.sleep(0.3)

    else:
        raise RuntimeError("Lever pagination safety limit reached")

    return jobs


def collect_all_jobs():
    all_jobs = []
    errors = []

    with open(
        BASE_DIR / "companies.csv",
        newline="",
        encoding="utf-8"
    ) as file:
        companies = list(csv.DictReader(file))

    for company_info in companies:
        company = company_info["company"]
        ats = company_info["ats"].strip().lower()
        board_id = company_info["board_id"].strip()

        try:
            if ats == "greenhouse":
                jobs = get_greenhouse_jobs(company, board_id)

            elif ats == "lever":
                jobs = get_lever_jobs(company, board_id)

            else:
                raise ValueError(f"Unsupported ATS: {ats}")

            checked_at = datetime.now(timezone.utc).isoformat()

            for job in jobs:
                job["last_checked"] = checked_at

            all_jobs.extend(jobs)
            print(f"{company}: collected {len(jobs)} jobs")

        except (requests.exceptions.RequestException,
                ValueError, RuntimeError) as error:
            errors.append(f"{company}: {error}")
            print(f"Collection error — {company}: {error}")

    # Remove duplicate job IDs
    unique_jobs = {}

    for job in all_jobs:
        key = (job["ats"], job["company"], job["job_id"])
        unique_jobs[key] = job

    return list(unique_jobs.values()), errors


# Only write jobs.csv when this script is run directly.
# Importing it into Streamlit will NOT create a CSV.
if __name__ == "__main__":
    jobs, errors = collect_all_jobs()

    columns = [
        "company",
        "ats",
        "job_id",
        "job_title",
        "location",
        "description",
        "job_url",
        "last_checked"
    ]

    with open(
        BASE_DIR / "jobs.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(jobs)

    print(f"\nSaved {len(jobs)} jobs to jobs.csv")

    if errors:
        print("Some companies could not be retrieved:")
        for error in errors:
            print(error)
