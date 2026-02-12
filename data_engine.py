# data_engine.py
# Titan SOP V100.0 - Data Engine
# 功能：數據下載、緩存、台股智慧識別、宏觀數據整合
# 提取自：app.py (V82.0)

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

# ==========================================
# [1] 核心數據下載函數
# ==========================================

def download_full_history(ticker: str, start: str = "1990-01-01") -> Optional[pd.DataFrame]:
    """
    下載完整歷史月K線數據
    [V86.2 CRITICAL FIX]: 支援台股上市 (.TW) 與上櫃 (.TWO) 自動回退
    
    Args:
        ticker: 股票代號 (會自動處理台股後綴)
        start: 起始日期
    
    Returns:
        月K DataFrame 或 None
    
    CRITICAL CONSTRAINTS:
    1. Taiwan Stock Fallback: 優先嘗試 .TW，失敗則嘗試 .TWO
    2. MultiIndex Handling: 處理 yfinance 多層索引
    3. Data Cleaning: 確保索引為 DatetimeIndex，數值正確
    """
    try:
        original_ticker = ticker
        
        # [V86.2 修正] 智慧處理台股代號 - 支援上市與上櫃
        if ticker.isdigit() and len(ticker) >= 4:
            ticker = f"{ticker}.TW"
        
        # 下載日K數據 (強制 auto_adjust 以獲取標準 OHLC，避免股息干擾)
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        
        # [V86.2 新增] 如果上市沒數據，嘗試上櫃
        if df.empty and original_ticker.isdigit() and len(original_ticker) >= 4:
            ticker = f"{original_ticker}.TWO"
            df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        
        # [關鍵修復]：yfinance 多層索引整平 (兼容台股與美股)
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.get_level_values(0)
            except: 
                pass
        
        if df.empty:
            return None
        
        # 確保索引是時間格式 (Resample 的前提)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # 轉換為月K
        df_monthly = df.resample('M').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        # [V86.2 新增] 儲存原始日K數據到 session_state 供圖表使用
        if 'daily_price_data' not in st.session_state:
            st.session_state.daily_price_data = {}
        st.session_state.daily_price_data[original_ticker] = df
        
        return df_monthly
    
    except Exception as e:
        st.error(f"數據下載失敗: {e}")
        return None


