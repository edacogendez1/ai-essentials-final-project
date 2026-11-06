
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from collect_jobs import collect_all_jobs

# ----------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------

st.set_page_config(
    page_title="AI Job Search Assistant",
    layout="wide"
)

# ----------------------------------------
# WEBSITE STYLING
# ----------------------------------------

st.markdown("""
<style>

    /* Main page background */
    .stApp {
        background-color: #FCFBF8;
    }

    /* Page width and spacing */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Headings */
    h1, h2, h3 {
        color: #25352D;
        letter-spacing: -0.5px;
    }

    /* General text */
    p, label {
        color: #374151;
    }

    /* Bordered containers and job cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"][data-testid] {
        border-color: #E2E5DF;
    }

    /* Sage-green dropdown backgrounds */
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div > div {
        background-color: #EAF1E9 !important;
        border-color: #D5E2D3 !important;
        border-radius: 10px !important;
    }

    /* Dropdown text */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #25352D !important;
    }

    /* Dropdown icon */
    div[data-testid="stSelectbox"] svg {
        color: #25352D !important;
    }

    /* Text inputs */
    .stTextInput input {
        background-color: #EAF1E9 !important;
        border: 1px solid #D5E2D3 !important;
        border-radius: 10px !important;
        color: #25352D !important;
    }

    /* Input placeholders */
    .stTextInput input::placeholder {
        color: #788A7B !important;
    }

    /* Text input focus */
    .stTextInput input:focus {
        border-color: #47745E !important;
        box-shadow: 0 0 0 1px #47745E !important;
    }

    /* Employment type badge */
    .pill {
        display: inline-block;
        background-color: #E7EFE8;
        color: #355A47;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Apply button */
    .stLinkButton a[data-testid="stBaseLinkButton-primary"] {
        background-color: #47745E !important;
        border-color: #47745E !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
    }

    /* White text inside Apply button */
    .stLinkButton a[data-testid="stBaseLinkButton-primary"] p {
        color: #FFFFFF !important;
    }

    /* Apply button hover */
    .stLinkButton a[data-testid="stBaseLinkButton-primary"]:hover {
        background-color: #355A47 !important;
        border-color: #355A47 !important;
        color: #FFFFFF !important;
    }

    /* Active tab styling */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #47745E !important;
        border-bottom-color: #47745E !important;
    }

    /* Tab underline */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #47745E !important;
    }

    /* Force select dropdowns to match the sage-green inputs */
div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="select"] {
    background: #EAF1E9 !important;
    background-color: #EAF1E9 !important;
}

/* Style Streamlit's newer select control */
.stSelectbox [data-baseweb="select"] {
    background-color: #EAF1E9 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)
# ----------------------------------------
# COMPANY LOGOS
# ----------------------------------------

COMPANY_DOMAINS = {
    "Stripe": "stripe.com",
    "Palantir": "palantir.com",
    "Datadog": "datadoghq.com",
    "Airbnb": "airbnb.com",
    "Robinhood": "robinhood.com",
    "Affirm": "affirm.com",
    "DoorDash": "doordash.com",
    "Duolingo - University Recruitment": "duolingo.com",
    "IDEO": "ideo.com",
    "fairlife": "fairlife.com",
    "Figure AI": "figure.ai",
    "Figure": "figure.com",
    "FourKites": "fourkites.com",
    "CAI": "cagents.com",
    "Allegiant Air": "allegiantair.com"
}


def get_company_logo(company):
    domain = COMPANY_DOMAINS.get(company)

    if domain:
        return (
            f"https://www.google.com/s2/favicons"
            f"?domain={domain}&sz=128"
        )

    return None


# ----------------------------------------
# EMPLOYMENT TYPE
# ----------------------------------------

def classify_employment_type(title):
    title = str(title).lower()

    if "intern" in title:
        return "Internship"

    elif "part-time" in title or "part time" in title:
        return "Part-time"

    elif "contract" in title or "temporary" in title:
        return "Contract"

    else:
        return "Full-time"


# ----------------------------------------
# LIVE JOB DATA
# ----------------------------------------

@st.cache_data(ttl=21600, show_spinner=False)
def load_live_jobs():
    jobs, errors = collect_all_jobs()
    last_updated = datetime.now(timezone.utc)

    return pd.DataFrame(jobs), errors, last_updated


# ----------------------------------------
# HOMEPAGE HEADER
# ----------------------------------------

st.title("Find your next opportunity")

st.write(
    "Explore job opportunities, discover positions that "
    "match your experience, and take the next step "
    "in your career."
)

st.caption("AI Job Search Assistant | Eda & Yuvraj")

st.divider()


# ----------------------------------------
# MAIN NAVIGATION
# ----------------------------------------

explore_tab, matches_tab, profile_tab = st.tabs([
    "Explore Jobs",
    "AI Matches",
    "My Profile"
])


# ========================================
# TAB 1 — EXPLORE JOBS
# ========================================


with explore_tab:

    st.header("Explore Opportunities")
    st.caption("Find positions aligned with your career goals.")

    try:
        with st.spinner("Loading job opportunities..."):
            jobs_df, collection_errors, last_updated = load_live_jobs()

        if collection_errors:
            st.warning(
                "Some employer job boards could not be retrieved. "
                "Results may be incomplete."
            )
            with st.expander("View API errors"):
                for error in collection_errors:
                    st.write(error)

        if jobs_df.empty:
            st.info("No job postings are available right now.")

        else:
            jobs_df = jobs_df.fillna("")
            jobs_df["employment_type"] = (
                jobs_df["job_title"].apply(classify_employment_type)
            )

            st.caption(
                f"{len(jobs_df):,} available jobs across "
                f"{jobs_df['company'].nunique()} companies"
                "  |  Last updated: "
                + last_updated.strftime("%B %d, %Y at %I:%M %p UTC")
            )

            st.write("")

            # LEFT: Filters   RIGHT: Job listings
            filter_col, results_col = st.columns(
                [1, 2.3],
                gap="large"
            )

            # --------------------------------
            # LEFT FILTER PANEL
            # --------------------------------

            with filter_col:
                with st.container(border=True):

                    st.subheader("Filters")

                    companies = ["All Companies"] + sorted(
                        jobs_df["company"].unique().tolist()
                    )

                    selected_company = st.selectbox(
                        "Company",
                        companies,
                        key="job_search_company"
                    )

                    selected_employment = st.selectbox(
                        "Employment Type (estimated)",
                        [
                            "Full-time",
                            "Part-time",
                            "Internship",
                            "Contract",
                            "All Types"
                        ],
                        key="job_search_employment"
                    )

                    location_search = st.text_input(
                        "Location",
                        placeholder="Any location",
                        key="job_search_location"
                    )

                    keyword_search = st.text_input(
                        "Job Title or Keyword",
                        placeholder="Search positions",
                        key="job_search_keyword"
                    )

            # --------------------------------
            # APPLY FILTERS
            # --------------------------------

            filtered_jobs = jobs_df.copy()

            if selected_company != "All Companies":
                filtered_jobs = filtered_jobs[
                    filtered_jobs["company"] == selected_company
                ]

            if selected_employment != "All Types":
                filtered_jobs = filtered_jobs[
                    filtered_jobs["employment_type"]
                    == selected_employment
                ]

            if location_search:
                filtered_jobs = filtered_jobs[
                    filtered_jobs["location"].str.contains(
                        location_search,
                        case=False,
                        regex=False
                    )
                ]

            if keyword_search:
                title_matches = (
                    filtered_jobs["job_title"].str.contains(
                        keyword_search,
                        case=False,
                        regex=False
                    )
                )

                description_matches = (
                    filtered_jobs["description"].str.contains(
                        keyword_search,
                        case=False,
                        regex=False
                    )
                )

                filtered_jobs = filtered_jobs[
                    title_matches | description_matches
                ]

            # --------------------------------
            # RIGHT JOB RESULTS PANEL
            # --------------------------------

            with results_col:

                heading_col, count_col = st.columns([2, 1])

                with heading_col:
                    st.subheader("Job Opportunities")

                with count_col:
                    st.caption(
                        f"{len(filtered_jobs):,} results"
                    )

                if filtered_jobs.empty:
                    st.info(
                        "No jobs match your filters. "
                        "Try broadening your search."
                    )

                # Compact job cards
                for _, job in filtered_jobs.head(20).iterrows():

                    with st.container(border=True):

                        logo_col, details_col = st.columns(
                            [1, 6],
                            gap="medium",
                            vertical_alignment="center"
                        )

                        with logo_col:
                            logo_url = get_company_logo(
                                job["company"]
                            )

                            if logo_url:
                                st.image(logo_url, width=48)

                        with details_col:
                            st.markdown(
                                f"**{job['job_title']}**"
                            )

                            st.caption(
                                f"{job['company']}  |  "
                                f"{job['location']}"
                            )

                            st.markdown(
                                f'<span class="pill">'
                                f'{job["employment_type"]}'
                                f'</span>',
                                unsafe_allow_html=True
                            )

                        # Actions below the job details
                        description_col, apply_col = st.columns(
                            [2, 1],
                            vertical_alignment="center"
                        )

                        with description_col:
                            with st.expander("View details"):
                                st.write(job["description"])

                        with apply_col:
                            if str(job["job_url"]).startswith(
                                ("https://", "http://")
                            ):
                                st.link_button(
                                    "Apply",
                                    job["job_url"],
                                    type="primary"
                                )

                if len(filtered_jobs) > 20:
                    st.caption(
                        "Showing the first 20 matching jobs. "
                        "Pagination will be added next."
                    )

    except Exception as error:
        st.error("Unable to load job postings.")
        st.exception(error)

# ========================================
# TAB 2 — AI MATCHES
# ========================================

with matches_tab:

    st.header("Personalized Job Recommendations")

    st.write(
        "Our recommendation system will analyze your "
        "resume and career preferences to identify "
        "opportunities that align with your background."
    )

    st.info(
        "AI matching is currently under development."
    )

    st.subheader("How It Will Work")

    st.write(
        "1. Upload your resume in My Profile."
    )

    st.write(
        "2. Select your preferred industries, "
        "locations, and employment type."
    )

    st.write(
        "3. Receive personalized job recommendations "
        "ranked by relevance."
    )

    st.write(
        "4. Provide feedback to help improve "
        "future recommendations."
    )


# ========================================
# TAB 3 — MY PROFILE
# ========================================

with profile_tab:

    st.header("My Profile")

    st.write(
        "Tell us about your background and career "
        "preferences to prepare for personalized matching."
    )

    st.subheader("Resume")

    uploaded_resume = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        key="profile_resume"
    )

    if uploaded_resume is not None:
        st.success("Resume uploaded for this session.")

    st.divider()

    st.subheader("Career Preferences")

    preferred_industry = st.selectbox(
        "Preferred Industry",
        [
            "Select an industry",
            "Finance",
            "Consulting",
            "Technology",
            "Marketing",
            "Healthcare",
            "Other"
        ],
        key="profile_industry"
    )

    preferred_location = st.text_input(
        "Preferred Location",
        placeholder="Chicago, New York, Remote",
        key="profile_location"
    )

    preferred_employment = st.selectbox(
        "Preferred Employment Type",
        [
            "Full-time",
            "Internship",
            "Part-time",
            "Contract"
        ],
        key="profile_employment"
    )

    st.info(
        "Profile-based recommendations are not yet "
        "active. Your preferences will be used when "
        "we implement the AI matching system."
    )


# ----------------------------------------
# FOOTER
# ----------------------------------------

st.divider()

st.caption(
    "AI Essentials Final Project | Eda & Yuvraj"
)
