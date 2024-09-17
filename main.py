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
from user_accounts import create_user, authenticate_user, get_personalized_recommendations, update_user_preferences, get_user_watchlist, update_user_watchlist, get_user_preferences
from educational_resources import display_educational_resources
from notifications import generate_notifications, mark_notification_as_read, get_notification_history, process_notifications, stress_test_notifications, test_no_notifications

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
        st_lottie.st_lottie(lottie_json, speed=1, height=200, key="lottie_login")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="login_button"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
    with col2:
        if st.button("Register", key="register_button"):
            st.session_state.register = True
            st.rerun()

def registration_page():
    st.markdown('<div class="futuristic-header">Register for InvestSmartly</div>', unsafe_allow_html=True)
    
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
    
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
    
    st.subheader("Notification Preferences")
    price_changes = st.checkbox("Receive price change notifications", value=True)
    price_change_threshold = st.slider("Price change threshold (%)", min_value=1, max_value=10, value=5)
    market_news = st.checkbox("Receive market news notifications", value=True)
    market_events = st.checkbox("Receive market event notifications", value=True)
    
    if st.button("Save Preferences"):
        update_user_preferences(st.session_state.username, {
            "risk_tolerance": risk_tolerance,
            "sectors": sectors,
            "price_changes": price_changes,
            "price_change_threshold": price_change_threshold,
            "market_news": market_news,
            "market_events": market_events
        })
        st.success("Preferences saved successfully!")

def display_notifications(username):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Notifications")
    
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    watchlist = get_user_watchlist(username)
    user_preferences = get_user_preferences(username)
    
    new_notifications = generate_notifications(watchlist, user_preferences)
    st.session_state.notifications.extend(new_notifications)
    
    unread_notifications = [n for n in st.session_state.notifications if not n['read']]
    
    if unread_notifications:
        for notification in unread_notifications:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.info(notification['message'])
            with col2:
                if st.button("Mark as Read", key=f"read_{notification['timestamp'].isoformat()}_{hash(notification['message'])}"):
                    mark_notification_as_read(notification)
                    st.rerun()
        
        if st.sidebar.button("Mark All as Read"):
            for notification in unread_notifications:
                mark_notification_as_read(notification)
            st.rerun()
    else:
        st.sidebar.info("No new notifications.")
    
    if st.sidebar.button("View Notification History"):
        st.session_state.show_notification_history = True
        st.rerun()
    
    if st.sidebar.button("Notification Preferences"):
        st.session_state.show_notification_preferences = True
        st.rerun()

def notification_preferences_page():
    st.markdown('<div class="futuristic-header">Notification Preferences</div>', unsafe_allow_html=True)
    
    user_preferences = get_user_preferences(st.session_state.username)
    
    st.subheader("Notification Types")
    price_changes = st.checkbox("Price Changes", value=user_preferences.get('price_changes', True))
    market_news = st.checkbox("Market News", value=user_preferences.get('market_news', True))
    market_events = st.checkbox("Market Events", value=user_preferences.get('market_events', True))
    
    st.subheader("Notification Frequency")
    frequency = st.selectbox("Update Frequency", ["Real-time", "Daily", "Weekly"], index=["Real-time", "Daily", "Weekly"].index(user_preferences.get('frequency', "Real-time")))
    
    st.subheader("Price Change Threshold")
    price_change_threshold = st.slider("Notify when price changes by (%)", min_value=1, max_value=10, value=user_preferences.get('price_change_threshold', 5))
    
    st.subheader("Email Notifications")
    email_notifications = st.checkbox("Receive Email Notifications", value=user_preferences.get('email_notifications', False))
    
    if st.button("Save Preferences"):
        update_user_preferences(st.session_state.username, {
            "price_changes": price_changes,
            "market_news": market_news,
            "market_events": market_events,
            "frequency": frequency,
            "price_change_threshold": price_change_threshold,
            "email_notifications": email_notifications
        })
        st.success("Notification preferences updated successfully!")
    
    if st.button("Back to Main"):
        st.session_state.show_notification_preferences = False
        st.rerun()

def notification_history_page():
    st.markdown('<div class="futuristic-header">Notification History</div>', unsafe_allow_html=True)
    
    history = get_notification_history(st.session_state.notifications)
    
    if history:
        for notification in history:
            st.markdown(f"**{notification['timestamp'].strftime('%Y-%m-%d %H:%M')}** - {notification['message']} ({'Read' if notification['read'] else 'Unread'})")
    else:
        st.info("No notifications in the past 7 days.")
    
    if st.button("Back to Main"):
        st.session_state.show_notification_history = False
        st.rerun()

