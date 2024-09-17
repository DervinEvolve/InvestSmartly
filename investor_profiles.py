import random

investor_profiles = {
    "Warren Buffett": {
        "style": "Value investing, focusing on undervalued companies with strong fundamentals and long-term growth potential.",
        "sectors": ["Financials", "Consumer Goods", "Energy"],
        "stocks": ["BRK.A", "BAC", "AAPL", "KO", "AXP"]
    },
    "Nancy Pelosi": {
        "style": "Growth-oriented investing with a focus on technology and healthcare sectors.",
        "sectors": ["Technology", "Healthcare", "Communication Services"],
        "stocks": ["AAPL", "MSFT", "GOOGL", "NVDA", "RBLX"]
    },
    "Michael Dell": {
        "style": "Technology-focused investing with an emphasis on hardware and software companies.",
        "sectors": ["Technology", "Cloud Computing", "Cybersecurity"],
        "stocks": ["DELL", "VMW", "CRM", "CSCO", "IBM"]
    },
    "Larry Fink": {
        "style": "Diversified investing across multiple sectors with a focus on ESG (Environmental, Social, and Governance) factors.",
        "sectors": ["Financials", "Technology", "Healthcare", "Clean Energy"],
        "stocks": ["BLK", "MSFT", "JNJ", "TSLA", "NEE"]
    },
    "Roaring Kitty": {
        "style": "Value investing with a focus on undervalued companies and potential short squeezes.",
        "sectors": ["Retail", "Technology", "Gaming"],
        "stocks": ["GME", "AMC", "BB", "PLTR", "TSLA"]
    }
}

def get_investor_profile(investor):
    return investor_profiles.get(investor, {})

def get_profile_recommendations(investor):
    profile = get_investor_profile(investor)
    return random.sample(profile.get("stocks", []), 3)
