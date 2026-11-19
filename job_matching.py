
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

    # Rank from highest to lowest
    candidates = candidates.sort_values(
        by="match_score",
        ascending=False
    )

    return candidates.head(top_n)

