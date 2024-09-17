import streamlit as st
import bcrypt
import pandas as pd
from typing import Dict, List
import json
import os

# File to store user data
USER_DATA_FILE = 'user_data.json'

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

# Load user data
users_db = load_users()

def create_user(username: str, password: str) -> bool:
    if username in users_db:
        return False
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users_db[username] = {
        'password': hashed_password,
        'preferences': {},
        'watchlist': []
    }
    save_users(users_db)
    return True

def authenticate_user(username: str, password: str) -> bool:
    if username not in users_db:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), users_db[username]['password'].encode('utf-8'))

def get_user_preferences(username: str) -> Dict:
    return users_db[username]['preferences']

def update_user_preferences(username: str, preferences: Dict) -> None:
    users_db[username]['preferences'] = preferences
    save_users(users_db)

def get_user_watchlist(username: str) -> List[str]:
    return users_db[username]['watchlist']

def update_user_watchlist(username: str, watchlist: List[str]) -> None:
    users_db[username]['watchlist'] = watchlist
    save_users(users_db)

def get_personalized_recommendations(username: str) -> List[str]:
    preferences = get_user_preferences(username)
    watchlist = get_user_watchlist(username)
    
    # Implement a simple recommendation algorithm based on user preferences and watchlist
    # This is a placeholder implementation and should be replaced with a more sophisticated algorithm
    recommendations = []
    
    if 'risk_tolerance' in preferences:
        if preferences['risk_tolerance'] == 'low':
            recommendations.extend(['AAPL', 'MSFT', 'JNJ'])
        elif preferences['risk_tolerance'] == 'medium':
            recommendations.extend(['GOOGL', 'AMZN', 'V'])
        elif preferences['risk_tolerance'] == 'high':
            recommendations.extend(['TSLA', 'NVDA', 'SQ'])
    
    if 'sectors' in preferences:
        sector_recommendations = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL'],
            'Healthcare': ['JNJ', 'UNH', 'PFE'],
            'Finance': ['JPM', 'V', 'MA'],
            'Consumer': ['AMZN', 'WMT', 'HD'],
            'Energy': ['XOM', 'CVX', 'BP']
        }
        for sector in preferences['sectors']:
            recommendations.extend(sector_recommendations.get(sector, []))
    
    # Add stocks from the user's watchlist that are not already in the recommendations
    recommendations.extend([stock for stock in watchlist if stock not in recommendations])
    
    # Remove duplicates and limit to top 5 recommendations
    return list(dict.fromkeys(recommendations))[:5]
