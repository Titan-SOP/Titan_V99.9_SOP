# utils_ui.py
# Titan SOP V100.0 - UI Utilities & Styling
# 功能：CSS 樣式、Lottie 動畫、評級顏色映射、UI 輔助函數
# 提取自：app.py (V82.0)
# 作者：Senior Python Architect
# 狀態：PRODUCTION READY

import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from typing import Optional, Tuple, Dict

# ==========================================
# [1] LOTTIE 動畫載入器
# ==========================================

def load_lottie_url(url: str) -> Optional[dict]:
    """
    從 URL 載入 Lottie 動畫
    
    Args:
        url: Lottie 動畫 JSON URL
    
    Returns:
        動畫數據字典或 None
    """
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        print(f"Lottie 載入失敗: {e}")
        return None


def load_lottie_local(filepath: str) -> Optional[dict]:
    """
    從本地檔案載入 Lottie 動畫
    
    Args:
        filepath: 本地 JSON 檔案路徑
    
    Returns:
        動畫數據字典或 None
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"本地 Lottie 載入失敗: {e}")
        return None


# ==========================================
# [2] 桌面版 CSS (Bloomberg Terminal 風格)
# ==========================================

DESKTOP_CSS = """
<style>
    /* Main container styling */
    .stApp {
        background-color: #1a1a1a;
        color: #FAFAFA;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #2a2a2a;
        border-right: 2px solid #444;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #00FF00;
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
        transform: translateY(-2px);
    }
    
    /* Center text inside the button */
    div.stButton > button > div {
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    
    /* DataFrames */
    .dataframe {
        font-size: 14px;
        border-collapse: collapse;
    }
    
    .dataframe th {
        background-color: #3a3a3a !important;
        color: #00FF00 !important;
        font-weight: bold;
        padding: 12px;
        text-align: left;
        border-bottom: 2px solid #00FF00;
    }
    
    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid #3a3a3a;
        color: #FAFAFA;
    }
    
    .dataframe tr:hover {
        background-color: #2a2a2a;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: bold;
        color: #00FF00;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #AAAAAA;
        text-transform: uppercase;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #2a2a2a;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #3a3a3a;
        color: #FAFAFA;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: 1px solid #444;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00FF00;
        color: #000000;
        border: none;
    }
    
    /* Alerts */
    .stSuccess {
        background-color: #1B4D3E;
        border-left: 4px solid #00FF7F;
        padding: 15px;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: #4D3E1B;
        border-left: 4px solid #FFD700;
        padding: 15px;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #4D1B1B;
        border-left: 4px solid #FF4500;
        padding: 15px;
        border-radius: 8px;
    }
    
    .stInfo {
        background-color: #1B2B4D;
        border-left: 4px solid #1E90FF;
        padding: 15px;
        border-radius: 8px;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        color: #FFFFFF;
        border: 1px solid #444;
        border-radius: 5px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00FF00;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #2a2a2a;
        color: #FFFFFF;
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background-color: #00FF00;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #00FF00;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #2a2a2a;
        color: #00FF00;
        border-radius: 5px;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background-color: #2a2a2a;
        border: 2px dashed #444;
        border-radius: 10px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}    
</style>
/* === 修復側邊欄展開按鈕 === */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0); /* 讓頂部橫條透明 */
        visibility: visible !important;  /* 強制顯示頂部區域 */
    }
    
    [data-testid="collapsedControl"] {
        color: #FFD700 !important;      /* 讓展開箭頭變成金色 */
        display: block !important;
    }
    
    /* 隱藏右上的漢堡選單 (Deploy/Settings)，只留左上的箭頭 */
    [data-testid="stToolbar"] {
        visibility: hidden;
    }
