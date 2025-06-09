from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_hellhades_page(champion):
    url = f"https://hellhades.com/raid/champions/{champion.lower().replace(" ","-")}/"
    
    # Set up Selenium with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # You might need to specify the path to chromedriver if it's not in your PATH.
    driver = webdriver.Chrome(options=chrome_options)
    
    # Open the page
    driver.get(url)
    
    if "Page not found" in driver.page_source:
        print(f"Champion '{champion}' does not exist. Skipping...")
        return None  # Exit early

    # Wait for the ratings list to load (adjust the timeout as needed)
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "raid-ratings-list"))
        WebDriverWait(driver, 10).until(element_present)
    except Exception as e:
        print(f"Timeout waiting for dynamic content on champion '{champion}':", e)
        driver.quit()
        return None

    # Optionally, wait a moment extra for safety
    time.sleep(2)
    
    # Get the fully rendered HTML page
    html = driver.page_source
    driver.quit()

    return html
