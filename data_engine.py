# data_engine.py
# Titan SOP V100.0 - Data Engine (PHASE 1 OVERHAUL)
# 功能：Robust Data Loading + Fuzzy Mapping + CRITICAL ALIAS PATCH
# 狀態：PRODUCTION READY

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

# ==========================================
# [PHASE 1 CRITICAL FIX] Robust Data Loader
# ==========================================

def load_cb_data_from_upload(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Robust Data Loader with Fuzzy Mapping + CRITICAL ALIAS PATCH
    
    [PHASE 1 OVERHAUL] 修復：
    1. Fuzzy Column Mapping (支援各種中文欄位名稱)
    2. CRITICAL ALIAS PATCH (防止 UI 崩潰)
    3. Intelligent Fallback (缺失欄位智慧補充)
    
    Args:
        uploaded_file: Streamlit UploadedFile 對象
    
    Returns:
        清理後的 DataFrame 或 None
    """
    if uploaded_file is None:
        return None
    
    try:
        # 1. Load File
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # 2. Standardization (Remove spaces)
        df.columns = df.columns.astype(str).str.strip().str.replace(" ", "")
        
        # 3. Fuzzy Mapping Dictionary
        rename_map = {}
        
        # [CRITICAL] 優先處理「可轉債市價」避免被「市價」覆蓋
        cb_price_col = next((c for c in df.columns if "可轉債市價" in c), None)
        if cb_price_col:
            rename_map[cb_price_col] = 'price'
        
        underlying_price_col = next((c for c in df.columns if "標的股票市價" in c), None)
        if underlying_price_col:
            rename_map[underlying_price_col] = 'underlying_price'
        
        # Fuzzy mapping for other columns
        for col in df.columns:
            if col in rename_map:
                continue
            col_lower = col.lower()
            
            if "代號" in col and "標的" not in col:
                rename_map[col] = 'code'
            elif "名稱" in col or "標的債券" in col:
                rename_map[col] = 'name'
            elif cb_price_col is None and any(k in col_lower for k in ["市價", "收盤", "close", "成交"]):
                rename_map[col] = 'price'
            elif any(k in col_lower for k in ["標的", "stock_code", "標的代號"]):
                rename_map[col] = 'stock_code'
            elif "發行" in col and "日" in col:
                rename_map[col] = 'list_date'
            elif "賣回" in col or "到期" in col:
                rename_map[col] = 'put_date'
            elif any(k in col for k in ["轉換價", "轉換價格", "最新轉換價"]):
                rename_map[col] = 'conversion_price'
            elif any(k in col for k in ["已轉換比例", "轉換比例", "轉換率"]):
                rename_map[col] = 'converted_ratio'
            elif any(k in col for k in ["發行餘額", "流通餘額"]):
                rename_map[col] = 'outstanding_balance'
            elif "發行總額" in col:
                rename_map[col] = 'issue_amount'
            elif any(k in col_lower for k in ["均量", "成交量", "avg_vol", "volume"]):
                rename_map[col] = 'avg_volume'
            elif "漲跌幅" in col or "change" in col_lower:
                rename_map[col] = 'change_pct'
        
        # Apply mapping
        df.rename(columns=rename_map, inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        
        # 4. Handle Missing Critical Columns
        if 'code' not in df.columns and not df.empty:
            st.warning("⚠️ 未找到「代號」欄位，使用第一欄作為代號")
            df.rename(columns={df.columns[0]: 'code'}, inplace=True)
        
        if 'code' in df.columns:
            df['code'] = df['code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        if 'stock_code' in df.columns:
            df['stock_code'] = df['stock_code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        # ==========================================
        # [PHASE 1 CRITICAL PATCH] Create Aliases
        # ==========================================
        # 這是防止 UI 崩潰的關鍵修復
        
        # Alias 1: code -> stock_code (if stock_code missing)
        if 'code' in df.columns and 'stock_code' not in df.columns:
            df['stock_code'] = df['code']
            st.info("ℹ️ 使用「代號」作為「標的代號」")
        
        # Alias 2: price -> close (if close missing)
        if 'price' in df.columns and 'close' not in df.columns:
            df['close'] = df['price']
        
        # Alias 3: underlying_price -> underlying_close (optional)
        if 'underlying_price' in df.columns and 'underlying_close' not in df.columns:
            df['underlying_close'] = df['underlying_price']
        
        # 5. Validation
        if 'code' not in df.columns:
            st.error("❌ 檔案缺少「代號」欄位")
            return None
        
        df.dropna(subset=['code'], inplace=True)
        df = df[df['code'].str.len() > 0]
        
        # 6. Handle Optional Columns
        if 'name' not in df.columns:
            df['name'] = df['code']
        
        if 'close' not in df.columns and 'price' not in df.columns:
            st.warning("⚠️ 缺少「市價」欄位")
            df['close'] = 100.0
        
        if 'stock_code' not in df.columns:
            df['stock_code'] = df['code']
        
        if 'conversion_price' not in df.columns:
            df['conversion_price'] = 0
        
        if 'converted_ratio' not in df.columns:
            df['converted_ratio'] = 0
        
        if 'avg_volume' not in df.columns:
            vol_col = next((c for c in df.columns if '量' in c or 'volume' in c.lower()), None)
            if vol_col:
                df.rename(columns={vol_col: 'avg_volume'}, inplace=True)
            else:
                df['avg_volume'] = 100
        
        # 7. Convert numeric columns
        numeric_cols = ['close', 'price', 'conversion_price', 'underlying_price', 
                       'avg_volume', 'converted_ratio']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        st.success(f"✅ 成功載入 {len(df)} 筆數據")
        return df
        
    except Exception as e:
        st.error(f"❌ 數據載入失敗: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None


def download_stock_price(ticker: str, period: str = "1y", start_date: Optional[str] = None) -> Optional[pd.DataFrame]:
    """智慧下載股價數據 (支援台股 .TW/.TWO 自動回退)"""
    try:
        original_ticker = ticker
        
        if ticker.isdigit() and len(ticker) >= 4:
            ticker = f"{ticker}.TW"
        
        if start_date:
            df = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
        else:
            df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        
        if df.empty and original_ticker.isdigit() and len(original_ticker) >= 4:
            ticker = f"{original_ticker}.TWO"
            if start_date:
                df = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
            else:
                df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        if df.empty:
            return None
        
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        return df
    
    except Exception as e:
        st.error(f"數據下載失敗: {e}")
        return None


@st.cache_data(ttl=3600)
def get_market_benchmarks(period='1mo') -> pd.DataFrame:
    """獲取市場基準數據 (VIX, 台股, 美股, 匯率)"""
    try:
        tickers = ['^VIX', '^TWII', '^GSPC', 'USDTWD=X']
        data = yf.download(tickers, period=period, progress=False)
        
        if isinstance(data.columns, pd.MultiIndex):
            if 'Close' in data.columns.get_level_values(0):
                data = data['Close']
            else:
                data.columns = data.columns.get_level_values(0)
        
        return data
    except:
        return pd.DataFrame()


def run_fast_backtest(ticker: str, start_date: str, initial_capital: float = 1000000) -> Optional[Dict]:
    """極速回測引擎 - 策略：收盤價 > 20MA 時買入"""
    try:
        df = download_stock_price(ticker, start_date=start_date)
        
        if df is None or df.empty:
            return None
        
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['Signal'] = (df['Close'] > df['MA20']).astype(int)
        df['Position'] = df['Signal'].diff()
        df['Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Returns'] * df['Signal'].shift(1)
        
        total_return = (df['Strategy_Returns'] + 1).prod() - 1
        
        days = (df.index[-1] - df.index[0]).days
        years = days / 365.25
        cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        cumulative = (1 + df['Strategy_Returns']).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        sharpe_ratio = df['Strategy_Returns'].mean() / df['Strategy_Returns'].std() * np.sqrt(252) if df['Strategy_Returns'].std() > 0 else 0
        
        num_trades = (df['Position'] != 0).sum()
        
        winning_trades = (df[df['Position'] == 1]['Returns'] > 0).sum()
        total_trades = num_trades / 2 if num_trades > 0 else 1
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        avg_win = df[df['Strategy_Returns'] > 0]['Strategy_Returns'].mean()
        avg_loss = abs(df[df['Strategy_Returns'] < 0]['Strategy_Returns'].mean())
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        kelly = win_rate - ((1 - win_rate) / profit_factor) if profit_factor > 0 else 0
        
        return {
            'total_return': total_return,
            'cagr': cagr,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'num_trades': int(num_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'kelly': kelly
        }
    
    except Exception as e:
        st.error(f"回測失敗: {e}")
        return None