import streamlit as st


import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Job Search Assistant",
    page_icon="💼",
    layout="wide"
)

# Main title
st.title("💼 AI Job Search Assistant")

# Introduction
st.write(
    "Find job opportunities that match your experience, "
    "skills, and career goals."
)

st.markdown(
    "**Eda & Yuvraj's AI Essentials Final Project**"
)

st.divider()

# Welcome section
st.header("Welcome!")

st.write(
    "Our AI-powered job search assistant helps students "
    "discover relevant opportunities and make the recruiting "
    "process more personalized and efficient."
)

# Features section
st.subheader("What can our assistant do?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📄 Resume Analysis")
    st.write(
        "Upload your resume so our system can understand "
        "your skills, education, and experience."
    )

with col2:
    st.markdown("### 🎯 Personalized Job Matching")
    st.write(
        "Discover job opportunities ranked according to "
        "your background and career preferences."
    )

with col3:
    st.markdown("### 🧠 Adaptive Recommendations")
    st.write(
        "Help the system improve its recommendations "
        "by giving feedback on suggested jobs."
    )

st.divider()

# Future application functionality
st.subheader("Get Started")

uploaded_resume = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)

preferred_location = st.text_input(
    "Preferred job location",
    placeholder="e.g., Chicago, New York, Remote"
)

target_industry = st.selectbox(
    "Target industry",
    [
        "Select an industry",
        "Finance",
        "Consulting",
        "Technology",
        "Marketing",
        "Healthcare",
        "Other"
    ]
)

# Clearly mark incomplete functionality
st.info(
    "Prototype: Resume analysis and job matching "
    "are currently under development."
)

st.divider()

# Footer
st.caption(
    "Built for AI Essentials | Eda & Yuvraj"
)


# ----------------------------------------
# JOB SEARCH SECTION
# ----------------------------------------

import pandas as pd
from pathlib import Path

st.divider()
st.header("🔎 Explore Job Opportunities")

jobs_path = Path(__file__).parent / "jobs.csv"

if jobs_path.exists():
    jobs_df = pd.read_csv(jobs_path).fillna("")

    st.write(f"Explore {len(jobs_df):,} job opportunities!")

    # Company filter
    companies = ["All Companies"] + sorted(
        jobs_df["company"].unique().tolist()
    )

    selected_company = st.selectbox(
        "Select a company",
        companies
    )

       # Location filter
    location_search = st.text_input(
        "Preferred job location",
        placeholder="e.g., Chicago, New York, Remote",
        key="job_search_location"
    )

    # Job title filter
    keyword_search = st.text_input(
        "Job title or keyword",
        placeholder="e.g., Analyst, Finance, Data Scientist",
        key="job_search_keyword"
    )

    # Apply filters
    filtered_jobs = jobs_df.copy()

    if selected_company != "All Companies":
        filtered_jobs = filtered_jobs[
            filtered_jobs["company"] == selected_company
        ]

    if location_search:
        filtered_jobs = filtered_jobs[
            filtered_jobs["location"].str.contains(
                location_search, case=False, regex=False
            )
        ]

    if keyword_search:
        filtered_jobs = filtered_jobs[
            filtered_jobs["job_title"].str.contains(
                keyword_search, case=False, regex=False
            )
        ]

    st.write(f"**{len(filtered_jobs)} matching jobs found**")

    # Display the first 20 matching results
    for _, job in filtered_jobs.head(20).iterrows():
        with st.container(border=True):
            st.subheader(job["job_title"])
            st.write(f"**Company:** {job['company']}")
            st.write(f"**Location:** {job['location']}")

            with st.expander("View Job Description"):
                st.write(job["description"])

            if str(job["job_url"]).startswith("https://"):
                st.link_button(
                    "View Original Posting",
                    job["job_url"]
                )

else:
    st.info(
        "Job database not found. "
        "Run collect_jobs.py locally to generate jobs.csv."
    )
