# core_logic.py
# Titan V100.0 - The Brain (Core Business Logic & Calculations)
# 狀態: 策略與運算核心

import pandas as pd
import numpy as np
from scipy.stats import linregress
import google.generativeai as genai
import streamlit as st

# --- Import logic from original project files ---
from backtest import TitanBacktestEngine
from execution import CalendarAgent
from intelligence import IntelligenceIngestor
from knowledge_base import TitanKnowledgeBase
from strategy import TitanStrategyEngine

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

def calculate_geometry_metrics(df_monthly, months):
    if df_monthly is None or df_monthly.empty or len(df_monthly) < 3:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    slice_df = df_monthly.iloc[-months:] if len(df_monthly) >= months else df_monthly
    if len(slice_df) < 3: return {'angle': 0, 'r2': 0, 'slope': 0}
    log_prices = np.log(slice_df['Close'].values)
    x = np.arange(len(log_prices))
    slope, _, r_value, _, _ = linregress(x, log_prices)
    angle = np.arctan(slope * 100) * (180 / np.pi)
    return {'angle': round(np.clip(angle, -90, 90), 2), 'r2': round(r_value**2, 4), 'slope': round(slope, 6)}

def compute_7d_geometry(df_monthly):
    if df_monthly is None: return None
    periods = {'35Y': 420, '10Y': 120, '5Y': 60, '3Y': 36, '1Y': 12, '6M': 6, '3M': 3}
    results = {label: calculate_geometry_metrics(df_monthly, months) for label, months in periods.items()}
    results['acceleration'] = results['3M']['angle'] - results['1Y']['angle']
    results['phoenix_signal'] = (results['10Y']['angle'] < 0) and (results['6M']['angle'] > 25)
    return results

def titan_rating_system(geo):
    if geo is None: return ("N/A", "無數據", "數據不足", "#808080")
    a35, a10, a5, a3, a1, a6, a3m = geo['35Y']['angle'], geo['10Y']['angle'], geo['5Y']['angle'], geo['3Y']['angle'], geo['1Y']['angle'], geo['6M']['angle'], geo['3M']['angle']
    if all([a35 > 45, a10 > 45, a1 > 45, a3m > 45]): return ("SSS", "Titan (泰坦)", "全週期超過45度，神級標的", "#FFD700")
    if a1 > 40 and a6 > 45 and a3m > 50 and geo['acceleration'] > 20: return ("AAA", "Dominator (統治者)", "短期加速向上，完美趨勢", "#FF4500")
    if geo['phoenix_signal'] and a3m > 30: return ("Phoenix", "Phoenix (浴火重生)", "長空短多，逆轉信號", "#FF6347")
    # ... (add all 22 rating rules here for completeness)
    return ("BBB", "Neutral (中性)", "橫盤震蕩", "#D3D3D3") # Default case

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