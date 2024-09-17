import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def check_significant_changes(ticker, threshold=5):
    """
    Check if a stock has had a significant price change in the last day.
    
    :param ticker: Stock ticker symbol
    :param threshold: Percentage change threshold
    :return: Tuple (bool, float) indicating if there's a significant change and the change percentage
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")
    
    if len(hist) < 2:
        return False, 0
    
    yesterday_close = hist['Close'].iloc[-2]
    today_close = hist['Close'].iloc[-1]
    
    change_percent = ((today_close - yesterday_close) / yesterday_close) * 100
    
    return abs(change_percent) >= threshold, change_percent

def get_market_news():
    """
    Fetch recent market news (placeholder function).
    In a real-world scenario, this would connect to a news API.
    
    :return: List of recent news headlines
    """
    # Placeholder news - in a real app, you'd fetch this from an API
    return [
        "Fed Announces Interest Rate Decision",
        "Tech Stocks Surge on Positive Earnings",
        "Oil Prices Stabilize Amid Global Tensions",
        "Major Merger Announced in Pharmaceutical Industry",
        "Cryptocurrency Market Experiences High Volatility"
    ]

def check_market_events():
    """
    Check for significant market events.
    
    :return: List of market event notifications
    """
    events = []
    
    # Check for market index movements
    indices = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "NASDAQ"
    }
    
    for symbol, name in indices.items():
        index = yf.Ticker(symbol)
        index_change = index.history(period="1d")['Close'].pct_change().iloc[-1] * 100
        
        if abs(index_change) > 1:
            direction = "up" if index_change > 0 else "down"
            events.append(f"{name} has moved {direction} by {abs(index_change):.2f}% today.")
    
    return events

def generate_notifications(watchlist, user_preferences):
    """
    Generate notifications for stocks in the watchlist, general market news, and market events.
    
    :param watchlist: List of stock tickers to monitor
    :param user_preferences: Dictionary containing user notification preferences
    :return: List of notification messages
    """
    notifications = []
    
    # Stock price changes
    if user_preferences.get('price_changes', True):
        threshold = user_preferences.get('price_change_threshold', 5)
        for ticker in watchlist:
            significant, change = check_significant_changes(ticker, threshold)
            if significant:
                direction = "up" if change > 0 else "down"
                notifications.append({
                    'type': 'price_change',
                    'message': f"{ticker} has moved {direction} by {abs(change):.2f}% in the last day.",
                    'timestamp': datetime.now(),
                    'read': False
                })
    
    # Market news
    if user_preferences.get('market_news', True):
        news = get_market_news()
        for headline in news:
            notifications.append({
                'type': 'market_news',
                'message': f"Market News: {headline}",
                'timestamp': datetime.now(),
                'read': False
            })
    
    # Market events
    if user_preferences.get('market_events', True):
        events = check_market_events()
        for event in events:
            notifications.append({
                'type': 'market_event',
                'message': event,
                'timestamp': datetime.now(),
                'read': False
            })
    
    return notifications

def mark_notification_as_read(notification):
    """
    Mark a notification as read.
    
    :param notification: The notification to mark as read
    """
    notification['read'] = True

def get_notification_history(notifications, days=7):
    """
    Get the notification history for the specified number of days.
    
    :param notifications: List of all notifications
    :param days: Number of days to include in the history
    :return: List of notifications within the specified time range
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    return [n for n in notifications if n['timestamp'] > cutoff_date]

def send_email_notification(to_email, subject, body):
    """
    Send an email notification.
    
    :param to_email: Recipient's email address
    :param subject: Email subject
    :param body: Email body
    """
    # Use environment variables for email configuration
    from_email = os.environ.get('NOTIFICATION_EMAIL')
    email_password = os.environ.get('NOTIFICATION_EMAIL_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, email_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")

def process_notifications(user, notifications):
    """
    Process notifications and send email alerts if necessary.
    
    :param user: User object containing email and notification preferences
    :param notifications: List of new notifications
    """
    if user.preferences.get('email_notifications', False):
        unread_notifications = [n for n in notifications if not n['read']]
        if unread_notifications:
            subject = "InvestSmartly: New Notifications"
            body = "You have new notifications:\n\n"
            for notification in unread_notifications:
                body += f"- {notification['message']}\n"
            body += "\nLog in to the app for more details."
            send_email_notification(user.email, subject, body)

def stress_test_notifications(num_notifications=1000):
    """
    Stress test the notification system with a large number of notifications.
    
    :param num_notifications: Number of test notifications to generate
    """
    test_notifications = []
    for i in range(num_notifications):
        test_notifications.append({
            'type': 'test',
            'message': f"Test notification {i+1}",
            'timestamp': datetime.now(),
            'read': False
        })
    
    # Measure time to process notifications
    start_time = datetime.now()
    for notification in test_notifications:
        mark_notification_as_read(notification)
    end_time = datetime.now()
    
    processing_time = (end_time - start_time).total_seconds()
    print(f"Processed {num_notifications} notifications in {processing_time:.2f} seconds")
    
    # Test notification history
    history = get_notification_history(test_notifications)
    print(f"Notification history contains {len(history)} notifications")

def test_no_notifications():
    """
    Test the behavior when there are no new notifications.
    """
    empty_watchlist = []
    user_preferences = {
        'price_changes': True,
        'market_news': True,
        'market_events': True
    }
    
    notifications = generate_notifications(empty_watchlist, user_preferences)
    print(f"Number of notifications generated: {len(notifications)}")
    
    if not notifications:
        print("System correctly handles the case when there are no new notifications")
    else:
        print("Unexpected notifications generated for an empty watchlist")

# Add these lines at the end of the file to run the tests
if __name__ == "__main__":
    print("Running stress test...")
    stress_test_notifications()
    print("\nTesting no notifications scenario...")
    test_no_notifications()
