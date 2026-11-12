
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Load our prepared CareerCorpus resumes
resumes = pd.read_csv("data/prepared_resumes.csv")

# Load the pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Select one resume for testing
resume_text = resumes.iloc[0]["resume_text"]
print("\nSelected resume:")
print(resume_text[:2000])

# Three example job descriptions

jobs = [
    (
        "Banking Operations Analyst: Manage customer accounts, "
        "support loan operations, monitor regulatory compliance, "
        "prepare financial reports, identify operational risks, "
        "and assist with daily banking transactions. "
        "Requires experience in banking operations, "
        "financial services, Excel, and customer account management."
    ),

    (
        "Financial Analyst: Develop financial forecasts, "
        "analyze financial statements, prepare budgets, "
        "evaluate financial performance, and build valuation models. "
        "Requires financial analysis, Excel, accounting, "
        "and financial modeling skills."
    ),

    (
        "Marketing Associate: Develop marketing campaigns, "
        "manage social media content, support branding initiatives, "
        "analyze campaign performance, and coordinate marketing projects. "
        "Requires marketing experience, communication skills, "
        "and familiarity with digital marketing tools."
    ),

    (
        "Research Assistant: Conduct literature reviews, "
        "collect and analyze research data, prepare reports, "
        "and support academic research projects. "
        "Requires research methods, data analysis, "
        "and academic writing skills."
    )
]

# Convert the resume and jobs into numerical embeddings
resume_embedding = model.encode(
    resume_text,
    convert_to_tensor=True
)

job_embeddings = model.encode(
    jobs,
    convert_to_tensor=True
)

# Calculate cosine similarity scores
scores = util.cos_sim(
    resume_embedding,
    job_embeddings
)[0]

# Rank jobs from highest to lowest similarity
results = sorted(
    zip(jobs, scores.tolist()),
    key=lambda item: item[1],
    reverse=True
)

print("Resume category:", resumes.iloc[0]["Domain"])
print("\nRanked job matches:")

for job, score in results:
    print(f"{score:.3f} | {job}")
