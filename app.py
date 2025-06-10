from flask import Flask, request, jsonify
import os
import time
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Set your credentials here or via environment variables in Render
SCRUSER = os.getenv("SCRUSER")
SCRPASSWORD = os.getenv("SCRPASSWORD")

def build_query_string(filters):
    parts = [f"{key} {op} {val}" for (key, op, val) in filters]
    query = " AND\n".join(parts)
    return urllib.parse.quote(query)

def build_url(filters):
    base = "https://www.screener.in/screen/raw/?sort=&order=&source_id=&query="
    query_string = build_query_string(filters)
    full_url = base + query_string
    return full_url

def login_screener(driver, username, password):
    driver.get("https://www.screener.in/login/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    driver.find_element(By.ID, "id_username").send_keys(username)
    driver.find_element(By.ID, "id_password").send_keys(password)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'form button[type="submit"]')))
    button = driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]')
    driver.execute_script("arguments[0].scrollIntoView(true);", button)
    time.sleep(0.5)
    try:
        button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", button)
    wait.until(EC.presence_of_element_located((By.ID, "nav-user-menu")))

def scrape_screened_results_paginated(driver, base_url, max_pages=5):
    wait = WebDriverWait(driver, 10)
    driver.get(base_url)
    all_data = []

    for page in range(1, max_pages + 1):
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.data-table tbody tr")))
        rows = driver.find_elements(By.CSS_SELECTOR, "table.data-table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 7:
                continue
            all_data.append({
                "Ticker": cols[0].text,
                "Market Cap": cols[1].text,
                "Price": cols[2].text,
                "PE Ratio": cols[3].text,
                "Dividend Yield": cols[4].text,
                "Profit Growth 3Y": cols[5].text,
                "Dividend Payout": cols[6].text
            })
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
            if 'disabled' in next_btn.get_attribute('class'):
                break
            next_btn.click()
            time.sleep(2)
        except Exception:
            break
    return all_data

@app.route('/scrape', methods=['POST'])
def scrape():
    # Optional: get filters from JSON POST payload
    filters = request.json.get('filters', [
        ("Market capitalization", ">", "500"),
        ("Price to earning", "<", "15"),
        ("Dividend yield", ">", "1.2"),
        ("Current price", ">", "100"),
        ("Profit growth 3Years", ">", "0"),
        ("Dividend Payout", ">", "30"),
    ])
    
    url = build_url(filters)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Unique user data directory per request to avoid conflicts
    chrome_options.add_argument(f"--user-data-dir=/tmp/selenium_user_data_{os.getpid()}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        login_screener(driver, SCRUSER, SCRPASSWORD)
        data = scrape_screened_results_paginated(driver, url, max_pages=5)
    finally:
        driver.quit()
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
