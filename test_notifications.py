import streamlit as st
from notifications import generate_notifications, mark_notification_as_read, get_notification_history, stress_test_notifications, test_no_notifications
from user_accounts import get_user_preferences, update_user_preferences

def test_notification_system():
    print("Starting notification system tests...")

    # Test data
    test_watchlist = ["AAPL", "GOOGL", "MSFT"]
    test_preferences = {
        "price_changes": True,
        "market_news": True,
        "market_events": True,
        "price_change_threshold": 5,
        "frequency": "Real-time",
        "email_notifications": False
    }

    # 1. Verify that notifications are generated correctly
    print("\n1. Testing notification generation:")
    notifications = generate_notifications(test_watchlist, test_preferences)
    print("Generated notifications:")
    for notification in notifications:
        print(f"- {notification['type']}: {notification['message']}")

    # 2. Test user preference settings
    print("\n2. Testing user preference settings:")
    update_user_preferences("test_user", test_preferences)
    retrieved_preferences = get_user_preferences("test_user")
    print(f"User preferences: {retrieved_preferences}")

    # Toggle notifications off
    test_preferences["price_changes"] = False
    test_preferences["market_news"] = False
    update_user_preferences("test_user", test_preferences)
    notifications = generate_notifications(test_watchlist, test_preferences)
    print("Notifications with price changes and market news turned off:")
    for notification in notifications:
        print(f"- {notification['type']}: {notification['message']}")

    # 3. Check "Mark as Read" functionality
    print("\n3. Testing 'Mark as Read' functionality:")
    if notifications:
        mark_notification_as_read(notifications[0])
        print(f"Marked notification as read: {notifications[0]['message']}")
        print(f"Is read: {notifications[0]['read']}")

    # 4. Test notification history
    print("\n4. Testing notification history:")
    history = get_notification_history(notifications)
    print(f"Notification history (last 7 days): {len(history)} notifications")

    # 5. Verify email notification system (placeholder)
    print("\n5. Email notification system:")
    print("Email notifications are currently not implemented. This would require setting up an email service.")

    # 6. Test performance with many notifications
    print("\n6. Testing performance with many notifications:")
    stress_test_notifications(1000)

    # 7. Test with no notifications
    print("\n7. Testing no notifications scenario:")
    test_no_notifications()

    print("\nNotification system tests completed.")

if __name__ == "__main__":
    test_notification_system()
