from fastapi import FastAPI
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import os

app = FastAPI()

def read_tickers_from_file(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_finviz_data(ticker: str) -> Dict:
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    result = {"ticker": ticker}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract metrics from the snapshot table
        table = soup.find("table", class_="snapshot-table2")
        if not table:
            result["error"] = "Data table not found"
            return result

        tds = table.find_all("td")
        data = {}
        for i in range(0, len(tds) - 1, 2):
            key = tds[i].text.strip()
            value = tds[i+1].text.strip()
            data[key] = value

        # Extract specific metrics
        result["price"] = data.get("Price", "N/A")
        result["pe_ratio"] = data.get("P/E", "N/A")
        result["beta"] = data.get("Beta", "N/A")

    except Exception as e:
        result["error"] = str(e)

    return result

@app.get("/scrape-from-file")
def scrape_from_file():
    file_path = "tickers.txt"
    tickers = read_tickers_from_file(file_path)
    if not tickers:
        return {"error": "tickers.txt not found or empty"}
    results = [get_finviz_data(ticker) for ticker in tickers]
    return {"data": results}
