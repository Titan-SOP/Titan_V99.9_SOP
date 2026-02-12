# core_logic.py
# Titan V100.0 - The Brain (Core Business Logic & Calculations)
# 狀態: 策略與運算核心

import numpy as np
import pandas as pd
from scipy.stats import linregress
import yfinance as yf
import streamlit as st
import google.generativeai as genai

# --- Import logic from original project files ---
from backtest import TitanBacktestEngine
from execution import CalendarAgent
from intelligence import IntelligenceIngestor
from knowledge_base import TitanKnowledgeBase
from strategy import TitanStrategyEngine
from macro_risk import MacroRiskEngine


# --- Calculation functions migrated from app.py ---

def run_fast_backtest(df, initial_capital=1000000):
    if df is None or df.empty or len(df) < 21: return None
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['Signal'] = 0
    df.loc[df['Close'] > df['MA20'], 'Signal'] = 1
    df['Pct_Change'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Pct_Change']
    df['Equity'] = (1 + df['Strategy_Return'].fillna(0)).cumprod() * initial_capital
    df['Drawdown'] = (df['Equity'] / df['Equity'].cummax()) - 1
    max_drawdown = df['Drawdown'].min()
    num_years = len(df) / 252
    total_return = df['Equity'].iloc[-1] / initial_capital - 1
    cagr = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0
    daily_returns = df['Strategy_Return'].dropna()
    sharpe_ratio = (daily_returns.mean() * 252 - 0.02) / (daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0.0
    return {"cagr": cagr, "sharpe_ratio": sharpe_ratio, "max_drawdown": max_drawdown, "equity_curve": df['Equity'], "drawdown_series": df['Drawdown'], "latest_price": df['Close'].iloc[-1]}


# ===================================================================
# [EXTRACTED] 7D Geometry & Rating Logic from source_app.py (Tab 6)
# ===================================================================

def get_time_slice(df, months):
    """
    精準切割最後 N 個月的數據片段
    """
    if df is None or df.empty:
        return df
    if len(df) >= months:
        return df.iloc[-months:]
    return df

def download_full_history(ticker, start="1990-01-01"):
    """
    下載完整歷史月K線數據, 支援台股上市(.TW)與上櫃(.TWO)
    """
    try:
        original_ticker = ticker
        if ticker.isdigit() and len(ticker) >= 4:
            ticker = f"{ticker}.TW"
        
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        
        if df.empty and original_ticker.isdigit() and len(original_ticker) >= 4:
            ticker = f"{original_ticker}.TWO"
            df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        
        if isinstance(df.columns, pd.MultiIndex):
           df.columns = df.columns.get_level_values(0)
        
        if df.empty:
            return None, None
        
        daily_df = df.copy() # Keep daily data for other uses
        
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        df_monthly = df.resample('M').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()
        
        return df_monthly, daily_df
    
    except Exception:
        return None, None

def calculate_geometry_metrics(df, months):
    """
    計算單一時間窗口的幾何指標 (斜率, 角度, R²)
    """
    if df is None or df.empty:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    
    slice_df = get_time_slice(df, months)
    
    if len(slice_df) < 3:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    
    log_prices = np.log(slice_df['Close'].values)
    x = np.arange(len(log_prices))
    
    slope, intercept, r_value, p_value, std_err = linregress(x, log_prices)
    
    angle = np.arctan(slope * 100) * (180 / np.pi)
    angle = np.clip(angle, -90, 90)
    
    r2 = r_value ** 2
    
    return {
        'angle': round(angle, 2),
        'r2': round(r2, 4),
        'slope': round(slope, 6)
    }

def titan_rating_system(geo):
    """
    22 階泰坦信評引擎 (The 22 Scripts)
    """
    if geo is None:
        return ("N/A", "無數據", "數據不足", "#808080")
    
    angle_35y, angle_10y, angle_5y, angle_1y, angle_6m, angle_3m = geo['35Y']['angle'], geo['10Y']['angle'], geo['5Y']['angle'], geo['1Y']['angle'], geo['6M']['angle'], geo['3M']['angle']
    r2_1y, r2_3m = geo['1Y']['r2'], geo['3M']['r2']
    acceleration, phoenix = geo['acceleration'], geo['phoenix_signal']
    
    if all([angle_35y > 45, angle_10y > 45, angle_1y > 45, angle_3m > 45]):
        return ("SSS", "Titan (泰坦)", "全週期超過45度，神級標的", "#FFD700")
    if angle_1y > 40 and angle_6m > 45 and angle_3m > 50 and acceleration > 20:
        return ("AAA", "Dominator (統治者)", "短期加速向上，完美趨勢", "#FF4500")
    if phoenix and angle_3m > 30:
        return ("Phoenix", "Phoenix (浴火重生)", "長空短多，逆轉信號", "#FF6347")
    if r2_1y > 0.95 and 20 < angle_1y < 40 and acceleration > 0:
        return ("Launchpad", "Launchpad (發射台)", "線性度極高，蓄勢待發", "#32CD32")
    if angle_1y > 35 and angle_3m > 40 and r2_3m > 0.85:
        return ("AA+", "Elite (精英)", "一年期強勢上攻", "#FFA500")
    if angle_1y > 30 and angle_6m > 35:
        return ("AA", "Strong Bull (強多)", "中短期穩定上升", "#FFD700")
    if angle_1y > 25 and angle_3m > 30:
        return ("AA-", "Steady Bull (穩健多)", "趨勢健康向上", "#ADFF2F")
    if angle_6m > 20 and angle_3m > 25:
        return ("A+", "Moderate Bull (溫和多)", "短期表現良好", "#7FFF00")
    if angle_3m > 15:
        return ("A", "Weak Bull (弱多)", "短期微幅上揚", "#98FB98")
    if -5 < angle_3m < 15 and angle_1y > 0:
        return ("BBB+", "Neutral+ (中性偏多)", "盤整偏多", "#F0E68C")
    if -10 < angle_3m < 10 and -10 < angle_1y < 10:
        return ("BBB", "Neutral (中性)", "橫盤震蕩", "#D3D3D3")
    if -15 < angle_3m < 5 and angle_1y < 0:
        return ("BBB-", "Neutral- (中性偏空)", "盤整偏弱", "#DDA0DD")
    if angle_1y > 20 and angle_3m < -10:
        return ("Divergence", "Divergence (背離)", "價格創高但動能衰竭", "#FF1493")
    if -25 < angle_3m < -15 and angle_1y > -10:
        return ("BB+", "Weak Bear (弱空)", "短期下跌", "#FFA07A")
    if -35 < angle_3m < -25:
        return ("BB", "Moderate Bear (中等空)", "下跌趨勢明確", "#FF6347")
    if -45 < angle_3m < -35:
        return ("BB-", "Strong Bear (強空)", "跌勢凌厲", "#DC143C")
    if angle_3m < -45 and angle_1y < -30:
        return ("B+", "Severe Bear (重度空)", "崩跌模式", "#8B0000")
    if angle_10y < -30 and angle_3m < -40:
        return ("B", "Depression (蕭條)", "長期熊市", "#800000")
    if angle_35y < -20 and angle_10y < -35:
        return ("C", "Structural Decline (結構衰退)", "世代熊市", "#4B0082")
    if angle_3m < -60:
        return ("D", "Collapse (崩盤)", "極度危險", "#000000")
    if angle_10y < -20 and angle_3m > 15 and acceleration > 30:
        return ("Reversal", "Reversal (觸底反彈)", "熊市中的V型反轉", "#00CED1")
    return ("N/A", "Unknown (未分類)", "無法歸類", "#808080")

def compute_7d_geometry(df_monthly):
    """
    計算 7 維度完整幾何掃描並回傳包含評級的最終結果。
    此函式整合了幾何計算與評級系統。
    """
    if df_monthly is None: 
        return None

    periods = {'35Y': 420, '10Y': 120, '5Y': 60, '3Y': 36, '1Y': 12, '6M': 6, '3M': 3}
    
    geo_results = {}
    for label, months in periods.items():
        metrics = calculate_geometry_metrics(df_monthly, months)
        geo_results[label] = metrics
    
    # 計算加速度 (Acceleration)
    acceleration = geo_results['3M']['angle'] - geo_results['1Y']['angle']
    geo_results['acceleration'] = round(acceleration, 2)
    
    # 鳳凰信號 (Phoenix Signal)
    phoenix = (geo_results['10Y']['angle'] < 0) and (geo_results['6M']['angle'] > 25)
    geo_results['phoenix_signal'] = phoenix
    
    # 執行評級
    rating_level, rating_name, description, color = titan_rating_system(geo_results)
    
    # 組合最終輸出
    # 雖然原始需求回傳單一 slope/angle，但評級系統需要所有窗口的數據。
    # 此處回傳一個綜合性的結果，包含最重要的短期指標和評級。
    return {
        "slope": geo_results['3M']['slope'],
        "angle": geo_results['3M']['angle'],
        "r_squared": geo_results['3M']['r2'],
        "acceleration": geo_results['acceleration'],
        "rating": f"{rating_level} ({rating_name})",
        "color": color,
        "full_geometry": geo_results # 包含所有窗口的詳細數據供進階使用
    }

# ===================================================================

class TitanAgentCouncil:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.model = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                st.warning(f"AI 模型初始化失敗: {e}")

    def generate_battle_prompt(self, ticker, price, geo_data, rating_info, intel_text="", commander_note="", selected_principles=None):
        # This function would contain the full, detailed prompt from app.py
        return f"Analyze {ticker} at price {price} with rating {rating_info[0]}. Intel: {intel_text[:100]}..."

    def run_debate(self, *args, **kwargs):
        if not self.model:
            return "❌ **AI 功能未啟用**\n\n請在側邊欄輸入 Gemini API Key 以啟用此功能。"
        try:
            prompt = self.generate_battle_prompt(*args, **kwargs)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ **AI 辯論失敗**\n\n{str(e)}"