
import requests
from bs4 import BeautifulSoup

# TEST 3: WORKDAY JOB BOARD

# NVIDIA's Workday careers website
base_url = "https://nvidia.wd5.myworkdayjobs.com"
tenant = "nvidia"
site = "NVIDIAExternalCareerSite"

jobs_url = f"{base_url}/wday/cxs/{tenant}/{site}/jobs"

# Request 5 job postings
payload = {
    "appliedFacets": {},
    "limit": 5,
    "offset": 0,
    "searchText": ""
}

try:
    response = requests.post(
        jobs_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    response.raise_for_status()

    data = response.json()
    jobs = data.get("jobPostings", [])

    print("Total jobs reported:", data.get("total"))
    print("Jobs retrieved:", len(jobs))

    for job in jobs:
        print("\nJob title:", job.get("title"))
        print("Location:", job.get("locationsText"))

        # Retrieve the full job description
        job_path = job.get("externalPath")

        if job_path:
            detail_url = (
                f"{base_url}/wday/cxs/{tenant}/{site}{job_path}"
            )

            detail_response = requests.get(
                detail_url,
                timeout=30
            )
            detail_response.raise_for_status()

            job_info = detail_response.json().get(
                "jobPostingInfo", {}
            )

            description = BeautifulSoup(
                job_info.get("jobDescription", ""),
                "html.parser"
            ).get_text(separator=" ", strip=True)

            print("Job description:", description[:500])

except requests.exceptions.RequestException as error:
    print("Workday request failed:", error)
