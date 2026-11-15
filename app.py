
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from collect_jobs import collect_all_jobs

from classify_jobs import (
    classify_employment_type_with_description,
    classify_seniority_with_description,
    classify_job_categories
)

from io import BytesIO
from pypdf import PdfReader
from docx import Document


def extract_resume_text(uploaded_file):
    file_bytes = uploaded_file.getvalue()

    if uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(file_bytes))
        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif uploaded_file.name.lower().endswith(".docx"):
        document = Document(BytesIO(file_bytes))
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        return ""

    return text.strip()


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
    "Allegiant Air": "allegiantair.com",
    "Adyen": "adyen.com",
    "Beyond Finance": "beyondfinance.com",
    "Supporting Strategies": "supportingstrategies.com",
    "American Institutes for Research": "air.org",
    "Reformation": "thereformation.com",
    "FAM Brands": "fambrands.com",
    "Twilio": "twilio.com",
    "Anthropic": "anthropic.com",
    "Flexport": "flexport.com",
    "Braze": "braze.com",
    "Extend": "paywithextend.com",
    "Ocrolus": "ocrolus.com",
    "Metronome": "metronome.com",
    "The Virtus Solution": "thevirtussolution.com",

    # Technology, Finance & AI
    "Scale AI": "scale.com",
    "Figma": "figma.com",
    "Chime": "chime.com",
    "Cloudflare": "cloudflare.com",
    "Reddit": "reddit.com",
    "Gusto": "gusto.com",
    "Endor Labs": "endorlabs.com",
    "Mercury": "mercury.com",
    "Chainguard": "chainguard.dev",
    "Vercel": "vercel.com",
    "Snorkel AI": "snorkel.ai",
    "Kikoff": "kikoff.com",
    "Customer.io": "customer.io",
    "Labelbox": "labelbox.com",
    "MedElite Group": "medelitegrp.com",
    "xAI": "x.ai",
    "Veeam Software": "veeam.com",
    "Rocket Lab": "rocketlabusa.com",
    "PlayStation Global": "playstation.com",
    "The Specialty Alliance": "thespecialtyalliance.com",
    "SharkNinja": "sharkninja.com",
    "GitLab": "gitlab.com",
    "Precision Medicine Group": "precisionmedicinegrp.com",
    "Voyager Technologies": "voyagertechnologies.com",
    "Praxis Precision Medicines": "praxismedicines.com",
    "Anduril Industries": "anduril.com",

    # Additional Technology & Consumer Companies
    "Databricks": "databricks.com",
    "Dropbox": "dropbox.com",
    "Instacart": "instacart.com",
    "Asana": "asana.com",
    "Discord": "discord.com",
    "Samsara": "samsara.com",
    "Twitch": "twitch.tv",
    "Pinterest": "pinterest.com",
    "MongoDB": "mongodb.com",
    "Elastic": "elastic.co",
    "Peloton": "onepeloton.com",
    "SoFi": "sofi.com",
    "Betterment": "betterment.com",
    "Airtable": "airtable.com",
    "Faire": "faire.com",

    # Final 30 Companies
    "SpaceX": "spacex.com",
    "Carvana": "carvana.com",
    "EquipmentShare": "equipmentshare.com",
    "WPP Media": "wppmedia.com",
    "Capco": "capco.com",
    "Accenture Federal Services": "accenture.com",
    "Coinbase": "coinbase.com",
    "Brex": "brex.com",
    "Axon": "axon.com",
    "Esri": "esri.com",
    "Lucid Motors": "lucidmotors.com",
    "HelloFresh": "hellofresh.com",
    "Okta": "okta.com",
    "Zscaler": "zscaler.com",
    "Nebius": "nebius.com",
    "Waymo": "waymo.com",
    "Toast": "toasttab.com",
    "CoreWeave": "coreweave.com",
    "Verkada": "verkada.com",
    "Relativity Space": "relativityspace.com",
    "Zipline": "flyzipline.com",
    "Monks": "monks.com",
    "One Medical": "onemedical.com",
    "Agoda": "agoda.com",
    "Canonical": "canonical.com",
    "Roblox": "roblox.com",
    "SentinelOne": "sentinelone.com",
    "Coupang": "coupang.com",
    "SumUp": "sumup.com",
    "Langan Engineering": "langan.com",

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
# LIVE JOB DATA
# ----------------------------------------

