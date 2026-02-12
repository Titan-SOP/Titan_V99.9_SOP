# utils_ui.py
# Titan V100.0 - Shared UI Utilities & Styling
# 狀態: UI/UX 核心函式庫

import streamlit as st
import requests
from streamlit_lottie import st_lottie

def load_lottie_url(url: str):
    """Helper function to load a Lottie animation from a URL."""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- Lottie Animations ---
LOTTIE_ANIMATIONS = {
    "sunrise": "https://assets10.lottiefiles.com/packages/lf20_z2A256.json",
    "loading": "https://assets6.lottiefiles.com/packages/lf20_fityb9j4.json",
    "storm": "https://assets1.lottiefiles.com/packages/lf20_71Yrtk.json",
    "sun": "https://assets9.lottiefiles.com/packages/lf20_i7s9t2fi.json",
    "radar": "https://assets5.lottiefiles.com/packages/lf20_gcn3k22n.json",
    "treasure": "https://assets3.lottiefiles.com/packages/lf20_8s12t7ns.json"
}

# --- CSS Styles ---
DESKTOP_CSS = """
<style>
    /* Main container styling */
    .stApp {
        background-color: #1a1a1a;
        color: #FAFAFA;
    }
    /* Custom button styling for homepage navigation */
    div.stButton > button {
        background-color: #2a2a2a;
        color: #FFFFFF;
        border: 2px solid #444;
        border-radius: 10px;
        padding: 20px;
        width: 100%;
        height: 150px;
        font-size: 26px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0);
        line-height: 1.3;
    }
    div.stButton > button:hover {
        border-color: #00FF00;
        color: #00FF00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
    }
    /* Center text inside the button */
    div.stButton > button > div {
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
</style>
"""

MOBILE_CSS = """
<style>
    /* Hide Streamlit's default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    /* Big, touch-friendly buttons */
    div.stButton > button {
        min-height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        background-color: #007AFF; /* iOS Blue */
        color: white;
        border: none;
        margin-bottom: 10px;
    }
    /* Card styling */
    .mobile-card {
        background-color: #2C2C2E; /* iOS Dark Grey */
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* HUD styling */
    .hud-metric {
        font-size: 48px;
        font-weight: bold;
        color: #34C759; /* iOS Green */
        text-align: center;
    }
    .hud-label {
        font-size: 16px;
        color: #8E8E93; /* iOS Grey */
        text-align: center;
    }
    /* Chat bubble styling */
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        max-width: 80%;
        word-wrap: break-word;
    }
    .chat-bubble.quant {
        background-color: #007AFF; /* Blue */
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .chat-bubble.burry {
        background-color: #FF3B30; /* Red */
        color: white;
        margin-right: auto;
    }
    .chat-bubble.commander {
        background-color: #FF9500; /* Gold/Orange */
        color: white;
        margin-left: auto;
        text-align: right;
        border: 2px solid gold;
    }
</style>
"""