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
        quote = t.quote.get(ticker, {})
        summary = t.summary_detail.get(ticker, {})

        return {
            "ticker": ticker,
            "price": quote.get("regularMarketPrice", "N/A"),
            "pe_ratio": quote.get("trailingPE", "N/A"),
            "beta": summary.get("beta", "N/A")
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
        time.sleep(2)  # Respect rate limits

    return {"data": results}