"""

# ==========================================
# [3] 移動版 CSS (Netflix/Robinhood 風格)
# ==========================================

MOBILE_CSS = """
<style>
    /* Global settings */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Hide sidebar on mobile */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide Streamlit header */
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Bottom navigation bar */
    .mobile-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, #1A1A1A 0%, #000000 100%);
        border-top: 1px solid #333333;
        padding: 12px 0;
        z-index: 1000;
        display: flex;
        justify-content: space-around;
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.5);
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #888888;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .nav-item.active {
        color: #00FF00;
        transform: scale(1.1);
    }
    
    .nav-icon {
        font-size: 24px;
        margin-bottom: 4px;
    }
    
    /* Big buttons - CRITICAL REQUIREMENT */
    .stButton > button {
        width: 100% !important;
        min-height: 60px !important;
        background: linear-gradient(135deg, #00FF00 0%, #00CC00 100%);
        color: #000000;
        font-size: 20px;
        font-weight: bold;
        border-radius: 16px;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 255, 0, 0.3);
        transition: all 0.3s;
    }
    
    .stButton > button:active {
        transform: scale(0.95);
        box-shadow: 0 2px 6px rgba(0, 255, 0, 0.5);
    }
    
    /* Cards */
    .mobile-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 100%);
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        border: 1px solid #333333;
    }
    
    /* HUD style large text */
    .hud-price {
        font-size: 72px;
        font-weight: 900;
        color: #00FF00;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        margin: 20px 0;
    }
    
    .hud-angle {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 16px 0;
    }
    
    .angle-up {
        color: #00FF7F;
        text-shadow: 0 0 15px rgba(0, 255, 127, 0.5);
    }
    
    .angle-down {
        color: #FF4500;
        text-shadow: 0 0 15px rgba(255, 69, 0, 0.5);
    }
    
    /* Chat bubbles */
    .chat-bubble {
        background-color: #2A2A2A;
        border-radius: 18px;
        padding: 16px 20px;
        margin: 12px 0;
        max-width: 85%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .chat-bubble.quant {
        background: linear-gradient(135deg, #1E3A5F 0%, #2A5280 100%);
        align-self: flex-start;
        border-bottom-left-radius: 4px;
    }
    
    .chat-bubble.burry {
        background: linear-gradient(135deg, #5F1E1E 0%, #802A2A 100%);
        align-self: flex-start;
        border-bottom-left-radius: 4px;
    }
    
    .chat-bubble.commander {
        background: linear-gradient(135deg, #5F4E1E 0%, #806A2A 100%);
        align-self: flex-end;
        border-bottom-right-radius: 4px;
    }
    
    /* TikTok style scrolling cards */
    .tiktok-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 100%);
        border-radius: 24px;
        padding: 32px 24px;
        margin: 20px 0;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
    }
    
    .tiktok-icon {
        font-size: 80px;
        margin-bottom: 24px;
    }
    
    .tiktok-title {
        font-size: 28px;
        font-weight: bold;
        color: #00FF00;
        text-align: center;
        margin-bottom: 16px;
    }
    
    .tiktok-content {
        font-size: 18px;
        line-height: 1.6;
        text-align: center;
        color: #CCCCCC;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1A1A1A;
        color: #FFFFFF;
        border: 2px solid #333333;
        border-radius: 16px;
        padding: 16px 20px;
        font-size: 18px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00FF00;
        box-shadow: 0 0 12px rgba(0, 255, 0, 0.3);
    }
    
    /* Metrics for mobile */
    [data-testid="stMetricValue"] {
        font-size: 48px;
        font-weight: 900;
        color: #00FF00;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #AAAAAA;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Swipe buttons */
    .swipe-container {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin: 24px 0;
    }
    
    .swipe-btn {
        flex: 1;
        min-height: 80px;
        border-radius: 20px;
        font-size: 24px;
        font-weight: bold;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
    }
    
    .swipe-pass {
        background: linear-gradient(135deg, #FF4500 0%, #DC143C 100%);
        color: #FFFFFF;
    }
    
    .swipe-lock {
        background: linear-gradient(135deg, #00FF7F 0%, #32CD32 100%);
        color: #000000;
    }
    
    .swipe-btn:active {
        transform: scale(0.9);
    }
    
    /* Hide elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Bottom padding to avoid nav bar overlap */
    .main .block-container {
        padding-bottom: 100px;
    }
</style>
"""

# ==========================================
# [4] 首頁特殊 CSS (保留原始樣式)
# ==========================================

HOMEPAGE_CSS = """
<style>
    /* Main container styling */
    .stApp {
        background-color: #1a1a1a;
    }
    
    /* Custom button styling for homepage navigation */
    div.stButton > button {
        background-color: #2a2a2a;
        color: #FFFFFF; /* FORCE WHITE FONT FOR VISIBILITY */
        border: 2px solid #444;
        border-radius: 10px;
        padding: 20px;
        width: 100%;
        height: 150px;
        font-size: 26px; /* INCREASED FONT SIZE */
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0); /* Initial transparent glow */
        line-height: 1.3; /* Better line spacing for two lines */
    }
    
    div.stButton > button:hover {
        border-color: #00FF00; /* Bright green border */
        color: #00FF00; /* Bright green text */
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.7); /* Green glow effect on hover */
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

# ==========================================
# [5] CSS 注入函數
# ==========================================

def inject_css(mode: str = "desktop"):
    """
    注入對應模式的 CSS
    
    Args:
        mode: "desktop", "mobile", "homepage"
    """
    if mode == "mobile":
        st.markdown(MOBILE_CSS, unsafe_allow_html=True)
    elif mode == "homepage":
        st.markdown(HOMEPAGE_CSS, unsafe_allow_html=True)
    else:
        st.markdown(DESKTOP_CSS, unsafe_allow_html=True)


# ==========================================
# [6] 評級系統顏色映射 (從 app.py 提取)
# ==========================================

RATING_COLORS = {
    # SSS-AAA 級 (金色系)
    "SSS": "#FFD700",
    "AAA": "#FF4500",
    "Phoenix": "#FF6347",
    "Launchpad": "#32CD32",
    
    # AA 級 (橙金色系)
    "AA+": "#FFA500",
    "AA": "#FFD700",
    "AA-": "#ADFF2F",
    
    # A 級 (綠色系)
    "A+": "#7FFF00",
    "A": "#98FB98",
    
    # BBB 級 (黃灰色系)
    "BBB+": "#F0E68C",
    "BBB": "#D3D3D3",
    "BBB-": "#DDA0DD",
    
    # 特殊警告
    "Divergence": "#FF1493",
    
    # BB 級 (淺紅色系)
    "BB+": "#FFA07A",
    "BB": "#FF6347",
    "BB-": "#DC143C",
    
    # B-C-D 級 (深紅到黑色)
    "B+": "#8B0000",
    "B": "#800000",
    "C": "#4B0082",
    "D": "#000000",
    
    # 特殊反轉
    "Reversal": "#00CED1",
    
    # 預設
    "N/A": "#808080",
    "Unknown": "#808080"
}


def get_rating_color(rating_level: str) -> str:
    """
    根據評級等級獲取對應顏色
    
    Args:
        rating_level: 評級等級 (如 "AAA", "BB+")
    
    Returns:
        顏色代碼 (Hex)
    """
    return RATING_COLORS.get(rating_level, "#808080")


def format_rating_badge(rating_level: str, rating_name: str, color: str = None) -> str:
    """
    生成評級徽章 HTML
    
    Args:
        rating_level: 評級等級
        rating_name: 評級名稱
        color: 顏色代碼 (可選)
    
    Returns:
        HTML 字串
    """
    if color is None:
        color = get_rating_color(rating_level)
    
    html = f"""
    <div style="
        display: inline-block;
        background-color: {color};
        color: #000000;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        margin: 4px;
    ">
        {rating_level}: {rating_name}
    </div>
    """
    return html


# ==========================================
# [7] UI 組件生成函數
# ==========================================

def create_metric_card(label: str, value: str, delta: Optional[str] = None, 
                       help_text: Optional[str] = None):
    """
    創建美化的 Metric 卡片
    
    Args:
        label: 指標標籤
        value: 指標值
        delta: 變化量
        help_text: 說明文字
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)


def create_mobile_nav_bar(active_tab: str = "home"):
    """
    創建移動版底部導航欄
    
    Args:
        active_tab: 當前激活的 Tab
    """
    nav_html = f"""
    <div class="mobile-nav">
        <div class="nav-item {'active' if active_tab == 'home' else ''}">
            <div class="nav-icon">🏠</div>
            <div>首頁</div>
        </div>
        <div class="nav-item {'active' if active_tab == 'hunt' else ''}">
            <div class="nav-icon">🎯</div>
            <div>獵殺</div>
        </div>
        <div class="nav-item {'active' if active_tab == 'analyze' else ''}">
            <div class="nav-icon">📊</div>
            <div>分析</div>
        </div>
        <div class="nav-item {'active' if active_tab == 'learn' else ''}">
            <div class="nav-icon">📚</div>
            <div>學習</div>
        </div>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)


def show_loading_skeleton():
    """顯示載入骨架屏"""
    st.markdown("""
    <div style='animation: pulse 1.5s infinite; 
                background: linear-gradient(90deg, #1A1A1A 25%, #2A2A2A 50%, #1A1A1A 75%); 
                background-size: 200% 100%; 
                height: 60px; 
                border-radius: 12px; 
                margin: 8px 0;'>
    </div>
    <style>
    @keyframes pulse {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    </style>
    """, unsafe_allow_html=True)


def create_hud_display(price: float, angle: float, g_force: float):
    """
    創建 HUD 抬頭顯示器 (移動版)
    
    Args:
        price: 當前價格
        angle: 角度
        g_force: G-Force 加速度
    """
    angle_class = "angle-up" if angle > 0 else "angle-down"
    angle_arrow = "↗️" if angle > 0 else "↘️"
    
    html = f"""
    <div class="mobile-card">
        <div class="hud-price">${price:.2f}</div>
        <div class="hud-angle {angle_class}">
            {angle_arrow} {angle:.1f}°
        </div>
        <div style="text-align: center; font-size: 24px; color: #AAA; margin-top: 16px;">
            ⚡ G-Force: {g_force:+.1f}°
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_chat_bubble(role: str, message: str):
    """
    創建聊天氣泡 (移動版)
    
    Args:
        role: 角色名稱 ("Quant", "Burry", "Commander")
        message: 訊息內容
    """
    role_class = {
        "quant": "quant",
        "burry": "burry",
        "commander": "commander"
    }.get(role.lower(), "quant")
    
    role_emoji = {
        "quant": "🤖",
        "burry": "🐻",
        "commander": "⚔️"
    }.get(role.lower(), "💬")
    
    html = f"""
    <div class="chat-bubble {role_class}">
        <div style="font-weight: bold; margin-bottom: 8px; color: #FFD700;">
            {role_emoji} {role}
        </div>
        <div style="line-height: 1.5;">
            {message}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_tiktok_card(icon: str, title: str, content: str):
    """
    創建 TikTok 風格教學卡片 (移動版)
    
    Args:
        icon: Emoji 圖標
        title: 標題
        content: 內容
    """
    html = f"""
    <div class="tiktok-card">
        <div class="tiktok-icon">{icon}</div>
        <div class="tiktok-title">{title}</div>
        <div class="tiktok-content">{content}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_swipe_buttons() -> Tuple[bool, bool]:
    """
    創建滑動操作按鈕 (移動版)
    
    Returns:
        (pass_clicked, lock_clicked)
    """
    col1, col2 = st.columns(2)
    with col1:
        pass_btn = st.button("❌ 跳過", key="swipe_pass", use_container_width=True)
    with col2:
        lock_btn = st.button("✅ 鎖定", key="swipe_lock", use_container_width=True)
    
    return pass_btn, lock_btn


# utils_ui.py 補丁內容

def get_lottie_animation(key: str) -> str:
    """獲取預設的 Lottie 動畫 URL"""
    animations = {
        # 使用更穩定的網址，或更換其他有效的 Lottie JSON 連結
        "sunrise": "https://lottie.host/801314d5-8930-466d-979c-7e930f6b489d/P9R9N6uO8c.json",
        "loading": "https://lottie.host/88168270-3490-4e7a-976c-37e0e7135e98/mK8eY2f1W0.json",
        "matrix": "https://lottie.host/e0586e96-6e3e-4363-9524-7629c5e3f7f8/Matrix.json"
    }
    return animations.get(key, "")

def inject_css(mode: str = "desktop"):
    """動態注入 CSS 樣式"""
    if mode == "desktop":
        if 'DESKTOP_CSS' in globals():
            st.markdown(DESKTOP_CSS, unsafe_allow_html=True)
    else:
        if 'MOBILE_CSS' in globals():
            st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ==========================================
# [MOBILE PATCH] 手機版專用組件 (請貼在 utils_ui.py 最下方)
# ==========================================

def get_rating_color(rating_str: str) -> str:
    """
    解析信評字串並返回對應顏色
    範例輸入: "SSS (Titan)" -> 返回 #FFD700
    """
    if not isinstance(rating_str, str):
        return "#808080"
    
    # 提取等級 (例如從 "SSS (Titan)" 提取 "SSS")
    level = rating_str.split(" ")[0]
    
    # 顏色對照表 (Titan Color Palette)
    colors = {
        "SSS": "#FFD700", "Titan": "#FFD700",
        "AAA": "#FF4500", "Dominator": "#FF4500",
        "Phoenix": "#FF6347", 
        "Launchpad": "#32CD32",
        "AA+": "#FFA500", "AA": "#FFD700", "AA-": "#ADFF2F",
        "A+": "#7FFF00", "A": "#98FB98",
        "BBB+": "#F0E68C", "BBB": "#D3D3D3", "BBB-": "#DDA0DD",
        "Divergence": "#FF1493",
        "BB+": "#FFA07A", "BB": "#FF6347", "BB-": "#DC143C",
        "B+": "#8B0000", "B": "#800000",
        "C": "#4B0082", "D": "#000000", "Reversal": "#00CED1"
    }
    return colors.get(level, "#808080")

def format_rating_badge(rating_str: str) -> str:
    """生成 HTML 評級標籤"""
    color = get_rating_color(rating_str)
    return f'<span style="background-color: {color}; color: black; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{rating_str}</span>'

def create_mobile_nav_bar():
    """
    渲染手機版底部導航欄
    使用 Streamlit Columns 模擬 App Tab Bar
    """
    st.markdown("---") # 分隔線
    
    # 定義導航項目
    nav_items = [
        ("🏠", "home", "獵殺"),
        ("📊", "analysis", "監控"),
        ("🤖", "ai", "AI"),
        ("⚙️", "settings", "設定")
    ]
    
    # 建立 4 個欄位
    cols = st.columns(4)
    
    # 當前選中的 Tab
    current_tab = st.session_state.get("mobile_tab", "home")
    
    for i, (icon, key, label) in enumerate(nav_items):
        with cols[i]:
            # 判斷是否選中，改變按鈕樣式
            is_selected = (current_tab == key)
            btn_type = "primary" if is_selected else "secondary"
            
            # 渲染按鈕
            if st.button(f"{icon}\n{label}", key=f"nav_{key}", type=btn_type, use_container_width=True):
                st.session_state.mobile_tab = key
                st.rerun()

def create_swipe_buttons() -> tuple:
    """
    渲染 Tinder 風格的左右操作按鈕
    Returns: (pass_clicked, lock_clicked)
    """
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 左邊：跳過 (紅色系)
        pass_clicked = st.button("❌ 跳過", key="btn_pass", use_container_width=True)
        
    with col2:
        # 右邊：鎖定 (綠色系)
        lock_clicked = st.button("❤️ 鎖定", key="btn_lock", use_container_width=True, type="primary")
        
    return pass_clicked, lock_clicked

# ==========================================
# [DESKTOP PATCH] 桌面版專用組件 (請貼在 utils_ui.py 最下方)
# ==========================================

def create_glowing_title(text: str) -> str:
    """
    創建帶有發光效果的標題 HTML
    """
    html = f"""
    <div style="
        text-align: center;
        margin-bottom: 30px;
        animation: fadeIn 1.5s ease-in;
    ">
        <h1 style="
            font-family: 'Roboto', sans-serif;
            color: #FFD700;
            font-size: 3em;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.7), 0 0 20px rgba(255, 215, 0, 0.5);
            margin: 0;
            font-weight: 700;
            letter-spacing: 2px;
        ">{text}</h1>
        <div style="
            height: 2px;
            background: linear-gradient(90deg, transparent, #FFD700, transparent);
            margin-top: 10px;
            width: 100%;
        "></div>
    </div>
    """
    return html


# ==========================================
# [PHASE 1 REPAIR] 側邊欄工具函數
# ==========================================

def render_sidebar_utilities():
    """
    渲染側邊欄系統工具
    
    功能：
    - 清除快取與重置
    - 情報文件上傳
    
    [V82.0 Legacy Logic Transplant]
    """
    st.divider()
    st.header("🔧 系統工具")
    
    # 清除快取按鈕
    if st.button("🗑️ 清除快取 & 重置", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ 快取已清除")
        st.rerun()
    
    st.divider()
    
    # 情報文件上傳
    st.header("📂 情報上傳")
    intel_files = st.file_uploader(
        "上傳情報文件 (PDF, TXT)",
        type=['pdf', 'txt'],
        accept_multiple_files=True,
        key="intel_files",
        help="支援多檔案上傳，用於 AI 深度分析"
    )
    
    if intel_files:
        st.session_state['intel_files'] = intel_files
        st.success(f"✅ 已上傳 {len(intel_files)} 個文件")
    else:
        st.session_state['intel_files'] = []