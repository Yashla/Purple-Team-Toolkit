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
        driver.get('http://192.168.0.171:5000/')
        ssdp_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Evil SSDP Spoofer')]")
        ssdp_button.click()
        time.sleep(3)
        start_ssdp_button = driver.find_element(By.XPATH, "//button[contains(text(),'Start SSDP Spoofer')]")
        start_ssdp_button.click()
        time.sleep(30)
        stop_ssdp_button = driver.find_element(By.XPATH, "//button[contains(text(),'Stop SSDP Spoofer')]")
        stop_ssdp_button.click()
        time.sleep(60)

    except Exception as e:
        print(f"Instance {instance_number}: An exception occurred - {e}")
    finally:
        driver.quit()

num_instances = 10
with ThreadPoolExecutor(max_workers=num_instances) as executor:
    executor.map(run_selenium_instance, range(num_instances))
