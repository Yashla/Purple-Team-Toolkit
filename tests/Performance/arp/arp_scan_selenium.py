from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
import time

# Function that contains the Selenium script
def run_selenium_instance(instance_number):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage") 

    # Initialize the WebDriver for this instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Navigate to the login page
        driver.get('http://192.168.0.171:5000/login')  # Ensure this URL is accessible from your local network.

        username_input = driver.find_element(By.ID, 'username')
        username_input.send_keys('yash')
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys('yash')
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(3)
        driver.get('http://192.168.0.171:5000/') 
        arp_vendor_button = driver.find_element(By.XPATH, "//button[text()='ARP-Vendor']")
        arp_vendor_button.click()
        time.sleep(3)
        network_input = driver.find_element(By.ID, 'network')
        network_input.send_keys('192.168.0.0/24')
        arp_scan_button = driver.find_element(By.XPATH, "//button[contains(text(),'ARP Scan')]")
        arp_scan_button.click()
        time.sleep(50)

    finally:
        driver.quit()

# Number of concurrent instances
num_instances = 60

with ThreadPoolExecutor(max_workers=num_instances) as executor:
    executor.map(run_selenium_instance, range(num_instances))
