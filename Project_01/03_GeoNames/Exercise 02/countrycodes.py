import re
from collections import defaultdict
import pycountry
import csv

# Map country codes -> full name
country_names = {country.alpha_2: country.name for country in pycountry.countries}

# Create a directory for admin1 codes
country_admin_counts = defaultdict(set)

# Open the .txt file
with open('admin1CodesASCII.txt', 'r', encoding='utf=8') as file:
    content = file.readlines()

# Regex pattern of search
pattern = re.compile(r"([A-Z]{2})\.([A-Z0-9]+)")

# Extract the country and admin1 information from each line
for line in content:
    match = pattern.match(line)
    if match:
        country_code, admin_code = match.groups()
        country_admin_counts[country_code].add(admin_code)
    
# Write the CSV File
with open('country_admin_counts.csv', 'w', newline='', encoding='utf=8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Country Code', 'Country Full Name', 'Number of admin1 Regions'])

    for country_code, admin1_codes in country_admin_counts.items():
        country_full_name = country_names.get(country_code, "unknown")
        admin1_count = len(admin1_codes)
        writer.writerow([country_code, country_full_name, admin1_count])

print("CSV File ready, check your directory!")