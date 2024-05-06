from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
import time

def run_selenium_instance(instance_number):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get('http://192.168.0.171:5000/login')
        username_input = driver.find_element(By.ID, 'username')
        username_input.send_keys('yash')
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys('yash')
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(3)
        snmp_operations_button = driver.find_element(By.XPATH, "//button[contains(text(), 'SNMP Operations')]")
        snmp_operations_button.click()
        time.sleep(3)
        ip_address_input = driver.find_element(By.ID, 'set-ip-address')
        community_string_input = driver.find_element(By.ID, 'set-community-string')
        oid_input = driver.find_element(By.ID, 'set-oid')
        value_input = driver.find_element(By.ID, 'set-value')
        value_type_str_input = driver.find_element(By.ID, 'type_str')

        ip_address_input.send_keys('192.168.0.185')
        community_string_input.send_keys('yash')
        oid_input.send_keys('1.3.6.1.2.1.1.5.0')
        value_input.send_keys('selenium stress test')
        value_type_str_input.click()
        set_oid_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        set_oid_button.click()
        time.sleep(30)

        # Fill in the SNMP Walker form
        walk_ip_address_input = driver.find_element(By.ID, 'walk-ip-address')
        walk_community_string_input = driver.find_element(By.ID, 'walk-community-string')
        walk_oid_input = driver.find_element(By.ID, 'walk-oid')

        walk_ip_address_input.send_keys('192.168.0.185')
        walk_community_string_input.send_keys('yash')
        walk_oid_input.send_keys('1.3.6.1.2.1.1.5')

        # Start the SNMP walk
        start_walk_button = driver.find_element(By.XPATH, "//button[contains(text(),'Start Walk')]")
        start_walk_button.click()
        time.sleep(50)

    finally:
        driver.quit()
num_instances = 10
with ThreadPoolExecutor(max_workers=num_instances) as executor:
    executor.map(run_selenium_instance, range(num_instances))
