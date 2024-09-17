import yfinance as yf
import pandas as pd

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="6mo")
        
        return {
            "longName": info.get("longName", "N/A"),
            "currentPrice": info.get("currentPrice", 0),
            "marketCap": info.get("marketCap", 0),
            "trailingPE": info.get("trailingPE", 0),
            "dividendYield": info.get("dividendYield", 0),
            "history": history
        }
    except Exception as e:
        print(f"Error fetching stock info for {ticker}: {e}")
        return None

def compare_stocks(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        data.append({
            "Ticker": ticker,
            "Company": info.get("longName", "N/A"),
            "Current Price": info.get("currentPrice", 0),
            "Market Cap": info.get("marketCap", 0),
            "P/E Ratio": info.get("trailingPE", 0),
            "Dividend Yield": info.get("dividendYield", 0),
        })
    return pd.DataFrame(data)
