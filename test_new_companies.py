
from collect_jobs import get_greenhouse_jobs

companies = {
    "Databricks": "databricks",
    "Dropbox": "dropbox",
    "Instacart": "instacart",
    "Asana": "asana",
    "Discord": "discord",
    "Samsara": "samsara",
    "Twitch": "twitch",
    "Pinterest": "pinterest",
    "MongoDB": "mongodb",
    "Elastic": "elastic",
    "Peloton": "peloton",
    "SoFi": "sofi",
    "Betterment": "betterment",
    "Amplitude": "amplitude",
    "Airtable": "airtable",
    "Faire": "faire"
}

total = 0

for company, board_id in companies.items():
    try:
        jobs = get_greenhouse_jobs(company, board_id)
        count = len(jobs)
        total += count
        print(f"{company}: {count} jobs")
    except Exception as error:
        print(f"{company}: ERROR - {error}")

print(f"\nPotential additional jobs: {total}")
