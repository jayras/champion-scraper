from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # Run without UI
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

# Explicitly set Chromedriver path
service = Service("/home/jayras/.cache/selenium/chromedriver/linux64/137.0.7151.55/chromedriver")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.google.com")


print(driver.title)  # Test if browser launches correctly
print(driver.current_url)


driver.quit()


