import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from stock_analysis import get_stock_info, compare_stocks
from investor_profiles import get_investor_profile, get_profile_recommendations
from economic_trends import get_economic_trends
from utils import format_large_number
import streamlit_lottie as st_lottie
import requests
import ta
import numpy as np

st.set_page_config(page_title="InvestSmartly", layout="wide")

# Load custom CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load Lottie animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Login page
def login_page():
    st.markdown('<div class="futuristic-header">Welcome to InvestSmartly</div>', unsafe_allow_html=True)
    
    # Add Lottie animation
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"
    lottie_json = load_lottieurl(lottie_url)
    if lottie_json:
        st_lottie.st_lottie(lottie_json, speed=1, height=200, key="lottie")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", key="login_button"):
        st.session_state.logged_in = True
        st.rerun()

# Rate stock function
def rate_stock(ticker):
    stock = yf.Ticker(ticker)
    pe_ratio = stock.info.get('trailingPE', 0)
    dividend_yield = stock.info.get('dividendYield', 0)
    profit_margins = stock.info.get('profitMargins', 0)
    
    score = 0
    if pe_ratio < 15:
        score += 2
    elif pe_ratio < 20:
        score += 1
    
    if dividend_yield > 0.03:
        score += 2
    elif dividend_yield > 0.01:
        score += 1
    
    if profit_margins > 0.2:
        score += 1
    
    return min(max(score, 3), 5)  # Ensure the rating is between 3 and 5

# Automated investing simulation
def simulate_automated_investing(data, buy_threshold, sell_threshold):
    balance = 10000  # Starting balance
    shares = 0
    transactions = []

    for i in range(1, len(data)):
        prev_price = data['Close'].iloc[i-1]
        current_price = data['Close'].iloc[i]
        
        if current_price < prev_price * (1 - buy_threshold/100) and balance > current_price:
            shares_to_buy = balance // current_price
            shares += shares_to_buy
            balance -= shares_to_buy * current_price
            transactions.append(f"Day {i}: Bought {shares_to_buy} shares at ${current_price:.2f}")
        
        elif current_price > prev_price * (1 + sell_threshold/100) and shares > 0:
            balance += shares * current_price
            transactions.append(f"Day {i}: Sold {shares} shares at ${current_price:.2f}")
            shares = 0

    final_value = balance + shares * data['Close'].iloc[-1]
    return final_value, transactions

