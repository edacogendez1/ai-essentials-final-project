
# AI Job Search Assistant

**AI Essentials Final Project | Eda & Yuvraj**

## Project Overview

The AI Job Search Assistant is a web-based application designed to help students and early-career professionals discover job opportunities that align with their education, professional experience, technical skills, and career preferences.

Traditional job search platforms often require users to manually browse hundreds of job postings and determine which opportunities are relevant to their qualifications. Our application aims to simplify this process by combining automated job collection, AI-powered resume matching, and personalized job recommendations.

The application retrieves job postings from company career websites, categorizes available opportunities, and uses semantic similarity to evaluate how well each job matches an uploaded resume. It also incorporates user preferences, eligibility considerations, and feedback to produce personalized recommendations.

The application is built using **Python and Streamlit**.

## Key Features

### 1. Automated Job Collection

The application collects publicly available job postings through the Greenhouse and Lever APIs.

Collected job information includes:

- Company name
- Job title
- Location
- Job description
- Employment type
- Application URL

The application consolidates job postings from multiple employers into a searchable database.

### 2. Job Classification and Filtering

Job postings are categorized to make searching more efficient.

Users can explore available opportunities using filters including:

- Company
- Job category
- Employment type
- Seniority level
- Location
- Job title or keywords

Job categories include finance, consulting, investment banking, asset management, data science, software engineering, and other professional fields.

Employment type and seniority classifications are estimated when necessary. These classifications may not always perfectly reflect the employer's requirements.

### 3. Resume Upload and Career Preferences

Users can upload their resumes and specify their career interests.

The application uses information from the uploaded resume to identify the candidate's educational background, professional experience, and relevant skills.

Users can also specify career preferences to guide the recommendation process.

### 4. AI-Powered Job Matching

The main AI component of the application is its personalized job recommendation system.

Rather than relying exclusively on exact keyword matches, the application uses **semantic similarity** to compare resumes with job descriptions.

Semantic similarity allows the model to recognize relationships between concepts even when the resume and job posting use different terminology.

For example, experience in portfolio optimization and quantitative financial analysis may be relevant to investment research positions even when the descriptions do not contain identical keywords.

The application combines semantic similarity with other matching considerations to generate a hybrid ranking score.

### 5. Eligibility-Aware Recommendations

The recommendation system considers certain educational eligibility requirements when ranking opportunities.

For example, positions explicitly targeting PhD candidates may receive a ranking penalty when the uploaded resume indicates a bachelor's or master's qualification without a PhD.

This helps reduce the prominence of positions that may not be appropriate for a candidate's educational background.

Eligibility adjustments are not a comprehensive verification of all employer requirements.

### 6. Personalized Match Scores

The application ranks job opportunities according to their calculated personalized match scores.

Each recommendation displays:

- Company name and logo
- Job title
- Location
- Personalized match score
- Visual match score indicator
- Job description
- Application link

Match scores are displayed as percentages to make the recommendations easier to interpret.

**Important:** These percentages represent normalized matching scores, not probabilities of receiving a job offer.

### 7. User Feedback

Users can provide feedback on recommendations by selecting:

- Interested
- Not Interested

The application incorporates feedback into its personalization mechanism to adjust recommendation rankings.

This feature allows the recommendation process to reflect users' expressed interests rather than relying solely on their initial resume and preferences.

### 8. Interactive User Interface

The application is developed using Streamlit and organized into three main tabs:

**Explore Jobs**

Browse available job opportunities, apply filters, view job descriptions, and access employer application pages.

**My Profile**

Upload a resume and specify career preferences.

**AI Matches**

Generate personalized job recommendations, review match scores, and provide feedback.

## Technical Architecture

The application follows a multi-stage workflow:

**Step 1 — Data Collection**

Job postings are retrieved from publicly accessible employer recruitment APIs.

**Step 2 — Data Processing**

Collected information is cleaned, standardized, and classified into relevant job categories, employment types, and seniority levels.

**Step 3 — Resume Processing**

An uploaded resume provides information about the candidate's background, experience, education, and skills.

## Data Sources and Attribution

### Resume Dataset

**CareerCorpus: A Comprehensive Dataset of Annotated Resumes**

