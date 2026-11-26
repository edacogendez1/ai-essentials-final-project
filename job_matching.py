
from collections import OrderedDict
from functools import lru_cache
import re
from threading import Lock, Thread

import numpy as np
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


@st.cache_resource(show_spinner=False)
def job_embedding_cache():
    # Cache public posting text only. Resume embeddings stay local to the request.
    return OrderedDict(), Lock()


@st.cache_resource(show_spinner=False)
def job_embedding_warmup_state():
    return {"thread": None}


def _encode_missing(model, cache, lock, job_texts):
    with lock:
        missing_texts = [text for text in dict.fromkeys(job_texts) if text not in cache]
    if not missing_texts:
        return
    new_embeddings = model.encode(missing_texts, batch_size=32, normalize_embeddings=True)
    with lock:
        for job_text, embedding in zip(missing_texts, new_embeddings):
            cache[job_text] = embedding.copy()
            cache.move_to_end(job_text)
        while len(cache) > 20_000:
            cache.popitem(last=False)


def warm_job_embeddings(jobs_df):
    """
    Start embedding every loaded job in a background thread so the
    first "Find My Matches" click doesn't have to wait for it.
    """
    if jobs_df.empty:
        return

    # Resolve cached resources on the script thread (they need its context)
    model = load_matching_model()
    cache, lock = job_embedding_cache()
    state = job_embedding_warmup_state()

    job_texts = [
        prepare_job_text({"job_title": title, "description": description})
        for title, description in zip(jobs_df["job_title"], jobs_df["description"])
    ]

    with lock:
        thread = state["thread"]
        if thread is not None and thread.is_alive():
            return
        if all(text in cache for text in job_texts):
            return
        thread = Thread(
            target=_encode_missing,
            args=(model, cache, lock, job_texts),
            daemon=True
        )
        state["thread"] = thread
    thread.start()


def encode_job_texts(model, job_texts):
    cache, lock = job_embedding_cache()

    # If a background warmup is running, wait for it rather than
    # encoding the same postings twice.
    thread = job_embedding_warmup_state()["thread"]
    if thread is not None and thread.is_alive():
        thread.join()

    unique_texts = dict.fromkeys(job_texts)
    embeddings = {}
    with lock:
        for job_text in unique_texts:
            if job_text in cache:
                cache.move_to_end(job_text)
                embeddings[job_text] = cache[job_text]

    missing_texts = [job_text for job_text in unique_texts if job_text not in embeddings]
    if missing_texts:
        new_embeddings = model.encode(
            missing_texts,
            batch_size=32,
            normalize_embeddings=True
        )
        with lock:
            for job_text, embedding in zip(missing_texts, new_embeddings):
                # Keep a standalone vector so evicting a row can free its memory.
                vector = embedding.copy()
                embeddings[job_text] = cache[job_text] = vector
                cache.move_to_end(job_text)
            while len(cache) > 20_000:
                cache.popitem(last=False)

    return np.stack([embeddings[job_text] for job_text in job_texts])


def calculate_similarity(resume_text, job_texts, return_embeddings=False):
    model = load_matching_model()

    resume_embedding = model.encode(
        resume_text,
        normalize_embeddings=True
    )

    job_embeddings = encode_job_texts(model, job_texts) if len(job_texts) else np.empty(
        (0, len(resume_embedding)), dtype=resume_embedding.dtype
    )

    similarities = job_embeddings @ resume_embedding

    if return_embeddings:
        return similarities, job_embeddings

    return similarities


def filter_matching_candidates(
    jobs_df,
    preferred_categories,
    preferred_employment,
    preferred_seniority,
    preferred_location
):
    candidates = jobs_df.copy()

    # Filter by job category only when specific categories are selected
    if preferred_categories and "All Industries" not in preferred_categories:
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

# Precompile skill patterns once instead of rebuilding them per job
SKILL_PATTERNS = [
    (
        skill,
        re.compile(
            r"\br\b(?!\s*&\s*d)" if skill == "r"
            else r"\b" + re.escape(skill) + r"\b"
        ),
        SKILL_SYNONYMS.get(skill, skill)
    )
    for skill in SKILL_KEYWORDS
]


def extract_skills(text):
    text = str(text).lower()

    found_skills = set()

    for skill, pattern, canonical_skill in SKILL_PATTERNS:
        # A plain substring check is far faster than a regex starting
        # with \b, so only run the regex when the keyword appears at all.
        if skill in text and pattern.search(text):
            found_skills.add(canonical_skill)

    return found_skills


@lru_cache(maxsize=20_000)
def extract_job_skills(job_text):
    # Cache public posting text only; resumes are never cached.
    return frozenset(extract_skills(job_text))

