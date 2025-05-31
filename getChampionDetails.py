
import csv
import time
import uuid
import tempfile

def get_champion_data(champion):
    url = f"https://hellhades.com/raid/champions/{champion.lower()}/"
    
    # Set up Selenium with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # You might need to specify the path to chromedriver if it's not in your PATH.
    driver = webdriver.Chrome(options=chrome_options)
    
    # Open the page
    driver.get(url)
    
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
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Locate the key-areas container
    key_area = soup.find("div", id="key-areas")
    if not key_area:
        print(f"Warning: Could not find key areas content for champion '{champion}'.")
        return None

    # Locate the ratings list inside key-area
    ratings_list = key_area.find("div", class_="raid-ratings-list")
    if not ratings_list:
        print(f"Warning: Could not find the raid ratings list for champion '{champion}'.")
        return None

    # Find all individual rating items using their class
    rating_items = ratings_list.find_all("div", class_="raid-rating")
    if not rating_items:
        print(f"Warning: No rating items found for champion '{champion}'.")
        return None

    champ_data = {}
    
    # Debug: Print each rating item text so you can inspect the data structure
    for idx, item in enumerate(rating_items):
        text = item.get_text(separator=" ", strip=True)
        print(f"Rating item {idx}: {text}")
        # The precise structure may vary—adjust the parsing logic below as needed:
        if ":" in text:
            key, value = text.split(":", 1)
            champ_data[key.strip()] = value.strip()
        else:
            # If there's no colon separator, you might handle it differently,
            # e.g., assume a known order of ratings or use additional tags.
            champ_data[f"rating_{idx}"] = text

    champ_data["Character"] = champion
    return champ_data

def write_champion_csv(champion_list, csv_filename):
    all_data = []
    for champ in champion_list:
        champ_data = get_champion_data(champ)
        if champ_data:
            all_data.append(champ_data)
    
    if not all_data:
        print("No champion data to write!")
        return

    # Combine all keys for CSV header
    header_fields = sorted({ key for data in all_data for key in data.keys() })
    
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_fields)
        writer.writeheader()
        for data in all_data:
            writer.writerow(data)
    
    print(f"CSV file '{csv_filename}' successfully created with {len(all_data)} champion(s)' data.")

# Example usage: Add more champion names to this list as needed.
champions = ["ninja"]  
csv_filename = "champion_data.csv"
write_champion_csv(champions, csv_filename)
