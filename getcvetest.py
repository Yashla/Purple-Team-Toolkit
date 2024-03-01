import requests
from bs4 import BeautifulSoup
import math
from time import sleep

def fetch_cve_details(vendor, product, version):
    cves = []  # List to store CVE details
    base_url = "https://nvd.nist.gov/vuln/search/results?cpe_version=cpe%3A%2F%3A"
    initial_url = f"{base_url}{vendor}%3A{product}%3A{version}"
    response = requests.get(f"{initial_url}&startIndex=0")
    soup = BeautifulSoup(response.text, 'html.parser')
    num_results = soup.find('strong', {'data-testid': 'vuln-matching-records-count'}).text
    num_results = int(num_results)  # Convert the total results count to an integer
    print(f"Total CVEs found on the website: {num_results}")
    num_results_nearest_20 = 20 * math.ceil(num_results/20)
    
    for index in range(0, num_results_nearest_20, 20):
        page_url = f"{initial_url}&startIndex={index}"
        response = requests.get(page_url)
        page_soup = BeautifulSoup(response.text, 'html.parser')
        rows = page_soup.find_all('tr', {'data-testid': lambda x: x and x.startswith('vuln-row')})
        
        for row in rows:
            cve_id = row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-detail-link')}).text.strip() if row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-detail-link')}) else 'Not Available'
            summary = row.find('p', {'data-testid': lambda x: x and x.startswith('vuln-summary')}).text.strip() if row.find('p', {'data-testid': lambda x: x and x.startswith('vuln-summary')}) else 'Not Available'
            cvss_v3_score = row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-cvss3-link')}).text.strip() if row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-cvss3-link')}) else 'Not Available'
            cvss_v3_label = row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-cvss3-link')})['class'][1] if row.find('a', {'data-testid': lambda x: x and x.startswith('vuln-cvss3-link')}) else 'Not Available'
            
            cves.append({
                'cve_id': cve_id,
                'summary': summary,
                'cvss_v3_score': cvss_v3_score,
                'cvss_v3_label': cvss_v3_label
            })

        sleep(3)  # Be respectful to the server

    # Print the total amount of CVEs found and the number of CVEs in the array

    print(f"Number of CVEs in the array: {len(cves)}")
    return cves

# Example usage
vendor = "apple"
product = "macos"
version = "12.6"
cves = fetch_cve_details(vendor, product, version)
for cve in cves:
    print(cve)
