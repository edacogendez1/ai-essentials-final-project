
import csv
import time
import requests
from bs4 import BeautifulSoup
from html import unescape
from datetime import datetime, timezone

# Convert HTML job descriptions into readable text
def clean_text(raw_text):
    return BeautifulSoup(
        unescape(raw_text or ""), "html.parser"
    ).get_text(separator=" ", strip=True)


# Retrieve Greenhouse jobs
def get_greenhouse_jobs(company, board_id):
    url = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{board_id}/jobs"
    )

    response = requests.get(
        url,
        params={"content": "true"},
        timeout=60
    )
    response.raise_for_status()

    results = []

    for job in response.json().get("jobs", []):
        results.append({
            "company": company,
            "ats": "greenhouse",
            "job_id": str(job.get("id", "")),
            "job_title": job.get("title", ""),
            "location": job.get("location", {}).get("name", ""),
            "description": clean_text(job.get("content", "")),
            "job_url": job.get("absolute_url", "")
        })

    return results


# Retrieve Lever jobs using pagination
def get_lever_jobs(company, board_id):
    url = f"https://api.lever.co/v0/postings/{board_id}"

    results = []
    skip = 0
    batch_size = 20

    for page in range(100):
        response = requests.get(
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

            results.append({
                "company": company,
                "ats": "lever",
                "job_id": str(job.get("id", "")),
                "job_title": job.get("text", ""),
                "location": job.get("categories", {}).get(
                    "location", ""
                ),
                "description": description,
                "job_url": job.get("hostedUrl", "")
            })

        print(f"  Retrieved {len(results)} jobs so far")

        if len(batch) < batch_size:
            break

        skip += batch_size
        time.sleep(0.3)

    else:
        raise RuntimeError("Lever pagination safety limit reached")

    return results


# Read our list of companies
all_jobs = []
failed_companies = []

with open("companies.csv", newline="", encoding="utf-8") as file:
    companies = list(csv.DictReader(file))

for company_info in companies:
    company = company_info["company"]
    ats = company_info["ats"].strip().lower()
    board_id = company_info["board_id"].strip()

    print(f"\nCollecting jobs from {company}...")

    try:
        if ats == "greenhouse":
            jobs = get_greenhouse_jobs(company, board_id)

        elif ats == "lever":
            jobs = get_lever_jobs(company, board_id)

        else:
            raise ValueError(f"Unsupported ATS: {ats}")

        print(f"{company}: {len(jobs)} jobs collected")

        checked_at = datetime.now(timezone.utc).isoformat()

        for job in jobs:
            job["last_checked"] = checked_at

        all_jobs.extend(jobs)

    except (requests.exceptions.RequestException,
            ValueError, RuntimeError) as error:
        print(f"Could not collect {company}: {error}")
        failed_companies.append(company)


# Remove duplicate postings by ATS, company and job ID
unique_jobs = {}

for job in all_jobs:
    key = (job["ats"], job["company"], job["job_id"])
    unique_jobs[key] = job


# Save everything into a CSV
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

with open("jobs.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(unique_jobs.values())

print("\n===== COLLECTION COMPLETE =====")
print("Total unique jobs:", len(unique_jobs))
print("Saved to: jobs.csv")

if failed_companies:
    print("Companies with collection errors:", failed_companies)
    print("WARNING: Dataset is incomplete.")