- **Authors:** Chowdhury et al.
- **Source:** Mendeley Data
- **DOI:** [10.17632/wzzwn37gmd.1](https://doi.org/10.17632/wzzwn37gmd.1)
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Usage:** Used for developing and evaluating the resume-based job matching system.

### Job Posting Data

Job postings are collected from publicly available employer
recruitment APIs, primarily Greenhouse and Lever.

**Step 4 — Candidate Matching**

The application compares resume information with job descriptions using semantic similarity.

**Step 5 — Personalized Ranking**

The system incorporates matching scores, career preferences, and eligibility adjustments to rank job opportunities.

**Step 6 — Feedback**

User feedback can influence subsequent recommendation rankings.

**Step 7 — Recommendation Display**

The highest-ranked opportunities are presented through an interactive Streamlit interface.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Web application and interactive interface |
| Greenhouse API | Job posting collection |
| Lever API | Job posting collection |
| Pandas | Data processing and filtering |
| Semantic embedding model | Resume-to-job semantic similarity |
| PyTorch | Supporting model execution |
| HTML/CSS | User interface customization |
| GitHub | Version control and project management |

## Installation and Local Execution

### Prerequisites

- Python 3
- Git
- Internet connection for retrieving job postings

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-essentials-final-project
```

### 2. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Run the Application

```bash
python3 -m streamlit run app.py
```

### 4. Open the Application

Streamlit typically launches the application at:

http://localhost:8501

## Model Evaluation

We conducted an initial qualitative evaluation using five resumes representing different financial backgrounds:

1. Macroeconomic research
2. Asset management
3. Quantitative research
4. Investment and trading
5. Equity research

Each resume was processed through the recommendation system, and its top 10 job recommendations were manually reviewed for relevance.

We classified recommendations as:

- **Strong match:** Directly aligned with the candidate's background and professional specialization.
- **Partial match:** Related to transferable skills or experience, but not closely aligned with the candidate's primary specialization.
- **Weak match:** Limited alignment with the candidate's experience, qualifications, or professional specialization.

### Preliminary Evaluation Results

| Candidate specialization | Strong | Partial | Weak |
|---|---:|---:|---:|
| Macroeconomics | 3 | 3 | 4 |
| Asset Management | 6 | 3 | 1 |
| Quantitative Research | 6 | 2 | 2 |
| Investment & Trading | 6 | 3 | 1 |
| Equity Research | 1 | 7 | 2 |
| **Total** | **22** | **18** | **10** |

Across the five resumes, 22 of the 50 recommendations were classified as strong matches, corresponding to a preliminary strict Precision@10 of **44%**.

These results are based on a limited, subjective evaluation using candidate resumes and job titles. They should not be interpreted as a comprehensive or independently validated measure of recommendation accuracy.

### Observations

The model generally performed better for quantitative finance and trading backgrounds, identifying relevant positions in quantitative research, trading, risk analysis, and capital markets.

The model was less successful at distinguishing certain specialized career paths, particularly macroeconomic research and fundamental equity research.

Some technically oriented positions were recommended to candidates with general analytical or programming experience, even when their professional backgrounds were more closely related to investment analysis.

## Current Limitations

Although the application is a functional prototype, several limitations remain.

**1. Limited Job Coverage**

The application retrieves postings from selected companies using Greenhouse and Lever. As a result, the database does not represent all available job opportunities.

**2. Imperfect Job Classification**

Employment type, seniority level, and job category may be estimated, which can occasionally produce inaccurate classifications.

**3. Specialization Matching**

Semantic similarity can identify transferable skills but may not always distinguish between closely related professional fields.

**4. Eligibility Assessment**

The application incorporates selected educational eligibility adjustments but does not comprehensively verify graduation dates, work authorization, or all employer-specific requirements.

**5. Limited Evaluation Dataset**

Our initial testing focuses on five finance-related resumes. A larger and more diverse evaluation dataset would be necessary to assess performance across industries and experience levels.

**6. Recommendation Scores**

The personalized match scores indicate relative alignment according to the application's scoring method. They are not calibrated probabilities of employment success.

## Potential Future Improvements

Future development could include:

- Expanding job collection to additional recruitment platforms.
- Improving job-specialization classification.
- Developing more comprehensive eligibility assessments.
- Expanding the evaluation dataset across industries.
- Comparing the hybrid recommendation model against simpler matching baselines.
- Enhancing feedback-based personalization.
- Adding job-specific resume tailoring capabilities.

## Conclusion

The AI Job Search Assistant demonstrates how AI-based semantic matching can be integrated into a practical application to support job discovery.

By combining automated job collection, structured filtering, resume analysis, personalized ranking, and user feedback, the project provides an interactive system for identifying relevant career opportunities.

While the current prototype has limitations, it demonstrates the potential for AI to reduce the time and effort associated with manual job searching.

---

**Developed by Eda & Yuvraj**

*AI Essentials Final Project — University of Chicago*