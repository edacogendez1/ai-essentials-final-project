
import re

def classify_employment_type_with_description(title, description):
    # First, classify based on the job title
    title_type = classify_employment_type(title)

    if title_type != "Unknown":
        return title_type

    # Otherwise, examine the description
    description = str(description).lower()

    # Only classify internships from the job title,
    # never from the description

    patterns = {
        "Part-time": [
            r"\bpart[- ]time (?:position|role|job|employment)\b",
            r"\b(?:position|role|job) is part[- ]time\b"
        ],  
        "Contract": [
            r"\bfixed[- ]term contract\b",
            r"\bcontract (?:position|role|job|employment)\b",
            r"\b(?:position|role|job) is (?:a )?contract\b",
            r"\b\d+[- ]month contract\b"
        ],
        "Full-time": [
            r"\bfull[- ]time (?:position|role|job|employment)\b",
            r"\b(?:position|role|job) is full[- ]time\b",
            r"\bfull[- ]time employee\b"
        ]
    }

   
    matches = []

    for employment_type, expressions in patterns.items():
        if any(re.search(pattern, description) for pattern in expressions):
            matches.append(employment_type)

    if len(matches) == 1:
        return matches[0]

    # Default to Full-time when no clear classification is found
    return "Full-time"




def classify_employment_type(title):
    title = str(title).lower()

    if re.search(r"\bintern(ship)?\b|\bco-op\b", title):
        return "Internship"

    if re.search(r"\bpart[- ]time\b", title):
        return "Part-time"

    if re.search(r"\bcontract(or)?\b|\bfreelance\b", title):
        return "Contract"

    if re.search(r"\bfull[- ]time\b", title):
        return "Full-time"

    return "Unknown"



def classify_seniority(title):
    title = str(title).lower()

    # Internships
    if re.search(r"\bintern(ship)?\b|\bco-op\b", title):
        return "Intern"

    # Executive and director positions
    if re.search(
        r"\bchief\b|\bvice president\b|\bvp\b|\bdirector\b|\bhead of\b",
        title
    ):
        return "Director/Executive"

    # Senior specialist positions
    if re.search(
        r"\bprincipal\b|\bstaff\b|\bsenior\b|\bsr\b|\blead\b",
        title
    ):
        return "Senior"

    # Product Manager is a job function, not necessarily seniority
    if re.search(r"\bproduct manager\b", title):
        return "Unknown"

    # Explicit manager positions
    if re.search(r"\bmanager\b", title):
        return "Manager"

    # Entry-level indicators
    if re.search(
        r"\bjunior\b|\bentry[- ]level\b|\bnew grad\b|"
        r"\bgraduate\b|\bassociate\b",
        title
    ):
        return "Entry-level"

    return "Unknown"


def classify_seniority_with_description(title, description):
    # First, check whether the title specifies seniority
    title_level = classify_seniority(title)

    if title_level != "Unknown":
        return title_level

    # If not, examine the job description
    description = str(description).lower()
    # Identify explicit entry-level experience requirements
    entry_level_patterns = [
        r"\bno (?:prior |previous |professional )?experience required\b",
        r"\bno (?:prior |previous |professional )?experience necessary\b",
        r"\bno (?:prior |previous |professional )?experience needed\b",
        r"\bno minimum experience required\b",
        r"\b(?:entry[- ]level|recent graduates|new graduates)\b"
    ]

    for pattern in entry_level_patterns:
        if re.search(pattern, description):
            return "Entry-level"


    # Look for explicitly stated experience requirements
    experience_pattern = (
        r"(\d+)\s*(?:\+|[-–]\s*\d+)?\s*"
        r"years?\s+of\s+(?:relevant\s+|professional\s+)?experience"
    )

    match = re.search(experience_pattern, description)

    if match:
        years = int(match.group(1))

        if years <= 2:
            return "Entry-level"
        elif years <= 5:
            return "Mid-level"
        else:
            return "Senior"

    # Don't assume entry-level without evidence
    return "Unknown"


