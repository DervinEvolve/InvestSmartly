import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from stock_analysis import get_stock_info, compare_stocks
from investor_profiles import get_investor_profile, get_profile_recommendations
from economic_trends import get_economic_trends
from utils import format_large_number
import streamlit_lottie as st_lottie
import requests
import ta
import numpy as np
from user_accounts import create_user, authenticate_user, get_personalized_recommendations, update_user_preferences, get_user_watchlist, update_user_watchlist

st.set_page_config(page_title="InvestSmartly", layout="wide")

def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def login_page():
    st.markdown('<div class="futuristic-header">Welcome to InvestSmartly</div>', unsafe_allow_html=True)
    
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"
    lottie_json = load_lottieurl(lottie_url)
    if lottie_json:
        st_lottie.st_lottie(lottie_json, speed=1, height=200, key="lottie")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="login_button"):
            st.write(f"Attempting to log in with username: {username}")
            if authenticate_user(username, password):
                st.write("Authentication successful")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.write("Authentication failed")
                st.error("Invalid username or password")
    with col2:
        if st.button("Register", key="register_button"):
            st.session_state.register = True
            st.rerun()

def registration_page():
    st.markdown('<div class="futuristic-header">Register for InvestSmartly</div>', unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register", key="register_submit"):
        if password != confirm_password:
            st.error("Passwords do not match")
        elif create_user(username, password):
            st.success("Registration successful! Please log in.")
            st.session_state.register = False
            st.rerun()
        else:
            st.error("Username already exists")

def user_preferences_page():
    st.markdown('<div class="futuristic-header">User Preferences</div>', unsafe_allow_html=True)
    
    risk_tolerance = st.select_slider("Risk Tolerance", options=["low", "medium", "high"])
    sectors = st.multiselect("Preferred Sectors", ["Technology", "Healthcare", "Finance", "Consumer", "Energy"])
    
    if st.button("Save Preferences"):
        update_user_preferences(st.session_state.username, {
            "risk_tolerance": risk_tolerance,
            "sectors": sectors
        })
        st.success("Preferences saved successfully!")

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
    
    return min(max(score, 3), 5)

def simulate_automated_investing(data, buy_threshold, sell_threshold):
    balance = 10000
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

@st.cache_data
def get_stock_data(tickers, start_date, end_date):
    return yf.download(tickers=tickers, start=start_date, end=end_date)

def apply_quick_filter(filter_name):
    if filter_name == "High Dividend Yield":
        return {"min_dividend_yield": 3.0}
    elif filter_name == "Growth Stocks":
        return {"min_eps_growth": 10.0, "max_pe_ratio": 30.0}
    elif filter_name == "Value Stocks":
        return {"max_pe_ratio": 15.0, "min_dividend_yield": 2.0}
    elif filter_name == "Blue Chip Stocks":
        return {"min_market_cap": 100.0, "min_dividend_yield": 1.5}
    elif filter_name == "Momentum Stocks":
        return {"min_price_change": 10.0, "price_change_period": "1mo"}
    elif filter_name == "Oversold Stocks":
        return {"max_rsi": 30.0}
    elif filter_name == "Overbought Stocks":
        return {"min_rsi": 70.0}
    else:
        return {}

def get_filtered_stocks(filters, all_stocks_info):
    df = pd.DataFrame(all_stocks_info)
    
    for key, value in filters.items():
        if value is not None:
            if key in ["min_price", "max_price"]:
                df = df[df["price"].between(filters["min_price"] or 0, filters["max_price"] or float('inf'))]
            elif key in ["min_market_cap", "max_market_cap"]:
                df = df[df["market_cap"].between((filters["min_market_cap"] or 0) * 1e9, (filters["max_market_cap"] or float('inf')) * 1e9)]
            elif key in ["min_pe_ratio", "max_pe_ratio"]:
                df = df[df["pe_ratio"].between(filters["min_pe_ratio"] or 0, filters["max_pe_ratio"] or float('inf'))]
            elif key == "min_dividend_yield":
                df = df[df["dividend_yield"] >= filters["min_dividend_yield"] / 100]
            elif key == "sectors":
                df = df[df["sector"].isin(filters["sectors"])]
            elif key in ["min_beta", "max_beta"]:
                df = df[df["beta"].between(filters["min_beta"] or 0, filters["max_beta"] or float('inf'))]
            elif key == "min_eps":
                df = df[df["eps"] >= filters["min_eps"]]
            elif key == "min_price_change":
                df = df[df[f"price_change_{filters['price_change_period']}"] >= filters["min_price_change"]]
            elif key == "min_rsi":
                df = df[df["rsi"] >= filters["min_rsi"]]
            elif key == "max_rsi":
                df = df[df["rsi"] <= filters["max_rsi"]]
    
    return df

def save_filter_configuration(username, filter_name, filters):
    # Implement saving filter configuration to user's data
    pass

def compare_stocks(tickers, start_date, end_date, technical_indicators):
    data = get_stock_data(tickers, start_date, end_date)
    
    fig = make_subplots(rows=len(tickers), cols=1, shared_xaxes=True, vertical_spacing=0.02)
    for i, ticker in enumerate(tickers, 1):
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'][ticker], high=data['High'][ticker],
                                     low=data['Low'][ticker], close=data['Close'][ticker], name=ticker), row=i, col=1)
        
        if "MACD" in technical_indicators:
            macd = ta.trend.MACD(data['Close'][ticker])
            fig.add_trace(go.Scatter(x=data.index, y=macd.macd(), name=f"{ticker} MACD"), row=i, col=1)
        
        if "RSI" in technical_indicators:
            rsi = ta.momentum.RSIIndicator(data['Close'][ticker])
            fig.add_trace(go.Scatter(x=data.index, y=rsi.rsi(), name=f"{ticker} RSI"), row=i, col=1)
        
        if "Bollinger Bands" in technical_indicators:
            bollinger = ta.volatility.BollingerBands(data['Close'][ticker])
            fig.add_trace(go.Scatter(x=data.index, y=bollinger.bollinger_hband(), name=f"{ticker} Upper BB"), row=i, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=bollinger.bollinger_lband(), name=f"{ticker} Lower BB"), row=i, col=1)
    
    fig.update_layout(height=300*len(tickers), title_text="Stock Comparison", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

def stock_analysis_tab(dark_mode, advanced_mode):
    st.markdown('<div class="futuristic-header">Stock Analysis</div>', unsafe_allow_html=True)
    
    recommendations = get_personalized_recommendations(st.session_state.username)
    
    with st.expander("Advanced Filtering Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Price & Market Cap")
            min_price = st.number_input("Min Price ($)", min_value=0.0, step=1.0, help="Minimum stock price")
            max_price = st.number_input("Max Price ($)", min_value=0.0, step=1.0, help="Maximum stock price")
            min_market_cap = st.number_input("Min Market Cap (Billions $)", min_value=0.0, step=1.0, help="Minimum market capitalization in billions")
            max_market_cap = st.number_input("Max Market Cap (Billions $)", min_value=0.0, step=1.0, help="Maximum market capitalization in billions")
        
        with col2:
            st.subheader("Fundamentals")
            min_pe_ratio = st.number_input("Min P/E Ratio", min_value=0.0, step=0.1, help="Minimum price-to-earnings ratio")
            max_pe_ratio = st.number_input("Max P/E Ratio", min_value=0.0, step=0.1, help="Maximum price-to-earnings ratio")
            min_eps = st.number_input("Min EPS", min_value=0.0, step=0.1, help="Minimum earnings per share")
            min_dividend_yield = st.number_input("Min Dividend Yield (%)", min_value=0.0, step=0.1, help="Minimum dividend yield percentage")
        
        with col3:
            st.subheader("Performance & Volatility")
            min_beta = st.number_input("Min Beta", min_value=0.0, step=0.1, help="Minimum beta value (stock volatility)")
            max_beta = st.number_input("Max Beta", min_value=0.0, step=0.1, help="Maximum beta value (stock volatility)")
            price_change_period = st.selectbox("Price Change Period", ["1d", "5d", "1mo"], help="Time period for price change calculation")
            min_price_change = st.number_input(f"Min Price Change (%)", min_value=-100.0, max_value=100.0, step=1.0, help="Minimum price change percentage for the selected period")
        
        sectors = st.multiselect("Sectors", ["Technology", "Healthcare", "Finance", "Consumer", "Energy"], help="Select one or more sectors to filter stocks")
        
        col4, col5 = st.columns(2)
        with col4:
            start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
        with col5:
            end_date = st.date_input("End Date", value=pd.to_datetime("today"))
        
        technical_indicators = st.multiselect("Technical Indicators", ["MACD", "RSI", "Bollinger Bands"])
    
    st.subheader("Quick Filters")
    quick_filters = st.multiselect("Select quick filters", ["High Dividend Yield", "Growth Stocks", "Value Stocks", "Blue Chip Stocks", "Momentum Stocks", "Oversold Stocks", "Overbought Stocks"])
    
    if st.button("Save Current Filter"):
        filter_name = st.text_input("Enter a name for this filter configuration")
        if filter_name:
            save_filter_configuration(st.session_state.username, filter_name, filters)
            st.success(f"Filter configuration '{filter_name}' saved successfully!")
    
    saved_filters = st.selectbox("Load Saved Filter", ["None", "My Growth Filter", "My Value Filter"], help="Load a previously saved custom filter")
    
    filters = {
        "min_price": min_price,
        "max_price": max_price,
        "min_market_cap": min_market_cap,
        "max_market_cap": max_market_cap,
        "min_pe_ratio": min_pe_ratio,
        "max_pe_ratio": max_pe_ratio,
        "min_eps": min_eps,
        "min_dividend_yield": min_dividend_yield,
        "min_beta": min_beta,
        "max_beta": max_beta,
        "price_change_period": price_change_period,
        "min_price_change": min_price_change,
        "sectors": sectors
    }
    
    for quick_filter in quick_filters:
        quick_filter_values = apply_quick_filter(quick_filter)
        filters.update(quick_filter_values)
    
    if st.button("Apply Filters"):
        with st.spinner("Fetching and filtering stock data..."):
            all_stocks_data = get_stock_data(" ".join(["AAPL", "GOOGL", "MSFT", "AMZN", "FB", "TSLA", "NVDA", "JPM", "JNJ", "V"]), start_date, end_date)
            
            all_stocks_info = []
            for ticker in all_stocks_data.columns.levels[1]:
                stock = yf.Ticker(ticker)
                info = stock.info
                close_prices = all_stocks_data["Close"][ticker]
                rsi = ta.momentum.RSIIndicator(close_prices).rsi().iloc[-1]
                all_stocks_info.append({
                    "ticker": ticker,
                    "name": info.get("longName", "N/A"),
                    "sector": info.get("sector", "N/A"),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE", 0),
                    "eps": info.get("trailingEps", 0),
                    "dividend_yield": info.get("dividendYield", 0),
                    "beta": info.get("beta", 0),
                    "price": close_prices.iloc[-1],
                    "price_change_1d": (close_prices.pct_change(1).iloc[-1]) * 100,
                    "price_change_5d": (close_prices.pct_change(5).iloc[-1]) * 100,
                    "price_change_1mo": (close_prices.pct_change(20).iloc[-1]) * 100,
                    "rsi": rsi
                })
            
            filtered_stocks = get_filtered_stocks(filters, all_stocks_info)
        
        st.write("Applied Filters:")
        st.json(filters)
        
        st.write("Filtered Stocks:")
        for i in range(0, len(filtered_stocks), 10):
            page = filtered_stocks.iloc[i:i+10]
            for _, row in page.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{row['name']} ({row['ticker']})**")
                    st.write(f"Sector: {row['sector']}")
                with col2:
                    st.write(f"Price: ${row['price']:.2f}")
                    st.write(f"P/E Ratio: {row['pe_ratio']:.2f}")
                with col3:
                    if st.button("Add to Watchlist", key=f"add_watchlist_{row['ticker']}"):
                        st.success(f"Added {row['ticker']} to watchlist!")
                    if st.button("View Details", key=f"view_details_{row['ticker']}"):
                        st.info(f"Viewing details for {row['ticker']}")
            
            if i + 10 < len(filtered_stocks):
                if not st.button("Load More", key=f"load_more_{i}"):
                    break
    
    ticker_options = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"] + recommendations
    ticker = st.selectbox("Select a stock:", ticker_options, key="stock_select")
    
    if st.button("Add to Watchlist"):
        watchlist = get_user_watchlist(st.session_state.username)
        if ticker not in watchlist:
            watchlist.append(ticker)
            update_user_watchlist(st.session_state.username, watchlist)
            st.success(f"{ticker} added to your watchlist!")
        else:
            st.info(f"{ticker} is already in your watchlist.")
    
    with st.spinner("Fetching stock data..."):
        stock_info = get_stock_info(ticker)
    
    if stock_info:
        if advanced_mode:
            advanced_mode_layout(ticker, stock_info, dark_mode)
        else:
            simple_mode_layout(ticker, stock_info, dark_mode)
    
    st.subheader("Stock Comparison")
    comparison_stocks = st.multiselect("Select stocks to compare", ticker_options)
    if len(comparison_stocks) > 1:
        compare_stocks(comparison_stocks, start_date, end_date, technical_indicators)
    
    st.markdown('<div class="futuristic-card recommendations">', unsafe_allow_html=True)
    st.subheader("Personalized Recommendations")
    for rec in recommendations:
        st.write(f"- {rec}")
    st.markdown('</div>', unsafe_allow_html=True)

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

def main():
    load_css()

    if not hasattr(st.session_state, 'logged_in') or not st.session_state.logged_in:
        if hasattr(st.session_state, 'register') and st.session_state.register:
            registration_page()
        else:
            login_page()
        return

    st.sidebar.title("User Input")
    
    dark_mode = st.sidebar.checkbox("Dark Mode", key="dark_mode")
    if dark_mode:
        st.markdown('<style>body {background-color: #1E1E1E; color: #FFFFFF;}</style>', unsafe_allow_html=True)
    
    advanced_mode = st.sidebar.checkbox("Advanced Mode", key="advanced_mode")
    
    if st.sidebar.button("User Preferences"):
        st.session_state.show_preferences = True
        st.rerun()
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    if hasattr(st.session_state, 'show_preferences') and st.session_state.show_preferences:
        user_preferences_page()
        if st.button("Back to Main"):
            st.session_state.show_preferences = False
            st.rerun()
    else:
        tabs = st.tabs(["Stock Analysis", "Economic Trends", "Investor Profiles"])
        
        with tabs[0]:
            stock_analysis_tab(dark_mode, advanced_mode)
        
        with tabs[1]:
            economic_trends_tab(dark_mode)
        
        with tabs[2]:
            investor_profiles_tab(dark_mode)

if __name__ == "__main__":
    main()