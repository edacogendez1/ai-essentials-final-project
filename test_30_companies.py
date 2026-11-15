
import csv
from collect_jobs import get_greenhouse_jobs

with open("companies.csv", newline="", encoding="utf-8") as file:
    companies = list(csv.DictReader(file))

# Test only the last 30 companies
new_companies = companies[-30:]

total = 0
working = 0

for company in new_companies:
    try:
        jobs = get_greenhouse_jobs(
            company["company"],
            company["board_id"]
        )

        count = len(jobs)
        total += count
        working += 1

        print(f'{company["company"]}: {count} jobs')

    except Exception as error:
        print(f'{company["company"]}: ERROR - {error}')

print(f"\nWorking boards: {working}/30")
print(f"Potential additional jobs: {total}")
