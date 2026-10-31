
import requests
from bs4 import BeautifulSoup
from html import unescape


# TEST 1; GREENHOUSE JOB BOARD API --> stripr only
url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"

response = requests.get(
    url,
    params={"content": "true"},
    timeout=20
)

response.raise_for_status()

jobs = response.json()["jobs"]

print("Number of jobs found:", len(jobs))

for job in jobs[:3]:
    print("\nJob title:", job["title"])
    print("Location:", job["location"]["name"])

    raw_description = job.get("content", "")

    clean_description = BeautifulSoup(
        unescape(raw_description), "html.parser"
    ).get_text(separator=" ", strip=True)

    print("Job description:", clean_description[:500])

# TEST 2: LEVER JOB BOARD API --> all public Palantir job posts

print("\n===== LEVER JOB POSTINGS =====")

lever_url = "https://api.lever.co/v0/postings/palantir"

all_lever_jobs = []
skip = 0
batch_size = 20

while True:
    try:
        response = requests.get(
            lever_url,
            params={
                "mode": "json",
                "limit": batch_size,
                "skip": skip
            },
            timeout=60
        )
        response.raise_for_status()
        batch = response.json()

    except requests.exceptions.RequestException as error:
        print("Lever request failed:", error)
        break

    if not batch:
        break

    all_lever_jobs.extend(batch)
    print("Jobs retrieved so far:", len(all_lever_jobs))

    if len(batch) < batch_size:
        break

    skip += batch_size

print("\nTotal Lever jobs retrieved:", len(all_lever_jobs))

for job in all_lever_jobs[:3]:
    print("\nJob title:", job.get("text"))
    print("Location:", job.get("categories", {}).get("location"))
    print("Description:", job.get("descriptionPlain", "")[:500])
