from bs4 import BeautifulSoup
import requests
from time import sleep
import math  # Step 1: Import the math module

#Vendor = "microsoft"
#Product = "windows_10_21h2" 
#Version = "10.0.19044.3930"


#Vendor = "apple"
#Product = "mac" 
#Version = "14.0"

Vendor = "canonical"
Product = "ubuntu_linux" 
Version = "22.04"


# Your initial URL setup
URL = f"https://nvd.nist.gov/vuln/search/results?cpe_version=cpe%3A%2F%3A{Vendor}%3A{Product}%3A{Version}&startIndex={0}"
r = requests.get(URL)
rawHtml = r.text
soup = BeautifulSoup(rawHtml, 'html.parser')

# Find number of results
num_results = soup.find('strong', {'data-testid': 'vuln-matching-records-count'}).text

# Step 2: Replace the original calculation with this one
num_results_nearest_20 = 20 * math.ceil(int(num_results)/20)  # Adjusts rounding to ensure covering all results

print(num_results)

# Initialize a list to hold CVE details
cve_details = []

# Loop through pages
for index in range(0, num_results_nearest_20, 20):
    URL = f"https://nvd.nist.gov/vuln/search/results?cpe_version=cpe%3A%2F%3A{Vendor}%3A{Product}%3A{Version}&startIndex={index}"
    r = requests.get(URL)
    rawHtml = r.text

    # Update the soup object with the new HTML content
    soup = BeautifulSoup(rawHtml, 'html.parser')

    # Find all rows in the table
    rows = soup.find_all('tr', {'data-testid': lambda x: x and x.startswith('vuln-row')})

    # Extract details from each row
    for row in rows:
        cve_id = row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-detail-link')}).text.strip()
        summary = row.find('p', {'data-testid': lambda x: x and x.startswith('vuln-summary')}).text.strip()
        published_on = row.find('span', {'data-testid': lambda x: x and x.startswith('vuln-published-on')}).text.strip()
        cvss_v3_score = row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-cvss3-link')}).text.strip()
        cvss_v3_label = row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-cvss3-link')})['class'][1]

        # Add details to the list
        cve_details.append({
            'CVE ID': cve_id,
            'Summary': summary,
            'Published On': published_on,
            'CVSS v3 Score': cvss_v3_score,
            'CVSS v3 Label': cvss_v3_label
        })

        # Be respectful to the server: Sleep between requests
        sleep(1)

# Display extracted CVE details
print(cve_details)
