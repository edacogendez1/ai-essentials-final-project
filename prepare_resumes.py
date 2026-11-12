
import pandas as pd

# Load CareerCorpus from the local data folder
df = pd.read_excel("data/CareerCorpus resume dataset.xlsx")

# Show the dataset structure
print("Number of resumes:", len(df))
print("\nColumns:")
print(df.columns.tolist())

print("\nIndustry distribution:")
print(df["Domain"].value_counts())

# Combine relevant resume information into one text field
resume_columns = [
    "Education",
    "Skills and Achievements",
    "Experience"
]

df[resume_columns] = df[resume_columns].fillna("")

df["resume_text"] = df[resume_columns].agg(
    " ".join, axis=1
)

# Remove empty resumes
df = df[
    df["resume_text"].str.strip() != ""
].copy()

print("\nUsable resumes:", len(df))

# Save the prepared data locally
df.to_csv(
    "data/prepared_resumes.csv",
    index=False
)

print("\nPrepared resumes saved successfully.")
