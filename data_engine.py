# data_engine.py
# Titan V100.0 - The Heart (Data Fetching & Caching Engine)
# 狀態: 數據核心

import pandas as pd
import yfinance as yf
from datetime import datetime
from config import Config
from macro_risk import MacroRiskEngine, STOCK_METADATA # Keep original file for now
import streamlit as st

# --- Data Fetching & Caching ---

@st.cache_data(ttl=600) # 10-minute cache for market data
def get_market_data(ticker: str, period: str = "2y", start: str = "1990-01-01"):
    """
    A centralized function for downloading stock data with caching.
    Handles .TW and .TWO fallbacks for Taiwanese stocks.
    """
    try:
        original_ticker = ticker
        
        # Handle Taiwanese stock suffixes
        if ticker.isdigit() and len(ticker) >= 4:
            ticker_tw = f"{ticker}.TW"
            df = yf.download(ticker_tw, period=period, progress=False, auto_adjust=True)
            if df.empty:
                ticker_two = f"{ticker}.TWO"
                df = yf.download(ticker_two, period=period, progress=False, auto_adjust=True)
            return df

        # For US stocks and others
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600) # 1-hour cache for full history
def download_full_history(ticker, start="1990-01-01"):
    """
    Downloads complete historical daily data and converts it to monthly.
    """
    try:
        original_ticker = ticker
        
        # Smart handling for Taiwanese stocks
        if ticker.isdigit() and len(ticker) >= 4:
            ticker_to_try = f"{ticker}.TW"
        else:
            ticker_to_try = ticker

        df = yf.download(ticker_to_try, start=start, progress=False, auto_adjust=True)
        
        # Fallback for OTC stocks
        if df.empty and original_ticker.isdigit() and len(original_ticker) >= 4:
            ticker_to_try = f"{original_ticker}.TWO"
            df = yf.download(ticker_to_try, start=start, progress=False, auto_adjust=True)
        
        if df.empty:
            return None, None

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Convert to monthly OHLC
        df_monthly = df.resample('M').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()
        
        return df, df_monthly
    except Exception:
        return None, None

# --- Engine Classes ---

# The MacroRiskEngine from macro_risk.py is a perfect fit for the data engine.
# It encapsulates fetching and processing of macro-level data.
class DataMacroRiskEngine(MacroRiskEngine):
    def __init__(self):
        super().__init__()

# The TitanIntelAgency from app.py handles fetching fundamental data and news.
class TitanIntelAgency:
    """
    V90.2 PROJECT VALKYRIE - Automatic Intelligence Fetching Engine
    Fetches fundamental data and latest news from Yahoo Finance.
    """
    def __init__(self):
        self.ticker_obj = None
    
    def fetch_full_report(self, ticker):
        try:
            original_ticker = ticker
            if ticker.isdigit() and len(ticker) >= 4:
                ticker = f"{ticker}.TW"
            
            self.ticker_obj = yf.Ticker(ticker)
            
            try:
                info = self.ticker_obj.info
                if not info or 'symbol' not in info:
                    if original_ticker.isdigit() and len(original_ticker) >= 4:
                        ticker = f"{original_ticker}.TWO"
                        self.ticker_obj = yf.Ticker(ticker)
            except:
                if original_ticker.isdigit() and len(original_ticker) >= 4:
                    ticker = f"{original_ticker}.TWO"
                    self.ticker_obj = yf.Ticker(ticker)
            
            fundamentals = self._fetch_fundamentals()
            news = self._fetch_news()
            report = self._generate_report(ticker, fundamentals, news)
            return report
        except Exception as e:
            return f"❌ **情報抓取失敗**\n\n錯誤訊息: {str(e)}"

    def _fetch_fundamentals(self):
        try:
            info = self.ticker_obj.info
            return {
                '市值': info.get('marketCap'), '現價': info.get('currentPrice'),
                'Forward PE': info.get('forwardPE'), 'PEG Ratio': info.get('pegRatio'),
                '營收成長 (YoY)': info.get('revenueGrowth'), '毛利率': info.get('grossMargins'),
                '營業利益率': info.get('operatingMargins'), 'ROE': info.get('returnOnEquity'),
                '負債比': info.get('debtToEquity'), '自由現金流': info.get('freeCashflow'),
                '機構目標價': info.get('targetMeanPrice'), '52週高點': info.get('fiftyTwoWeekHigh'),
                '52週低點': info.get('fiftyTwoWeekLow'), '產業': info.get('industry'),
                '公司簡介': info.get('longBusinessSummary')
            }
        except Exception:
            return {}

    def _fetch_news(self):
        try:
            news_list = self.ticker_obj.news[:5]
            formatted_news = []
            for item in news_list:
                timestamp = item.get('providerPublishTime', 0)
                publish_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else 'N/A'
                formatted_news.append({
                    'title': item.get('title', 'N/A'), 'publisher': item.get('publisher', 'N/A'),
                    'time': publish_time, 'link': item.get('link', '#')
                })
            return formatted_news
        except Exception:
            return []

    def _generate_report(self, ticker, fundamentals, news):
        # This is a simplified version for brevity. The full formatting logic would be here.
        report = f"# 🤖 瓦爾基里情報報告: {ticker}\n\n## 📊 基本面\n"
        for key, value in fundamentals.items():
            if value is not None:
                report += f"- **{key}**: {value}\n"
        report += "\n## 📰 最新新聞\n"
        for item in news:
            report += f"- [{item['title']}]({item['link']}) ({item['publisher']})\n"
        return report