def download_stock_price(ticker: str, period: str = "1y", start_date: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    智慧下載股價數據 (支援台股 .TW/.TWO 自動回退)
    
    Args:
        ticker: 股票代號
        period: 時間範圍 (1y, 2y, 5y, max)
        start_date: 起始日期 (可選，與 period 互斥)
    
    Returns:
        DataFrame 或 None
    
    CRITICAL: 保留台股自動回退邏輯
    """
    try:
        original_ticker = ticker
        
        # 台股智慧識別：4-6 碼且開頭為數字
        if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
            ticker = f"{ticker}.TW"
        
        # 下載數據
        if start_date:
            df = yf.download(ticker, start=start_date, progress=False)
        else:
            df = yf.download(ticker, period=period, progress=False)
        
        # 台股上櫃回退邏輯
        if df.empty and re.match(r'^[0-9]', original_ticker) and 4 <= len(original_ticker) <= 6:
            ticker = f"{original_ticker}.TWO"
            if start_date:
                df = yf.download(ticker, start=start_date, progress=False)
            else:
                df = yf.download(ticker, period=period, progress=False)
        
        if df.empty:
            return None
        
        # MultiIndex 處理
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return df
    
    except Exception as e:
        st.error(f"下載 {ticker} 失敗: {e}")
        return None


# ==========================================
# [2] 回測引擎
# ==========================================

def run_fast_backtest(ticker: str, start_date: str = "2023-01-01", initial_capital: float = 1000000) -> Optional[Dict]:
    """
    [UPGRADED V78.3] 極速向量化回測引擎 (Vectorized Backtest Engine)
    策略邏輯：模擬趨勢追蹤 (Trend Following) - 當收盤價 > 20日均線時買入
    支援：台股 (TW/TWO)、美股、現金 (CASH)
    
    【Step 1 修正】台股 ETF 識別增強：
    - 使用正則表達式判斷 4-6 碼且開頭為數字的代號
    - 優先嘗試 .TW，失敗再嘗試 .TWO
    
    Returns:
        Dict 包含 cagr, sharpe_ratio, max_drawdown, win_rate, kelly, equity_curve 等
    """
    try:
        # Handle CASH asset
        if ticker.upper() in ['CASH', 'USD', 'TWD']:
            dates = yf.download('^TWII', start=start_date, progress=False).index
            if dates.empty: 
                return None
            df = pd.DataFrame(index=dates)
            df['Close'] = 1.0
            df['Strategy_Return'] = 0.0
            df['Equity'] = initial_capital
            df['Drawdown'] = 0.0
            
            return {
                "cagr": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                "win_rate": 0.0, "profit_factor": 0.0, "kelly": 0.0,
                "equity_curve": df['Equity'], "drawdown_series": df['Drawdown'],
                "latest_price": 1.0
            }

        # 1. 智慧代碼處理 (增強版：支援混合型代號如 00675L)
        original_ticker = ticker
        
        # 【Step 1 修正】使用正則判斷：長度 4-6 碼且開頭為數字
        if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
            ticker = f"{ticker}.TW"
        
        # 2. 下載數據 (優先 .TW，失敗再試 .TWO)
        df = yf.download(ticker, start=start_date, progress=False)
        if df.empty:
            # 僅對符合台股格式的代碼重試 .TWO
            if re.match(r'^[0-9]', original_ticker) and 4 <= len(original_ticker) <= 6:
                ticker_two = f"{original_ticker}.TWO"
                df = yf.download(ticker_two, start=start_date, progress=False)
            if df.empty:
                return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty or len(df) < 21: 
            return None

        # 3. 策略信號生成
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['Signal'] = 0
        df.loc[df['Close'] > df['MA20'], 'Signal'] = 1
        
        # 4. 績效計算
        df['Pct_Change'] = df['Close'].pct_change()
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Pct_Change']
        df['Equity'] = (1 + df['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        
        # 5. 凱利參數計算
        trade_days = df[df['Signal'].shift(1) == 1]
        if len(trade_days) < 10:
            win_rate, profit_factor, kelly = 0, 0, 0
        else:
            wins = trade_days[trade_days['Strategy_Return'] > 0]['Strategy_Return']
            losses = trade_days[trade_days['Strategy_Return'] < 0]['Strategy_Return']
            
            win_rate = len(wins) / len(trade_days)
            avg_win = wins.mean() if len(wins) > 0 else 0
            avg_loss = abs(losses.mean()) if len(losses) > 0 else 1
            profit_factor = avg_win / avg_loss if avg_loss != 0 else 0
            
            if profit_factor > 0:
                kelly = win_rate - ((1 - win_rate) / profit_factor)
            else:
                kelly = 0
        
        # 6. 新增專業指標
        df['Drawdown'] = (df['Equity'] / df['Equity'].cummax()) - 1
        max_drawdown = df['Drawdown'].min()

        num_years = len(df) / 252
        total_return = df['Equity'].iloc[-1] / initial_capital - 1
        cagr = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0

        risk_free_rate = 0.02
        daily_returns = df['Strategy_Return'].dropna()
        if daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() * 252 - risk_free_rate) / (daily_returns.std() * np.sqrt(252))
        else:
            sharpe_ratio = 0.0

        return {
            "cagr": cagr, 
            "sharpe_ratio": sharpe_ratio, 
            "max_drawdown": max_drawdown,
            "win_rate": win_rate, 
            "profit_factor": profit_factor, 
            "kelly": max(0, kelly),
            "equity_curve": df['Equity'], 
            "drawdown_series": df['Drawdown'],
            "latest_price": df['Close'].iloc[-1]
        }
    except Exception:
        return None


# ==========================================
# [3] 緩存數據函數
# ==========================================

@st.cache_data(ttl=600)
def get_macro_data(_macro, _df: pd.DataFrame) -> Dict:
    """
    快取宏觀風控數據 (10分鐘 TTL)
    
    Args:
        _macro: MacroRiskEngine 實例
        _df: CB DataFrame
    
    Returns:
        宏觀風險狀態字典
    """
    return _macro.check_market_status(cb_df=_df)


@st.cache_data(ttl=600)
def get_scan_result(_strat, _df: pd.DataFrame) -> pd.DataFrame:
    """
    快取策略掃描結果 (10分鐘 TTL)
    
    Args:
        _strat: TitanStrategyEngine 實例
        _df: CB DataFrame
    
    Returns:
        掃描結果 DataFrame
    """
    return _strat.scan_entire_portfolio(_df)


@st.cache_data(ttl=7200)
def run_stress_test(portfolio_text: str) -> Tuple[pd.DataFrame, Dict]:
    """
    [V82.1 FIX] 全球黑天鵝壓力測試 (含台股智慧識別)
    
    Args:
        portfolio_text: 投資組合文本 (格式: "TICKER;SHARES")
    
    Returns:
        (results_df, summary_dict)
    
    CRITICAL: 完整保留台股識別和 MultiIndex 處理邏輯
    """
    # 1. 解析輸入
    lines = [line.strip() for line in portfolio_text.split('\n') if line.strip()]
    flat_lines = []
    for line in lines:
        flat_lines.extend(item.strip() for item in line.split('|') if item.strip())

    if not flat_lines:
        return pd.DataFrame(), {}

    portfolio = []
    for item in flat_lines:
        parts = [p.strip() for p in item.split(';')]
        if len(parts) == 2 and parts[1]:
            try:
                portfolio.append({'ticker': parts[0].upper(), 'shares': float(parts[1])})
            except ValueError:
                st.warning(f"跳過無效項目: {item}")
                continue
    
    if not portfolio:
        return pd.DataFrame(), {}

    # 2. 下載基準與匯率數據
    try:
        benchmarks_data = yf.download(['^TWII', '^GSPC', 'USDTWD=X'], period="1y", progress=False)
        if benchmarks_data.empty:
            return pd.DataFrame(), {"error": "無法下載市場基準數據 (^TWII, ^GSPC)。"}
        
        # 處理 MultiIndex
        if isinstance(benchmarks_data.columns, pd.MultiIndex):
            twd_fx_rate = benchmarks_data['Close']['USDTWD=X'].iloc[-1]
        else:
            twd_fx_rate = benchmarks_data['USDTWD=X'].iloc[-1]
    except Exception as e:
        return pd.DataFrame(), {"error": f"下載市場數據失敗: {e}"}

    # 3. 處理每個資產
    results = []
    for asset in portfolio:
        original_ticker = asset['ticker']
        shares = asset['shares']
        ticker = original_ticker
        
        # [現金處理]
        if original_ticker in ['CASH', 'USD', 'TWD']:
            results.append({
                'ticker': original_ticker,
                'type': 'Cash',
                'shares': shares,
                'price': 1.0,
                'value_twd': shares,
                '損益_回檔 (-5%)': 0,
                '損益_修正 (-10%)': 0,
                '損益_技術熊市 (-20%)': 0,
                '損益_金融海嘯 (-30%)': 0,
            })
            continue
        
        # [V82.1 關鍵修復] 台股智慧識別邏輯
        is_tw_stock = False
        if re.match(r'^[0-9]', original_ticker) and 4 <= len(original_ticker) <= 6:
            ticker = f"{original_ticker}.TW"
            is_tw_stock = True

        try:
            # 下載數據
            data = yf.download(ticker, period="1mo", progress=False)
            
            # 如果 .TW 失敗，嘗試 .TWO
            if data.empty and is_tw_stock:
                ticker = f"{original_ticker}.TWO"
                data = yf.download(ticker, period="1mo", progress=False)
            
            if data.empty:
                st.warning(f"無法下載 {original_ticker} 的數據，跳過該資產。")
                continue
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            current_price = data['Close'].iloc[-1]
            
            # 判斷資產類型 (用於匯率計算)
            if '.TW' in ticker or '.TWO' in ticker or is_tw_stock:
                asset_type = 'TW_Stock'
                value_twd = current_price * shares
            else:
                asset_type = 'US_Asset'
                value_twd = current_price * shares * twd_fx_rate
            
            # 計算壓力損益
            stress_scenarios = {
                '回檔 (-5%)': -0.05,
                '修正 (-10%)': -0.10,
                '技術熊市 (-20%)': -0.20,
                '金融海嘯 (-30%)': -0.30,
            }
            
            pnl = {}
            for scenario_name, shock in stress_scenarios.items():
                pnl[f'損益_{scenario_name}'] = value_twd * shock
            
            results.append({
                'ticker': original_ticker,
                'type': asset_type,
                'shares': shares,
                'price': current_price,
                'value_twd': value_twd,
                **pnl
            })
        except Exception as e:
            st.warning(f"處理 {original_ticker} 時發生錯誤: {e}")
            continue
    
    if not results:
        return pd.DataFrame(), {"error": "無有效資產數據。"}
    
    results_df = pd.DataFrame(results)
    total_value = results_df['value_twd'].sum()
    
    return results_df, {'total_value': total_value}


@st.cache_data(ttl=7200)
def run_ma_strategy_backtest(ticker: str, strategy_name: str, start_date: str = "2015-01-01", 
                               initial_capital: float = 1000000) -> Optional[Dict]:
    """
    【Tab 4.3 核心】執行 15 種均線策略回測
    
    策略列表：
    1-5: 價格穿越單一均線 (20, 43, 60, 87, 284MA)
    6: 非對稱進出場 (P>20進 / P<60出)
    7-13: 均線交叉策略 (20/60, 20/87, 20/284, 43/87, 43/284, 60/87, 60/284)
    14-15: 三均線系統 (20/60/87, 43/87/284)
    
    Args:
        ticker: 股票代號
        strategy_name: 策略名稱
        start_date: 起始日期
        initial_capital: 初始資金
    
    Returns:
        績效指標字典或 None
    
    CRITICAL: 保留完整的台股回退邏輯
    """
    try:
        # 台股代碼處理
        original_ticker = ticker
        if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
            ticker = f"{ticker}.TW"
        
        # 下載數據
        df = yf.download(ticker, start=start_date, progress=False)
        
        # 台股上櫃回退
        if df.empty and re.match(r'^[0-9]', original_ticker) and 4 <= len(original_ticker) <= 6:
            ticker = f"{original_ticker}.TWO"
            df = yf.download(ticker, start=start_date, progress=False)
        
        if df.empty:
            return None
        
        # MultiIndex 處理
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        if len(df) < 300:  # 至少需要 300 個交易日
            return None
        
        # 計算各種均線
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA43'] = df['Close'].rolling(window=43).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        df['MA87'] = df['Close'].rolling(window=87).mean()
        df['MA284'] = df['Close'].rolling(window=284).mean()
        
        # 初始化信號
        df['Signal'] = 0
        
        # 根據策略生成信號
        if strategy_name == "價格 > 20MA":
            df.loc[df['Close'] > df['MA20'], 'Signal'] = 1
        elif strategy_name == "價格 > 43MA":
            df.loc[df['Close'] > df['MA43'], 'Signal'] = 1
        elif strategy_name == "價格 > 60MA":
            df.loc[df['Close'] > df['MA60'], 'Signal'] = 1
        elif strategy_name == "價格 > 87MA":
            df.loc[df['Close'] > df['MA87'], 'Signal'] = 1
        elif strategy_name == "價格 > 284MA":
            df.loc[df['Close'] > df['MA284'], 'Signal'] = 1
        elif strategy_name == "非對稱 (P>20進/P<60出)":
            # 進場：價格 > 20MA
            # 出場：價格 < 60MA
            position = 0
            signals = []
            for i in range(len(df)):
                if position == 0 and df['Close'].iloc[i] > df['MA20'].iloc[i]:
                    position = 1
                elif position == 1 and df['Close'].iloc[i] < df['MA60'].iloc[i]:
                    position = 0
                signals.append(position)
            df['Signal'] = signals
        elif strategy_name == "20MA 金叉 60MA":
            df.loc[df['MA20'] > df['MA60'], 'Signal'] = 1
        elif strategy_name == "20MA 金叉 87MA":
            df.loc[df['MA20'] > df['MA87'], 'Signal'] = 1
        elif strategy_name == "20MA 金叉 284MA":
            df.loc[df['MA20'] > df['MA284'], 'Signal'] = 1
        elif strategy_name == "43MA 金叉 87MA":
            df.loc[df['MA43'] > df['MA87'], 'Signal'] = 1
        elif strategy_name == "43MA 金叉 284MA":
            df.loc[df['MA43'] > df['MA284'], 'Signal'] = 1
        elif strategy_name == "60MA 金叉 87MA":
            df.loc[df['MA60'] > df['MA87'], 'Signal'] = 1
        elif strategy_name == "60MA 金叉 284MA":
            df.loc[df['MA60'] > df['MA284'], 'Signal'] = 1
        elif strategy_name == "三線多頭 (20>60>87)":
            df.loc[(df['MA20'] > df['MA60']) & (df['MA60'] > df['MA87']), 'Signal'] = 1
        elif strategy_name == "三線多頭 (43>87>284)":
            df.loc[(df['MA43'] > df['MA87']) & (df['MA87'] > df['MA284']), 'Signal'] = 1
        else:
            return None
        
        # 計算績效
        df['Pct_Change'] = df['Close'].pct_change()
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Pct_Change']
        df['Equity'] = (1 + df['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        
        # 計算指標
        df['Drawdown'] = (df['Equity'] / df['Equity'].cummax()) - 1
        max_drawdown = df['Drawdown'].min()
        
        num_years = len(df) / 252
        total_return = df['Equity'].iloc[-1] / initial_capital - 1
        cagr = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0
        
        daily_returns = df['Strategy_Return'].dropna()
        if daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() * 252 - 0.02) / (daily_returns.std() * np.sqrt(252))
        else:
            sharpe_ratio = 0.0
        
        # 計算交易次數和勝率
        trades = df[df['Signal'].diff() != 0]
        num_trades = len(trades)
        
        return {
            "strategy_name": strategy_name,
            "cagr": cagr,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "total_return": total_return,
            "num_trades": num_trades,
            "equity_curve": df['Equity'],
            "drawdown_series": df['Drawdown']
        }
    
    except Exception as e:
        st.error(f"回測失敗: {e}")
        return None


# ==========================================
# [4] 宏觀指標下載
# ==========================================

def get_market_benchmarks(period: str = "1y") -> Optional[pd.DataFrame]:
    """
    下載市場基準指標 (台股加權、美股 S&P500、VIX、匯率)
    
    Args:
        period: 時間範圍
    
    Returns:
        DataFrame 或 None
    """
    try:
        tickers = ['^TWII', '^GSPC', '^VIX', 'USDTWD=X']
        data = yf.download(tickers, period=period, progress=False)
        
        if data.empty:
            return None
        
        # MultiIndex 處理
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
        
        return data
    
    except Exception as e:
        st.error(f"下載市場基準失敗: {e}")
        return None


# ==========================================
# [5] 輔助函數
# ==========================================

def validate_ticker(ticker: str) -> Tuple[bool, str]:
    """
    驗證股票代號格式
    
    Args:
        ticker: 股票代號
    
    Returns:
        (is_valid, error_message)
    """
    if not ticker or ticker.strip() == "":
        return False, "代號不能為空"
    
    ticker = ticker.strip().upper()
    
    # 台股：4-6 位數字
    if re.match(r'^[0-9]{4,6}$', ticker):
        return True, ""
    
    # 美股：1-5 個字母
    if re.match(r'^[A-Z]{1,5}$', ticker):
        return True, ""
    
    # 已包含後綴的格式
    if re.match(r'^[0-9]{4,6}\.(TW|TWO)$', ticker):
        return True, ""
    
    return False, "代號格式不正確 (台股: 4-6位數字, 美股: 1-5個字母)"


def clean_numeric_column(series: pd.Series) -> pd.Series:
    """
    清理數值欄位（移除逗號、百分號等）
    
    Args:
        series: Pandas Series
    
    Returns:
        清理後的 Series
    """
    if series.dtype == 'object':
        # 移除逗號、百分號
        series = series.astype(str).str.replace(',', '').str.replace('%', '').str.replace('$', '')
        # 轉換為數值
        series = pd.to_numeric(series, errors='coerce')
    
    return series


def get_time_slice(df: pd.DataFrame, months: int) -> pd.DataFrame:
    """
    精準切割指定月數的月K數據
    
    Args:
        df: 月K DataFrame
        months: 回溯月數
    
    Returns:
        切割後的 DataFrame
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    return df.tail(months)


# ==========================================
# [6] 數據完整性檢查
# ==========================================

def check_data_completeness(df: pd.DataFrame) -> Dict[str, any]:
    """
    檢查 DataFrame 的數據完整性
    
    Args:
        df: DataFrame
    
    Returns:
        完整性報告字典
    """
    report = {
        "total_rows": len(df),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict()
    }
    
    return report


# ==========================================
# [7] CB 數據載入與處理
# ==========================================

def load_cb_data_from_upload(uploaded_file) -> Optional[pd.DataFrame]:
    """
    從上傳的檔案載入並清理 CB 數據
    
    Args:
        uploaded_file: Streamlit UploadedFile 對象
    
    Returns:
        清理後的 DataFrame 或 None
    
    CRITICAL: 保留原始的欄位映射邏輯
    """
    try:
        # 讀取檔案
        if uploaded_file.name.endswith('.xlsx'):
            df_raw = pd.read_excel(uploaded_file)
        else:
            df_raw = pd.read_csv(uploaded_file)
        
        df = df_raw.copy()
        df.columns = [c.strip().replace(" ", "") for c in df.columns]

        # 智慧欄位映射
        rename_map = {}
        
        # [V81.1 CRITICAL FIX] 優先使用「可轉債市價」作為 close
        cb_price_col = next((c for c in df.columns if "可轉債市價" in c), None)
        if cb_price_col: 
            rename_map[cb_price_col] = 'close'
        
        underlying_price_col = next((c for c in df.columns if "標的股票市價" in c), None)
        if underlying_price_col: 
            rename_map[underlying_price_col] = 'underlying_price'
        
        for col in df.columns:
            if col in rename_map: 
                continue
            col_lower = col.lower()
            
            if "代號" in col and "標的" not in col: 
                rename_map[col] = 'code'
            elif "名稱" in col or "標的債券" in col: 
                rename_map[col] = 'name'
            elif cb_price_col is None and any(k in col_lower for k in ["市價", "收盤", "close", "成交"]): 
                rename_map[col] = 'close'
            elif any(k in col_lower for k in ["標的", "stock_code"]): 
                rename_map[col] = 'stock_code'
            elif "發行" in col: 
                rename_map[col] = 'list_date'
            elif "賣回" in col: 
                rename_map[col] = 'put_date'
            elif any(k in col for k in ["轉換價", "轉換價格", "最新轉換價"]): 
                rename_map[col] = 'conversion_price'
            elif any(k in col for k in ["已轉換比例", "轉換比例", "轉換率"]): 
                rename_map[col] = 'converted_ratio'
            elif any(k in col for k in ["發行餘額", "流通餘額"]): 
                rename_map[col] = 'outstanding_balance'
            elif "發行總額" in col: 
                rename_map[col] = 'issue_amount'
            elif any(k in col_lower for k in ["均量", "成交量", "avg_vol"]): 
                rename_map[col] = 'avg_volume'

        df.rename(columns=rename_map, inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        
        # 檢查必要欄位
        required_cols = ['code', 'name', 'stock_code', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ 檔案缺少必要欄位！請確認包含: {', '.join(missing_cols)}")
            return None
        
        # 清理數據
        df['code'] = df['code'].astype(str).str.extract(r'(\d+)')
        df['stock_code'] = df['stock_code'].astype(str).str.extract(r'(\d+)')
        df.dropna(subset=['code', 'stock_code'], inplace=True)
        
        # 處理可選欄位
        if 'conversion_price' not in df.columns:
            st.warning("⚠️ 缺少「轉換價」欄位，溢價率將無法計算。")
            df['conversion_price'] = 0
        
        if 'converted_ratio' not in df.columns:
            if 'outstanding_balance' in df.columns and 'issue_amount' in df.columns:
                st.info("ℹ️ 未提供「已轉換比例」，系統將嘗試從發行餘額與總額計算。")
            else:
                st.warning("⚠️ 缺少「已轉換比例」相關欄位，籌碼鬆動分析將無法執行。")
                df['converted_ratio'] = 0
        
        if 'avg_volume' not in df.columns:
            st.warning("⚠️ 缺少「均量」欄位，流動性風險分析可能不準確。")
            vol_col = next((c for c in df.columns if '量' in c or 'volume' in c), None)
            if vol_col: 
                df.rename(columns={vol_col: 'avg_volume'}, inplace=True)
            else: 
                df['avg_volume'] = 100
        
        return df
    
    except Exception as e:
        st.error(f"檔案讀取或格式清洗失敗: {e}")
        return None
