import time
import pandas as pd
from yahooquery import Ticker

def read_tickers(file_path):
    with open(file_path, 'r') as file:
        return [line.strip().upper() for line in file if line.strip()]

def fetch_metrics(ticker):
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

def main():
    tickers = read_tickers("tickers.txt")
    results = []

    for ticker in tickers:
        print(f"Fetching: {ticker}")
        data = fetch_metrics(ticker)
        results.append(data)
        time.sleep(2)  # Delay to avoid rate limiting

    df = pd.DataFrame(results)
    df.to_csv("output.csv", index=False)
    print("Saved to output.csv")

if __name__ == "__main__":
    main()
