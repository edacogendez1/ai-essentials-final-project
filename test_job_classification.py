
import random

from collect_jobs import collect_all_jobs
from classify_jobs import (
    classify_employment_type_with_description,
    classify_seniority_with_description
)

# Collect real jobs
jobs, errors = collect_all_jobs()

print("\nTotal jobs collected:", len(jobs))

# Randomly select 20 jobs
random.seed(42)
sample_jobs = random.sample(jobs, min(20, len(jobs)))

print("\nREAL JOB CLASSIFICATION TEST")
print("----------------------------")

for job in sample_jobs:
    title = job["job_title"]
    description = job["description"]

    employment_type = classify_employment_type_with_description(
    title, description
    )
    seniority = classify_seniority_with_description(
        title, description
    )

    print(f"\nJob: {title}")
    print(f"Company: {job['company']}")
    print(f"Employment type: {employment_type}")
    print(f"Seniority: {seniority}")
