import requests

def fetch_cves_for_windows_version():
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {
        "API-Key": "2b9d9304-83f3-41d2-9c2c-fa543f6563fc"
    }
    params = {
        "cpeMatchString": "cpe:2.3:o:microsoft:windows_10_21h2:10.0.19044.3930:*:*:*:*:*:*:*:*",
        "resultsPerPage": "1000"
    }
    
    response = requests.get(base_url, headers=headers, params=params)
    
    # Write the response to a text file
    with open("json_response.txt", "w") as file:
        file.write(response.text)

# Example usage
fetch_cves_for_windows_version()
