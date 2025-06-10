import time
import pandas as pd
from yahooquery import Ticker
from fastapi import FastAPI
from typing import List

app = FastAPI()

def read_tickers(file_path: str = "tickers.txt") -> List[str]:
    try:
        with open(file_path, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def fetch_metrics(ticker: str) -> dict:
    try:
        t = Ticker(ticker)
        modules = t.all_modules.get(ticker, {})
        
        # Safely get nested data
        price = modules.get("price", {}).get("regularMarketPrice", "N/A")
        pe_ratio = modules.get("summaryDetail", {}).get("trailingPE", "N/A")
        beta = modules.get("summaryDetail", {}).get("beta", "N/A")

        return {
            "ticker": ticker,
            "price": price,
            "pe_ratio": pe_ratio,
            "beta": beta
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

@app.get("/screener")
def run_screener():
    tickers = read_tickers()
    if not tickers:
        return {"error": "tickers.txt is missing or empty"}

    results = []
    for ticker in tickers:
        results.append(fetch_metrics(ticker))
        time.sleep(2)  # Delay to avoid rate limits

    return {"data": results}