def classify_job_categories(title, description=""):
    title = str(title).lower()

    category_keywords = {
        "Finance": [
            "financial analyst", "finance", "treasury",
            "corporate finance", "underwriting", "credit analyst"
        ],
        "Accounting": [
            "accountant", "accounting", "audit", "tax"
        ],
        "Investment Banking": [
            "investment banking", "m&a analyst",
            "mergers and acquisitions"
        ],
        "Asset Management": [
            "asset management", "portfolio manager",
            "investment management"
        ],
        "Consulting": [
            "consultant", "consulting"
        ],
        "Strategy": [
            "strategy", "strategist", "strategic planning"
        ],
        "Economics": [
            "economist", "economic analyst",
            "economics"
        ],
        "Research": [
            "research", "research assistant",
            "research analyst"
        ],
         "Software Engineering": [
            "software engineer", "software developer",
            "backend engineer", "frontend engineer",
            "front end engineer", "front-end engineer",
            "full stack engineer", "full-stack engineer",
            "principal engineer", "engineering manager"
        ],

        "Artificial Intelligence & Machine Learning": [
             "machine learning", "ai engineer",
             "artificial intelligence", "applied ai",
             "ai architect", "llm engineer"
        ],
        "Data Science": [
            "data scientist", "data science"
        ],
        "Data Analytics": [
            "data analyst", "business intelligence",
            "analytics"
        ],
        "Cybersecurity": [
            "cybersecurity", "security engineer",
            "information security"
        ],
        "Information Technology": [
            "it support", "systems administrator",
            "information technology",
            "technical support engineer", "it specialist"
        ],
        "Marketing": [
            "marketing", "brand manager",
            "growth marketing"
        ],
        "Sales": [
            "sales", "account executive",
            "sales representative"
        ],
        "Business Development": [
            "business development", "partnerships"
        ],
        "Operations": [
            "operations", "operational excellence"
        ],
        "Supply Chain & Logistics": [
            "supply chain", "logistics", "procurement"
        ],
        "Human Resources": [
            "human resources", "recruiter",
            "talent acquisition"
        ],
        "Healthcare": [
            "clinical", "healthcare", "medical"
        ],
        "Legal & Compliance": [
            "legal", "compliance", "attorney"
        ],
        "Design": [
            "designer", "ux design", "product design"
        ],
        "Communications & Public Relations": [
            "public relations", "communications",
            "press relations"
        ]
    }


    import re

    # First, classify using the job title
    title_categories = []

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, title):
                title_categories.append(category)
                break

   
     # Prevent unrelated job functions from being classified as Finance or Research
    if re.search(
        r"\b(general counsel|legal counsel|attorney|lawyer)\b",
        title
    ):
        title_categories = [
            category for category in title_categories
            if category not in ["Finance", "Investment Banking", "Asset Management"]
        ]

    if re.search(
        r"\b(research engineer|research scientist|software engineer)\b",
        title
    ):
        title_categories = [
            category for category in title_categories
            if category != "Research"
        ]

    return title_categories if title_categories else ["Uncategorized"]


# Test our classifier on example titles
if __name__ == "__main__":

    test_titles = [
        "Financial Analyst",
        "Junior Financial Analyst",
        "Senior Risk Manager",
        "Marketing Intern",
        "Director of Finance",
        "Part-Time Accounting Assistant",
        "Contract Data Analyst"
    ]

    for title in test_titles:
        print(f"\nJob: {title}")
        print("Employment type:", classify_employment_type(title))
        print("Seniority:", classify_seniority(title))


    print("\nDESCRIPTION-BASED CLASSIFICATION TEST")

    examples = [
        ("Financial Analyst", "Requires 0-2 years of experience."),
        ("Financial Analyst", "Requires 3-5 years of experience."),
        ("Financial Analyst", "Requires 7+ years of experience."),
        ("Financial Analyst", "Strong analytical and Excel skills.")
    ]

    for title, description in examples:
        level = classify_seniority_with_description(title, description)
        print(f"{description} -> {level}")

    print("\nNEW ENTRY-LEVEL TESTS")

    entry_level_examples = [
        ("Financial Analyst", "No prior experience required."),
        ("Data Analyst", "No professional experience necessary."),
        ("Research Assistant", "Recent graduates encouraged to apply."),
        ("Financial Analyst", "Requires 5 years of experience.")
    ]

    for title, description in entry_level_examples:
        level = classify_seniority_with_description(title, description)
        print(f"{title}: {level}")


    print("\nEMPLOYMENT TYPE DESCRIPTION TESTS")

    employment_examples = [
        ("Financial Analyst", "This is a full-time position."),
        ("Data Analyst", "We are hiring for a part-time role."),
        ("Research Assistant", "This is a fixed-term contract."),
        ("Software Engineer", "Join our summer internship program."),
        ("Financial Analyst", "Strong Excel and analytical skills."),
        ("Marketing Intern", "This is a full-time internship position.")
    ]

    for title, description in employment_examples:
        employment_type = classify_employment_type_with_description(
            title, description
        )
        print(f"{title}: {employment_type}")

    print("\nJOB CATEGORY CLASSIFICATION TESTS")

    print(classify_job_categories("Investment Banking Analyst"))
    print(classify_job_categories("Machine Learning Engineer"))
    print(classify_job_categories("Strategy Consultant"))
    print(classify_job_categories("Financial Analyst"))