# Simple mode layout
def simple_mode_layout(ticker, stock_info, dark_mode):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="futuristic-card stock-info">', unsafe_allow_html=True)
        st.subheader("Stock Information")
        st.write(f"**Company:** {stock_info['longName']}")
        st.write(f"**Current Price:** ${stock_info['currentPrice']:.2f}")
        st.write(f"**Market Cap:** {format_large_number(stock_info['marketCap'])}")
        st.write(f"**P/E Ratio:** {stock_info['trailingPE']:.2f}")
        st.write(f"**Dividend Yield:** {stock_info['dividendYield']:.2%}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="futuristic-card main-chart">', unsafe_allow_html=True)
        st.subheader("Price Chart")
        fig = go.Figure(data=go.Scatter(x=stock_info['history'].index, y=stock_info['history']['Close'], mode='lines', name='Close'))
        fig.update_layout(
            title=f"{ticker} Stock Price (Last 6 Months)",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark" if dark_mode else "plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Advanced mode layout
def advanced_mode_layout(ticker, stock_info, dark_mode):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown('<div class="futuristic-card stock-info">', unsafe_allow_html=True)
        st.subheader("Stock Information")
        rating = rate_stock(ticker)
        st.write(f"**Company:** {stock_info['longName']}")
        st.write(f"**Current Price:** ${stock_info['currentPrice']:.2f}")
        st.write(f"**Market Cap:** {format_large_number(stock_info['marketCap'])}")
        st.write(f"**P/E Ratio:** {stock_info['trailingPE']:.2f}")
        st.write(f"**Dividend Yield:** {stock_info['dividendYield']:.2%}")
        st.write(f"**Rating:** {'★' * rating}{'☆' * (5 - rating)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="futuristic-card main-chart">', unsafe_allow_html=True)
        st.subheader("Advanced Price Chart")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=stock_info['history'].index,
                                     open=stock_info['history']['Open'],
                                     high=stock_info['history']['High'],
                                     low=stock_info['history']['Low'],
                                     close=stock_info['history']['Close'],
                                     name='Price'))
        fig.update_layout(
            title=f"{ticker} Stock Price (Last 6 Months)",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark" if dark_mode else "plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="futuristic-card market-pulse">', unsafe_allow_html=True)
        st.subheader("Market Pulse")
        st.write("**Latest Market News:**")
        st.write("1. Fed announces interest rate decision")
        st.write("2. Tech stocks surge on positive earnings")
        st.write("3. Oil prices stabilize amid global tensions")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="futuristic-card automated-investing">', unsafe_allow_html=True)
    st.subheader("Automated Investing Simulation")
    col3, col4 = st.columns(2)
    with col3:
        buy_threshold = st.slider("Buy Threshold (%)", 1, 10, 5)
    with col4:
        sell_threshold = st.slider("Sell Threshold (%)", 1, 10, 5)
    
    if st.button("Run Simulation", key="run_simulation"):
        final_value, transactions = simulate_automated_investing(stock_info['history'], buy_threshold, sell_threshold)
        st.write(f"Final portfolio value: ${final_value:.2f}")
        st.write("Transaction log:")
        for transaction in transactions:
            st.write(transaction)
    st.markdown('</div>', unsafe_allow_html=True)

# Main app
def main():
    load_css()

    if not hasattr(st.session_state, 'logged_in') or not st.session_state.logged_in:
        login_page()
        return

    # Sidebar for user input and dark mode toggle
    st.sidebar.title("User Input")
    
    # Dark mode toggle
    dark_mode = st.sidebar.checkbox("Dark Mode", key="dark_mode")
    if dark_mode:
        st.markdown('<style>body {background-color: #1E1E1E; color: #FFFFFF;}</style>', unsafe_allow_html=True)
    
    # Advanced/Simple layout toggle
    advanced_mode = st.sidebar.checkbox("Advanced Mode", key="advanced_mode")
    
    # Tabs for different sections
    tabs = st.tabs(["Stock Analysis", "Economic Trends", "Investor Profiles"])
    
    with tabs[0]:
        stock_analysis_tab(dark_mode, advanced_mode)
    
    with tabs[1]:
        economic_trends_tab(dark_mode)
    
    with tabs[2]:
        investor_profiles_tab(dark_mode)

def stock_analysis_tab(dark_mode, advanced_mode):
    # Stock selection
    ticker = st.selectbox("Select a stock:", ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"], key="stock_select")

    with st.spinner("Fetching stock data..."):
        stock_info = get_stock_info(ticker)

    if stock_info:
        if advanced_mode:
            st.markdown('<div class="futuristic-header">Advanced Stock Analysis</div>', unsafe_allow_html=True)
            advanced_mode_layout(ticker, stock_info, dark_mode)
        else:
            st.markdown('<div class="futuristic-header">Simple Stock Analysis</div>', unsafe_allow_html=True)
            simple_mode_layout(ticker, stock_info, dark_mode)

def economic_trends_tab(dark_mode):
    st.markdown('<div class="futuristic-header">Economic Trends</div>', unsafe_allow_html=True)

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    with st.spinner("Fetching economic trends..."):
        economic_trends = get_economic_trends()
    st.write(economic_trends)
    st.markdown('</div>', unsafe_allow_html=True)

def investor_profiles_tab(dark_mode):
    st.markdown('<div class="futuristic-header">Investor Profiles</div>', unsafe_allow_html=True)

    investor_profile = st.selectbox(
        "Select an investor profile:",
        ["Warren Buffett", "Nancy Pelosi", "Michael Dell", "Larry Fink", "Roaring Kitty"]
    )

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.subheader("Investor Profile Recommendations")
    profile_info = get_investor_profile(investor_profile)
    st.write(f"**{investor_profile}'s Investment Style:**")
    st.write(profile_info['style'])
    
    recommendations = get_profile_recommendations(investor_profile)
    st.write("**Recommended Stocks:**")
    for stock in recommendations:
        st.write(f"- {stock}")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
