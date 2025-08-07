# force rebuild
import yfinance as yf
import pandas as pd
import streamlit as st

def compute_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def passes_fundamental_criteria(stock):
    try:
        pe_ratio = stock.info.get('trailingPE', None)
        eps_growth = stock.info.get('earningsQuarterlyGrowth', None)
        return pe_ratio and eps_growth and pe_ratio < 30 and eps_growth > 0.15
    except:
        return False

def passes_technical_criteria(data):
    try:
        data['50_MA'] = data['Close'].rolling(window=50).mean()
        data['200_MA'] = data['Close'].rolling(window=200).mean()
        data['RSI'] = compute_rsi(data['Close'])
        latest = data.iloc[-1]
        return (
            latest['Close'] > latest['50_MA']
            and latest['50_MA'] > latest['200_MA']
            and latest['RSI'] < 70
        )
    except:
        return False

st.title("AI-Powered Stock Screener")

user_tickers = st.text_input(\"Enter stock tickers separated by commas\", \"AAPL,MSFT,NVDA,GOOGL,TSLA,META\")
tickers = [ticker.strip().upper() for ticker in user_tickers.split(',')]

results = []
progress = st.progress(0)

for i, ticker in enumerate(tickers):
    progress.progress((i + 1) / len(tickers))
    stock = yf.Ticker(ticker)
    data = yf.download(ticker, period='6mo', interval='1d')
    if not data.empty and passes_fundamental_criteria(stock) and passes_technical_criteria(data):
        results.append(ticker)

if results:
    st.success(\"High-Growth Stocks Identified:\")
    st.write(results)
else:
    st.warning(\"No high-growth stocks found with current filters.\")
