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

        def extract_metric(label: str):
            cell = soup.find(text=label)
            return cell.find_next("td").text.strip() if cell else "N/A"

        result["price"] = extract_metric("Price")
        result["pe_ratio"] = extract_metric("P/E")
        result["beta"] = extract_metric("Beta")

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