@st.cache_data(ttl=21600, show_spinner=False)
def load_live_jobs():
    jobs, errors = collect_all_jobs()
    last_updated = datetime.now(timezone.utc)

    return pd.DataFrame(jobs), errors, last_updated


# ----------------------------------------
# CACHED JOB CLASSIFICATION
# ----------------------------------------

@st.cache_data(show_spinner="Classifying job opportunities...")
def classify_all_jobs(jobs_df):

    jobs_df = jobs_df.copy().fillna("")

    jobs_df["employment_type"] = [
        classify_employment_type_with_description(title, description)
        for title, description in zip(
            jobs_df["job_title"], jobs_df["description"]
        )
    ]

    jobs_df["seniority_level"] = [
        classify_seniority_with_description(title, description)
        for title, description in zip(
            jobs_df["job_title"], jobs_df["description"]
        )
    ]

    jobs_df["job_categories"] = [
        classify_job_categories(title, description)
        for title, description in zip(
            jobs_df["job_title"], jobs_df["description"]
        )
    ]

    return jobs_df

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

explore_tab, profile_tab, matches_tab = st.tabs(
    ["Explore Jobs", "My Profile", "AI Matches"]
)
# ========================================
# TAB 1 — EXPLORE JOBS
# ========================================

with explore_tab:

    st.header("Explore Opportunities")
    st.caption("Find positions aligned with your career goals.")

    try:
        st.warning("Diagnostic test: job collection temporarily disabled.")
        st.stop()

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
            jobs_df = classify_all_jobs(jobs_df)

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

                    selected_category = st.selectbox(
                        "Job Category (estimated)",
                        [
                            "All Categories",
                            "Finance",
                            "Accounting",
                            "Investment Banking",
                            "Asset Management",
                            "Consulting",
                            "Strategy",
                            "Economics",
                            "Research",
                            "Software Engineering",
                            "Artificial Intelligence & Machine Learning",
                            "Data Science",
                            "Data Analytics",
                            "Cybersecurity",
                            "Information Technology",
                            "Marketing",
                            "Sales",
                            "Business Development",
                            "Operations",
                            "Supply Chain & Logistics",
                            "Human Resources",
                            "Healthcare",
                            "Legal & Compliance",
                            "Design",
                            "Communications & Public Relations",
                            "Uncategorized"
                        ],
                        key="job_search_category"
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

                    selected_seniority = st.selectbox(
                        "Seniority Level (estimated)",
                        [
                            "All Levels",
                            "Intern",
                            "Entry-level",
                            "Mid-level",
                            "Senior",
                            "Manager",
                            "Director/Executive",
                            "Level not specified"
                        ],
                        key="job_search_seniority"
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

            # Filter by job category
            if selected_category != "All Categories":
                filtered_jobs = filtered_jobs[
                    filtered_jobs["job_categories"].apply(
                        lambda categories: selected_category in categories
                    )
                ]

            if selected_employment != "All Types":
                filtered_jobs = filtered_jobs[
                    filtered_jobs["employment_type"]
                    == selected_employment
                ]

            if selected_seniority != "All Levels":
                seniority_value = (
                    "Unknown"
                    if selected_seniority == "Level not specified"
                    else selected_seniority
                )

                filtered_jobs = filtered_jobs[
                    filtered_jobs["seniority_level"]
                    == seniority_value
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


                # Reset pagination when search filters change
                current_filters = (
                    selected_company,
                    selected_category,
                    selected_employment,
                    selected_seniority,
                    location_search,
                    keyword_search
                )

                if st.session_state.get("previous_job_filters") != current_filters:
                    st.session_state.job_results_page = 1
                    st.session_state.previous_job_filters = current_filters


                # Pagination
                jobs_per_page = 20

                total_pages = max(
                    1,
                    (len(filtered_jobs) + jobs_per_page - 1)
                    // jobs_per_page
                )

                # Keep the selected page within the available range
                if "job_results_page" not in st.session_state:
                    st.session_state.job_results_page = 1

                st.session_state.job_results_page = min(
                    st.session_state.job_results_page,
                    total_pages
                )

                previous_col, page_col, next_col = st.columns([1, 2, 1])

                with previous_col:
                    if st.button(
                        "← Previous",
                        disabled=st.session_state.job_results_page == 1
                    ):
                        st.session_state.job_results_page -= 1
                        st.rerun()

                with page_col:
                    st.markdown(
                        f"**Page {st.session_state.job_results_page} "
                        f"of {total_pages}**"
                    )

                with next_col:
                    if st.button(
                        "Next →",
                        disabled=st.session_state.job_results_page == total_pages
                    ):
                        st.session_state.job_results_page += 1
                        st.rerun()

                page = st.session_state.job_results_page

                start_index = (page - 1) * jobs_per_page
                end_index = start_index + jobs_per_page

                page_jobs = filtered_jobs.iloc[
                    start_index:end_index
                ]


                # Compact job cards
                for _, job in page_jobs.iterrows():

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

                            
                            # Display employment type and seniority
                            badges = (
                                f'<span class="pill">{job["employment_type"]}</span> '
                                f'<span class="pill">'
                                f'{job["seniority_level"] if job["seniority_level"] != "Unknown" else "Level not specified"}'
                                f'</span> '
                            )

                            # Add job category badges
                            for category in job["job_categories"]:
                                if category != "Uncategorized":
                                    badges += f'<span class="pill">{category}</span> '

                            st.markdown(
                                badges,
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

    except Exception as error:
        st.error("Unable to load job postings.")
        st.exception(error)

# ========================================
# TAB 2 — AI MATCHES
# ========================================

with matches_tab:

    st.header("Personalized Job Recommendations")

    # Check whether a resume has been uploaded
    resume_text = st.session_state.get("resume_text", "")

    if resume_text:
        st.success("Your resume is ready for AI matching.")
    else:
        st.warning(
            "Please upload your resume in My Profile "
            "before generating recommendations."
        )

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
        try:
            resume_text = extract_resume_text(uploaded_resume)

            
            if resume_text:
                is_new_resume = (
                    st.session_state.get("resume_text") != resume_text
                )

                st.session_state["resume_text"] = resume_text

                if is_new_resume:
                    st.rerun()

                st.success("Resume uploaded and text extracted successfully.")
                st.caption(f"Extracted {len(resume_text):,} characters.")
            else:
                st.session_state.pop("resume_text", None)
                st.warning(
                    "We couldn't extract readable text from this resume."
                )

        except Exception:
            st.session_state.pop("resume_text", None)
            st.error(
                "We couldn't read this file. Please upload a valid PDF or DOCX."
            )
    else:
        st.session_state.pop("resume_text", None)


    st.divider()

    st.subheader("Career Preferences")

    
    preferred_categories = st.multiselect(
        "Preferred Job Categories",
        [
            "Finance",
            "Accounting",
            "Investment Banking",
            "Asset Management",
            "Consulting",
            "Strategy",
            "Economics",
            "Research",
            "Software Engineering",
            "Artificial Intelligence & Machine Learning",
            "Data Science",
            "Data Analytics",
            "Cybersecurity",
            "Information Technology",
            "Marketing",
            "Sales",
            "Business Development",
            "Operations",
            "Supply Chain & Logistics",
            "Human Resources",
            "Healthcare",
            "Legal & Compliance",
            "Design",
            "Communications & Public Relations"
        ],
        placeholder="Select your career interests",
        help="Select multiple categories to personalize your job recommendations.",
        key="profile_categories"
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

    preferred_seniority = st.selectbox(
        "Preferred Seniority Level",
        [
            "All Levels",
            "Intern",
            "Entry-level",
            "Mid-level",
            "Senior",
            "Manager",
            "Director/Executive"
        ],
        key="profile_seniority"
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
