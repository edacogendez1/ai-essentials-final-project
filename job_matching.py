
import streamlit as st


# ----------------------------------------
# AI JOB MATCHING
# ----------------------------------------

def prepare_job_text(job):
    """
    Combine relevant job information into text
    that the embedding model can analyze.
    """

    title = str(job.get("job_title", ""))
    description = str(job.get("description", ""))

    # Limit very long job descriptions
    description = description[:3000]

    return f"Job Title: {title}. Job Description: {description}"


from sentence_transformers import SentenceTransformer

@st.cache_resource(show_spinner="Loading AI matching model...")
def load_matching_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def calculate_similarity(resume_text, job_texts):
    model = load_matching_model()

    resume_embedding = model.encode(
        resume_text,
        normalize_embeddings=True
    )

    job_embeddings = model.encode(
        job_texts,
        batch_size=32,
        normalize_embeddings=True
    )

    similarities = job_embeddings @ resume_embedding

    return similarities

def filter_matching_candidates(
    jobs_df,
    preferred_categories,
    preferred_employment,
    preferred_seniority,
    preferred_location
):
    candidates = jobs_df.copy()

    # Filter by preferred job categories
    if preferred_categories:
        candidates = candidates[
            candidates["job_categories"].apply(
                lambda categories: any(
                    category in categories
                    for category in preferred_categories
                )
            )
        ]

    # Filter by employment type
    if preferred_employment:
        candidates = candidates[
            candidates["employment_type"] == preferred_employment
        ]

    # Filter by seniority level
    if preferred_seniority and preferred_seniority != "All Levels":
        candidates = candidates[
            candidates["seniority_level"] == preferred_seniority
        ]

    # Filter by preferred location
    if preferred_location.strip():
        candidates = candidates[
            candidates["location"].str.contains(
                preferred_location.strip(),
                case=False,
                regex=False,
                na=False
            )
        ]

    return candidates


# Skills used to evaluate resume-job alignment
SKILL_KEYWORDS = [
    "python", "sql", "r", "excel", "tableau",
    "power bi", "financial modeling", "valuation",
    "financial analysis", "financial reporting",
    "investment research", "portfolio management",
    "risk management", "due diligence", "m&a",
    "machine learning", "data analysis",
    "project management", "market research",
    "accounting", "budgeting", "forecasting",
    "quantitative trading", "algorithmic trading",
    "financial statement analysis", "equity research",
    "investment analysis", "industry research",
    "mergers and acquisitions", "capital allocation",
    "portfolio optimization", "backtesting",
    "factor analysis", "stochastic processes",
    "futures trading", "corporate finance",
    "fp&a", "financial planning and analysis"
 ]   

SKILL_SYNONYMS = {
    "m&a": "mergers and acquisitions",
    "mergers and acquisitions": "mergers and acquisitions",
    "fp&a": "financial planning and analysis",
    "financial planning and analysis": "financial planning and analysis"
}

def extract_skills(text):
    import re

    text = str(text).lower()

    found_skills = set()

    for skill in SKILL_KEYWORDS:
        if skill == "r":
            pattern = r"\br\b(?!\s*&\s*d)"
        else:
            pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            canonical_skill = SKILL_SYNONYMS.get(skill, skill)
            found_skills.add(canonical_skill)

    return found_skills

def calculate_skills_overlap(resume_text, job_text):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    if not resume_skills:
        return 0.0

    matching_skills = resume_skills.intersection(job_skills)

    return len(matching_skills) / len(resume_skills)


def rank_job_matches(resume_text, candidates, top_n=10):

    if candidates.empty:
        return candidates.copy()

    # Rank every job that passed the preference filters
    candidates = candidates.copy()
    # Prepare text for each job
    job_texts = [
        prepare_job_text(job)
        for _, job in candidates.iterrows()
    ]

    # Calculate semantic similarity
    scores = calculate_similarity(
        resume_text,
        job_texts
    )

    # Add similarity scores to the job data
    candidates["match_score"] = scores

    # Match skills using the full job description
    candidates["skills_score"] = [
        calculate_skills_overlap(
            resume_text,
            str(job["description"])
        )
        for _, job in candidates.iterrows()
    ]

    # Combine semantic similarity and skills overlap
    candidates["hybrid_score"] = (
        0.85 * candidates["match_score"]
        + 0.15 * candidates["skills_score"]
    )

    # Rank from highest to lowest
    candidates = candidates.sort_values(
        by="hybrid_score",
        ascending=False
    )

    # Create a unique key using company and job title
    candidates["dedup_key"] = (
        candidates["company"].str.strip().str.lower()
        + "|"
        + candidates["job_title"].str.strip().str.lower()
    )

# Keep only the highest-ranked posting for each job
    candidates = candidates.drop_duplicates(
        subset=["dedup_key"],
        keep="first"
    )

# Return the top unique recommendations
    return candidates.drop(columns=["dedup_key"]).head(top_n)