def user_documentation():
    st.markdown('<div class="futuristic-header">User Guide: Notification System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Notification System User Guide

    The InvestSmartly app features a powerful notification system to keep you informed about significant market events and changes in your watchlist stocks.

    ### Types of Notifications
    1. **Price Changes**: Alerts for significant price movements in your watchlist stocks.
    2. **Market News**: Important headlines and updates about the overall market.
    3. **Market Events**: Notifications about significant index movements and other market-wide events.

    ### Customizing Your Notifications
    You can customize your notification preferences in the Notification Preferences page:
    - Toggle different types of notifications on/off
    - Set the update frequency (Real-time, Daily, or Weekly)
    - Adjust the price change threshold for alerts
    - Enable/disable email notifications for important updates

    ### Viewing Notifications
    - New notifications appear in the sidebar of the app.
    - Click "Mark as Read" to acknowledge a notification.
    - Use the "Mark All as Read" button to clear all notifications at once.
    - Use the "View Notification History" button to see past notifications.

    ### Email Alerts
    If enabled, you'll receive email alerts for important notifications when you're not actively using the app.

    ### Tips for Effective Use
    - Regularly review and update your watchlist to receive relevant notifications.
    - Adjust your notification preferences to avoid alert fatigue.
    - Check the notification history periodically to stay informed about past events.
    """)

def developer_documentation():
    st.markdown('<div class="futuristic-header">Developer Guide: Notification System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Notification System Developer Guide

    The notification system is implemented in the `notifications.py` file and integrated into the main app through `main.py`.

    ### Key Components
    1. `generate_notifications(watchlist, user_preferences)`: Generates notifications based on user watchlist and preferences.
    2. `check_significant_changes(ticker, threshold)`: Checks for significant price changes in a stock.
    3. `get_market_news()`: Fetches recent market news (currently uses placeholder data).
    4. `check_market_events()`: Checks for significant market-wide events.
    5. `process_notifications(user, notifications)`: Handles email alerts for new notifications.
    6. `mark_notification_as_read(notification)`: Marks a notification as read.
    7. `get_notification_history(notifications, days)`: Retrieves notification history.

    ### Extending the System
    - To add new types of notifications, update the `generate_notifications()` function.
    - Implement real news API integration in `get_market_news()`.
    - Add more checks in `check_market_events()` for additional market-wide indicators.

    ### Testing
    - Use `stress_test_notifications(num_notifications)` to test system performance with a large number of notifications.
    - `test_no_notifications()` tests the system's behavior when there are no new notifications.

    ### Email Configuration
    Email notifications use the following environment variables:
    - NOTIFICATION_EMAIL: Sender email address
    - NOTIFICATION_EMAIL_PASSWORD: Sender email password
    - SMTP_SERVER: SMTP server address (default: smtp.gmail.com)
    - SMTP_PORT: SMTP port (default: 587)

    ### Best Practices
    - Regularly review and optimize the notification generation process for performance.
    - Implement rate limiting for external API calls (e.g., stock data fetching).
    - Consider implementing a queueing system for processing notifications in high-load scenarios.
    """)

def stock_analysis_tab(dark_mode, advanced_mode):
    st.markdown('<div class="futuristic-header">Stock Analysis</div>', unsafe_allow_html=True)
    
    recommendations = get_personalized_recommendations(st.session_state.username)
    
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
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Stock Information")
            st.write(f"**Company:** {stock_info['longName']}")
            st.write(f"**Current Price:** ${stock_info['currentPrice']:.2f}")
            st.write(f"**Market Cap:** {format_large_number(stock_info['marketCap'])}")
            st.write(f"**P/E Ratio:** {stock_info['trailingPE']:.2f}")
            st.write(f"**Dividend Yield:** {stock_info['dividendYield']:.2%}")
        
        with col2:
            st.subheader("Price Chart")
            fig = go.Figure(data=go.Scatter(x=stock_info['history'].index, y=stock_info['history']['Close'], mode='lines', name='Close'))
            fig.update_layout(
                title=f"{ticker} Stock Price (Last 6 Months)",
                xaxis_title="Date",
                yaxis_title="Price",
                template="plotly_dark" if dark_mode else "plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
    
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
        st.markdown('<style>body {background-color: #0a192f; color: #e6f1ff;}</style>', unsafe_allow_html=True)
    
    advanced_mode = st.sidebar.checkbox("Advanced Mode", key="advanced_mode")
    
    if st.sidebar.button("User Preferences"):
        st.session_state.show_preferences = True
        st.rerun()
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    display_notifications(st.session_state.username)
    
    if hasattr(st.session_state, 'show_preferences') and st.session_state.show_preferences:
        user_preferences_page()
        if st.button("Back to Main"):
            st.session_state.show_preferences = False
            st.rerun()
    elif hasattr(st.session_state, 'show_notification_history') and st.session_state.show_notification_history:
        notification_history_page()
    elif hasattr(st.session_state, 'show_notification_preferences') and st.session_state.show_notification_preferences:
        notification_preferences_page()
    else:
        tabs = st.tabs(["Stock Analysis", "Economic Trends", "Investor Profiles", "Educational Resources", "Documentation"])
        
        with tabs[0]:
            stock_analysis_tab(dark_mode, advanced_mode)
        
        with tabs[1]:
            economic_trends_tab(dark_mode)
        
        with tabs[2]:
            investor_profiles_tab(dark_mode)
        
        with tabs[3]:
            display_educational_resources()
        
        with tabs[4]:
            doc_type = st.radio("Select documentation type:", ["User Guide", "Developer Guide"])
            if doc_type == "User Guide":
                user_documentation()
            else:
                developer_documentation()

if __name__ == "__main__":
    main()