def calculate_skills_overlap(resume_text, job_text):
    resume_skills = extract_skills(resume_text)
    return score_skills_overlap(resume_skills, job_text)


def score_skills_overlap(resume_skills, job_text):
    if resume_skills:
        return len(resume_skills.intersection(extract_job_skills(str(job_text)))) / len(resume_skills)
    return 0.0


# ----------------------------------------
# EDUCATION ELIGIBILITY
# ----------------------------------------

def detect_required_degree(job_title):
    """Detect the minimum degree level mentioned in the job title."""
    title = str(job_title).lower()

    # PhD = Level 3
    if re.search(r"\bph\.?d\.?\b|\bdoctorate\b", title):
        return 3

    # BS/MS or BA/MA = Level 1 (either degree accepted)
    if re.search(
        r"\bb\.?[sa]\.?\s*/\s*m\.?[sa]\.?\b",
        title
    ):
        return 1

    # Master's = Level 2
    if re.search(
        r"\bm\.?[sa]\.?\b|\bmaster'?s?\b",
        title
    ):
        return 2

    # Bachelor's = Level 1
    if re.search(
        r"\bb\.?[sa]\.?\b|\bbachelor'?s?\b",
        title
    ):
        return 1

    return None


def detect_candidate_degree(resume_text):
    """Detect the highest degree level mentioned in the resume."""
    resume = str(resume_text).lower()

    if re.search(r"\bph\.?d\.?\b|\bdoctorate\b", resume):
        return 3

    if re.search(r"\bm\.?[sa]\.?\b|\bmaster'?s?\b", resume):
        return 2

    if re.search(r"\bb\.?[sa]\.?\b|\bbachelor'?s?\b", resume):
        return 1

    return None



def calculate_eligibility_penalty(resume_text, job_title):
    """
    Apply a penalty when the job title explicitly
    requests a higher degree than the candidate has.
    """
    return score_eligibility_penalty(detect_candidate_degree(resume_text), job_title)


def score_eligibility_penalty(candidate_degree, job_title):
    if candidate_degree is None:
        return 0.0

    required_degree = detect_required_degree(job_title)
    if required_degree is not None and candidate_degree < required_degree:
        return 0.15

    return 0.0


def rank_job_matches(resume_text, candidates, top_n=10, feedback=None):

    if candidates.empty:
        return candidates.copy()

    # Rank every job that passed the preference filters
    candidates = candidates.copy()
    # Prepare text for each job
    job_texts = [
        prepare_job_text({"job_title": title, "description": description})
        for title, description in zip(candidates["job_title"], candidates["description"])
    ]

    # Calculate semantic similarity
    scores, job_embeddings = calculate_similarity(resume_text, job_texts, return_embeddings=True)

    # Add similarity scores to the job data
    candidates["match_score"] = scores

    # Match skills using the full job description
    resume_skills = extract_skills(resume_text)
    candidates["skills_score"] = [
        score_skills_overlap(resume_skills, description)
        for description in candidates["description"]
    ]

    # Combine semantic similarity and skills overlap
    candidates["hybrid_score"] = (
        0.85 * candidates["match_score"]
        + 0.15 * candidates["skills_score"]
    )
    # Create job identifiers matching the feedback buttons
    candidates["feedback_key"] = (
        candidates["ats"].astype(str)
        + "_"
        + candidates["company"].astype(str)
        + "_"
        + candidates["job_id"].astype(str)
    )
    # Retrieve student feedback for each job
    feedback = feedback or {}

    candidates["feedback_rating"] = (
            candidates["feedback_key"]
            .map(feedback)
            .fillna(0)
            .astype(int)
        )
    # Calculate similarity to previously rated jobs
    candidates["feedback_score"] = 0.0

    if (candidates["feedback_rating"] != 0).any():

        ratings = candidates["feedback_rating"].to_numpy()
        rated_embeddings = job_embeddings[ratings != 0]
        rated_values = ratings[ratings != 0]

        feedback_scores = (
            job_embeddings @ rated_embeddings.T
        ) @ rated_values / len(rated_values)

        candidates["feedback_score"] = feedback_scores

   
    # Calculate education eligibility using job titles only
    candidate_degree = detect_candidate_degree(resume_text)
    candidates["eligibility_penalty"] = [
        score_eligibility_penalty(candidate_degree, title)
        for title in candidates["job_title"]
    ]

    # Adjust scores based on feedback and education eligibility
    candidates["final_score"] = (
        candidates["hybrid_score"]
        + 0.10 * candidates["feedback_score"]
        - candidates["eligibility_penalty"]
    )

    # Rank from highest to lowest
    candidates = candidates.sort_values(
        by="final_score",
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

