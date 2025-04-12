from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

search_terms = ["cafés", "gyms", "restaurants"]
location = "Montreal"
low_rated = []

def scroll_results_panel(driver, scrolls=40, delay=5):
    scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
    for _ in range(scrolls):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(delay)


for term in search_terms:
    print(f"\n--- Searching for: {term} in {location} ---")
    
    # Go to Google Maps homepage each time to reset state
    driver.get("https://www.google.ca/maps")
    time.sleep(3)

    # Enter search term
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(f"{term} in {location}")
    search_box.send_keys(Keys.ENTER)

    time.sleep(5)  # Let results start loading
    scroll_results_panel(driver, scrolls=10, delay=2)

    # Get listings
    try:
        listings = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.Nv2PK'))
        )
    except:
        print("No listings found.")
        continue

    print(f"Found {len(listings)} results.")


    
    for i, listing in enumerate(listings):
        try:
            name = listing.find_element(By.CSS_SELECTOR, 'div.qBF1Pd').text
        except:
            name = "N/A"
    
        try:
            rating_elem = listing.find_element(By.CSS_SELECTOR, 'span[role="img"]')
            rating_text = rating_elem.get_attribute("aria-label")  # "3.8 stars 245 Reviews"
            match = re.search(r"([0-9.]+) stars", rating_text)
            rating = float(match.group(1)) if match else None
        except:
            rating_text = "N/A"
            rating = None

        try:
            address = listing.find_element(By.CSS_SELECTOR, 'div.W4Efsd span:nth-child(3)').text
        except:
            address = "N/A"

        try:
            link = listing.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = "N/A"

        if rating is not None and rating < 4.0:
            print(f"{i+1}. {name} | {rating_text} | {address} → SELECTED")
            low_rated.append({
                "business_type": term,
                "name": name,
                "rating": rating,
                "raw_label": rating_text,
                "address": address,
                "link": link
            })


    
import pandas as pd
df = pd.DataFrame(low_rated)
output_path = "data/raw/low_rated_businesses.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved {len(df)} low-rated businesses to {output_path}")

#if low_rated:
#    print("\n=== Low-Rated Businesses (< 4 stars) ===")
#    for b in low_rated:
#        print(f"\n• {b['name']}")
#        print(f"  Type: {b['business_type']}")
#        print(f"  Rating: {b['rating']} ({b['raw_label']})")
#        print(f"  Address: {b['address']}")
#        print(f"  Link: {b['link']}")
#else:
#    print("\nNo low-rated businesses found.")




