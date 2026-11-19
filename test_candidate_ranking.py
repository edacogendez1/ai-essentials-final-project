
import pandas as pd

from job_matching import (
    filter_matching_candidates,
    rank_job_matches
)

# Load real job postings from our collected dataset
jobs_df = pd.read_csv("jobs.csv").fillna("")

# Load our prepared sample resumes
resumes_df = pd.read_csv("data/prepared_resumes.csv")

# Select one resume
resume_text = resumes_df.iloc[0]["resume_text"]

print("Resume category:", resumes_df.iloc[0]["Domain"])
print("Total available jobs:", len(jobs_df))


# Classify jobs before applying preference filters
from classify_jobs import (
    classify_job_categories,
    classify_employment_type_with_description,
    classify_seniority_with_description
)

jobs_df["job_categories"] = [
    classify_job_categories(title, description)
    for title, description in zip(
        jobs_df["job_title"],
        jobs_df["description"]
    )
]


jobs_df["employment_type"] = [
    classify_employment_type_with_description(title, description)
    for title, description in zip(
        jobs_df["job_title"],
        jobs_df["description"]
    )
]

jobs_df["seniority_level"] = [
    classify_seniority_with_description(title, description)
    for title, description in zip(
        jobs_df["job_title"],
        jobs_df["description"]
    )
]



# Filter jobs using a sample student's career preferences
candidates = filter_matching_candidates(
    jobs_df=jobs_df,
    preferred_categories=[
        "Finance",
        "Accounting",
        "Investment Banking",
        "Asset Management"
    ],
    preferred_employment="Full-time",
    preferred_seniority="Entry-level",
    preferred_location=""
)

print("Matching candidates:", len(candidates))


# Rank jobs using the AI embedding model
matches = rank_job_matches(
    resume_text,
    candidates,
    top_n=10
)

print("\nTOP 10 JOB MATCHES\n")

for _, job in matches.iterrows():
    print(f"Score: {job['match_score']:.3f}")
    print(f"Company: {job['company']}")
    print(f"Job: {job['job_title']}")
    print(f"Location: {job['location']}")
    print("-" * 50)
