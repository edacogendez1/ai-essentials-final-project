
import pandas as pd

from sentence_transformers import SentenceTransformer, util

from collect_jobs import collect_all_jobs

# Step 1: Load the prepared resumes
resumes = pd.read_csv("data/prepared_resumes.csv")

# Select the first resume for testing
resume = resumes.iloc[0]

print("Selected resume category:", resume["Domain"])

# Step 2: Collect real jobs from Greenhouse and Lever
print("\nCollecting real job postings...")

jobs, errors = collect_all_jobs()

# Convert the job listings into a DataFrame
jobs_df = pd.DataFrame(jobs)

print("Total jobs collected:", len(jobs_df))

# Step 3: Select 500 jobs
jobs_sample = jobs_df.sample(
    n=min(500, len(jobs_df)),
    random_state=42
).copy()

print("Jobs selected for testing:", len(jobs_sample))

# Display the first five job titles
print("\nSample job titles:")

for title in jobs_sample["job_title"].head(5):
    print("-", title)

# Step 4: Load our pretrained AI embedding model
print("\nLoading AI model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 5: Prepare the resume and job descriptions
resume_text = str(resume["resume_text"])

jobs_sample["job_text"] = (
    jobs_sample["job_title"].fillna("").astype(str)
    + ". "
    + jobs_sample["description"].fillna("").astype(str)
)

# Check whether our input documents exceed the model's token limit
resume_tokens = len(
    model.tokenizer.encode(
        resume_text,
        add_special_tokens=True
    )
)

job_token_counts = [
    len(model.tokenizer.encode(text, add_special_tokens=True))
    for text in jobs_sample["job_text"].tolist()
]

print("\nMODEL INPUT LENGTH CHECK")
print("Model token limit:", model.max_seq_length)
print("Resume token count:", resume_tokens)
print("Average job token count:", round(sum(job_token_counts) / len(job_token_counts)))
print("Jobs exceeding limit:", sum(
    count > model.max_seq_length for count in job_token_counts
))

# Step 6: Convert resume and jobs into embeddings
print("Generating embeddings...")

resume_embedding = model.encode(
    resume_text,
    convert_to_tensor=True
)


# Step 7: Split long job descriptions into smaller chunks

def split_into_chunks(text, model, chunk_size=200):
    tokens = model.tokenizer.encode(
        text,
        add_special_tokens=False
    )

    chunks = []

    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]

        chunk_text = model.tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True
        )

        chunks.append(chunk_text)

    return chunks


# Step 8: Compare the resume with every chunk of each job

similarity_scores = []

print("\nMatching resume against full job descriptions...")

for job_text in jobs_sample["job_text"]:

    chunks = split_into_chunks(job_text, model)

    chunk_embeddings = model.encode(
        chunks,
        convert_to_tensor=True
    )

    chunk_scores = util.cos_sim(
        resume_embedding,
        chunk_embeddings
    )[0]

    # Average similarity across all chunks
    average_score = chunk_scores.mean().item()

    similarity_scores.append(average_score)


# Store the scores for ranking
jobs_sample["similarity_score"] = similarity_scores


# Step 9: Rank jobs by similarity
top_jobs = jobs_sample.sort_values(
    "similarity_score",
    ascending=False
).head(10)

print("\nTOP 10 AI JOB MATCHES")
print("---------------------")

for _, job in top_jobs.iterrows():
    print(f"\n{job['job_title']} — {job['company']}")
    print(f"Similarity score: {job['similarity_score']:.3f}")
    print(f"Location: {job['location']}")