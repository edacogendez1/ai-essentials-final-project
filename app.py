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
