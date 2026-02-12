# core_logic.py
# Titan SOP V100.0 - Core Business Logic & Math Engine
# 功能：7D 幾何引擎、22 階信評系統、AI 參謀本部、回測引擎
# 提取自：app.py (V82.0)
# 狀態：ZERO SIMPLIFICATION - 100% 原始邏輯保留

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import linregress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai

# ==========================================
# [1] 輔助函數：時間切片
# ==========================================

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


def download_full_history(ticker: str, start: str = "1990-01-01") -> Optional[pd.DataFrame]:
    """
    下載完整歷史月K線數據
    [V86.2 CRITICAL FIX]: 支援台股上市 (.TW) 與上櫃 (.TWO) 自動回退
    
    Args:
        ticker: 股票代號 (會自動處理台股後綴)
        start: 起始日期
    
    Returns:
        月K DataFrame 或 None
    
    CRITICAL: 完整保留台股回退邏輯
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


# ==========================================
# [2] 7D 幾何引擎 (ZERO SIMPLIFICATION)
# ==========================================

def calculate_geometry_metrics(df: pd.DataFrame, months: int) -> Dict[str, float]:
    """
    計算單一時間窗口的幾何指標
    
    Args:
        df: 完整月K DataFrame
        months: 時間窗口 (月)
    
    Returns:
        dict: {'angle': float, 'r2': float, 'slope': float}
    
    CRITICAL: 完整保留所有數學公式
    - Slope, Intercept, R-squared
    - Angle calculation (arctan of slope * 100)
    """
    if df is None or df.empty:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    
    # 切割數據
    slice_df = get_time_slice(df, months)
    
    if len(slice_df) < 3:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    
    # 對數價格回歸
    log_prices = np.log(slice_df['Close'].values)
    x = np.arange(len(log_prices))
    
    slope, intercept, r_value, p_value, std_err = linregress(x, log_prices)
    
    # 將斜率轉換為角度 (-90 到 90 度)
    # 標準化: 假設 slope=0.01 對應 45度
    angle = np.arctan(slope * 100) * (180 / np.pi)
    angle = np.clip(angle, -90, 90)
    
    r2 = r_value ** 2
    
    return {
        'angle': round(angle, 2),
        'r2': round(r2, 4),
        'slope': round(slope, 6)
    }


def compute_7d_geometry(ticker: str) -> Optional[Dict]:
    """
    [V90.2 核心] 計算 7 維度完整幾何掃描
    使用 yf.download(period='max') 抓取全歷史數據
    
    Returns:
        dict: {
            '35Y': {'angle': float, 'r2': float, 'slope': float},
            '10Y': {...},
            '5Y': {...},
            '3Y': {...},
            '1Y': {...},
            '6M': {...},
            '3M': {...},
            'acceleration': float,
            'phoenix_signal': bool
        }
    
    CRITICAL: 完整保留所有邏輯
    - 7 個時間窗口計算
    - Acceleration = 3M Angle - 1Y Angle
    - Phoenix Signal = (10Y Angle < 0) AND (6M Angle > 25)
    """
    df = download_full_history(ticker)
    
    if df is None:
        return None
    
    # 定義 7 個時間窗口 (月)
    periods = {
        '35Y': 420,
        '10Y': 120,
        '5Y': 60,
        '3Y': 36,
        '1Y': 12,
        '6M': 6,
        '3M': 3
    }
    
    results = {}
    
    for label, months in periods.items():
        results[label] = calculate_geometry_metrics(df, months)
    
    # 計算加速度
    acceleration = results['3M']['angle'] - results['1Y']['angle']
    results['acceleration'] = round(acceleration, 2)
    
    # Phoenix 信號
    phoenix = (results['10Y']['angle'] < 0) and (results['6M']['angle'] > 25)
    results['phoenix_signal'] = phoenix
    
    return results


# ==========================================
# [3] 22 階泰坦信評引擎 (ZERO SIMPLIFICATION)
# ==========================================

def titan_rating_system(geo: Dict) -> Tuple[str, str, str, str]:
    """
    22 階信評邏輯樹
    
    Args:
        geo: 7D 幾何數據字典
    
    Returns:
        tuple: (rating_level, rating_name, description, color)
    
    CRITICAL: 所有 22 個評級條件完整保留
    """
    if geo is None:
        return ("N/A", "無數據", "數據不足", "#808080")
    
    # 提取關鍵指標
    angle_35y = geo['35Y']['angle']
    angle_10y = geo['10Y']['angle']
    angle_5y = geo['5Y']['angle']
    angle_1y = geo['1Y']['angle']
    angle_6m = geo['6M']['angle']
    angle_3m = geo['3M']['angle']
    
    r2_1y = geo['1Y']['r2']
    r2_3m = geo['3M']['r2']
    
    acceleration = geo['acceleration']
    phoenix = geo['phoenix_signal']
    
    # ===== SSS 級 =====
    if all([angle_35y > 45, angle_10y > 45, angle_1y > 45, angle_3m > 45]):
        return ("SSS", "Titan (泰坦)", "全週期超過45度，神級標的", "#FFD700")
    
    # ===== AAA 級 =====
    if angle_1y > 40 and angle_6m > 45 and angle_3m > 50 and acceleration > 20:
        return ("AAA", "Dominator (統治者)", "短期加速向上，完美趨勢", "#FF4500")
    
    # ===== Phoenix 級 (特殊) =====
    if phoenix and angle_3m > 30:
        return ("Phoenix", "Phoenix (浴火重生)", "長空短多，逆轉信號", "#FF6347")
    
    # ===== Launchpad 級 (特殊) =====
    if r2_1y > 0.95 and 20 < angle_1y < 40 and acceleration > 0:
        return ("Launchpad", "Launchpad (發射台)", "線性度極高，蓄勢待發", "#32CD32")
    
    # ===== AA+ 級 =====
    if angle_1y > 35 and angle_3m > 40 and r2_3m > 0.85:
        return ("AA+", "Elite (精英)", "一年期強勢上攻", "#FFA500")
    
    # ===== AA 級 =====
    if angle_1y > 30 and angle_6m > 35:
        return ("AA", "Strong Bull (強多)", "中短期穩定上升", "#FFD700")
    
    # ===== AA- 級 =====
    if angle_1y > 25 and angle_3m > 30:
        return ("AA-", "Steady Bull (穩健多)", "趨勢健康向上", "#ADFF2F")
    
    # ===== A+ 級 =====
    if angle_6m > 20 and angle_3m > 25:
        return ("A+", "Moderate Bull (溫和多)", "短期表現良好", "#7FFF00")
    
    # ===== A 級 =====
    if angle_3m > 15:
        return ("A", "Weak Bull (弱多)", "短期微幅上揚", "#98FB98")
    
    # ===== BBB+ 級 (中性偏多) =====
    if -5 < angle_3m < 15 and angle_1y > 0:
        return ("BBB+", "Neutral+ (中性偏多)", "盤整偏多", "#F0E68C")
    
    # ===== BBB 級 (中性) =====
    if -10 < angle_3m < 10 and -10 < angle_1y < 10:
        return ("BBB", "Neutral (中性)", "橫盤震蕩", "#D3D3D3")
    
    # ===== BBB- 級 (中性偏空) =====
    if -15 < angle_3m < 5 and angle_1y < 0:
        return ("BBB-", "Neutral- (中性偏空)", "盤整偏弱", "#DDA0DD")
    
    # ===== Divergence 級 (特殊警告) =====
    if angle_1y > 20 and angle_3m < -10:
        return ("Divergence", "Divergence (背離)", "價格創高但動能衰竭", "#FF1493")
    
    # ===== BB+ 級 =====
    if -25 < angle_3m < -15 and angle_1y > -10:
        return ("BB+", "Weak Bear (弱空)", "短期下跌", "#FFA07A")
    
    # ===== BB 級 =====
    if -35 < angle_3m < -25:
        return ("BB", "Moderate Bear (中等空)", "下跌趨勢明確", "#FF6347")
    
    # ===== BB- 級 =====
    if -45 < angle_3m < -35:
        return ("BB-", "Strong Bear (強空)", "跌勢凌厲", "#DC143C")
    
    # ===== B+ 級 =====
    if angle_3m < -45 and angle_1y < -30:
        return ("B+", "Severe Bear (重度空)", "崩跌模式", "#8B0000")
    
    # ===== B 級 =====
    if angle_10y < -30 and angle_3m < -40:
        return ("B", "Depression (蕭條)", "長期熊市", "#800000")
    
    # ===== C 級 =====
    if angle_35y < -20 and angle_10y < -35:
        return ("C", "Structural Decline (結構衰退)", "世代熊市", "#4B0082")
    
    # ===== D 級 =====
    if angle_3m < -60:
        return ("D", "Collapse (崩盤)", "極度危險", "#000000")
    
    # ===== 觸底反彈 級 (特殊) =====
    if angle_10y < -20 and angle_3m > 15 and acceleration > 30:
        return ("Reversal", "Reversal (觸底反彈)", "熊市中的V型反轉", "#00CED1")
    
    # ===== 預設 =====
    return ("N/A", "Unknown (未分類)", "無法歸類", "#808080")


# ==========================================
# [4] 情報局 (TitanIntelAgency) - ZERO SIMPLIFICATION
# ==========================================

class TitanIntelAgency:
    """
    [V90.2 PROJECT VALKYRIE] 自動情報抓取引擎
    功能：抓取 Yahoo Finance 基本面數據與最新新聞
    
    CRITICAL: 完整保留所有邏輯
    """
    def __init__(self):
        self.ticker_obj = None
    
    def fetch_full_report(self, ticker: str) -> str:
        """
        抓取完整情報報告
        
        Args:
            ticker: 股票代號 (支援台股與美股)
        
        Returns:
            str: Markdown 格式的完整報告
        """
        try:
            # 處理台股代號
            original_ticker = ticker
            if ticker.isdigit() and len(ticker) >= 4:
                ticker = f"{ticker}.TW"
            
            # 初始化 Ticker
            self.ticker_obj = yf.Ticker(ticker)
            
            # 如果上市沒數據，嘗試上櫃
            try:
                test_info = self.ticker_obj.info
                if not test_info or 'symbol' not in test_info:
                    if original_ticker.isdigit() and len(original_ticker) >= 4:
                        ticker = f"{original_ticker}.TWO"
                        self.ticker_obj = yf.Ticker(ticker)
            except:
                if original_ticker.isdigit() and len(original_ticker) >= 4:
                    ticker = f"{original_ticker}.TWO"
                    self.ticker_obj = yf.Ticker(ticker)
            
            # 抓取基本面數據
            fundamentals = self._fetch_fundamentals()
            
            # 抓取新聞
            news = self._fetch_news()
            
            # 組合報告
            report = self._generate_report(ticker, fundamentals, news)
            
            return report
        
        except Exception as e:
            return f"❌ **情報抓取失敗**\n\n錯誤訊息: {str(e)}\n\n請確認股票代號是否正確，或手動貼上情報。"
    
    def _fetch_fundamentals(self) -> Dict:
        """
        抓取基本面數據
        
        Returns:
            dict: 基本面指標
        """
        try:
            info = self.ticker_obj.info
            
            fundamentals = {
                '市值': info.get('marketCap', 'N/A'),
                '現價': info.get('currentPrice', 'N/A'),
                'Forward PE': info.get('forwardPE', 'N/A'),
                'PEG Ratio': info.get('pegRatio', 'N/A'),
                '營收成長 (YoY)': info.get('revenueGrowth', 'N/A'),
                '毛利率': info.get('grossMargins', 'N/A'),
                '營業利益率': info.get('operatingMargins', 'N/A'),
                'ROE': info.get('returnOnEquity', 'N/A'),
                '負債比': info.get('debtToEquity', 'N/A'),
                '自由現金流': info.get('freeCashflow', 'N/A'),
                '機構目標價': info.get('targetMeanPrice', 'N/A'),
                '52週高點': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52週低點': info.get('fiftyTwoWeekLow', 'N/A'),
                '產業': info.get('industry', 'N/A'),
                '公司簡介': info.get('longBusinessSummary', 'N/A')
            }
            
            return fundamentals
        
        except Exception as e:
            return {'錯誤': str(e)}
    
    def _fetch_news(self) -> List[Dict]:
        """
        抓取最新新聞 (最多 5 則)
        
        Returns:
            list: 新聞列表
        """
        try:
            news_list = self.ticker_obj.news
            
            if not news_list:
                return []
            
            # 取前 5 則
            top_news = news_list[:5]
            
            formatted_news = []
            for item in top_news:
                title = item.get('title', 'N/A')
                publisher = item.get('publisher', 'N/A')
                link = item.get('link', '#')
                
                # 轉換時間戳
                timestamp = item.get('providerPublishTime', 0)
                if timestamp:
                    publish_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                else:
                    publish_time = 'N/A'
                
                formatted_news.append({
                    'title': title,
                    'publisher': publisher,
                    'time': publish_time,
                    'link': link
                })
            
            return formatted_news
        
        except Exception as e:
            return []
    
    def _generate_report(self, ticker: str, fundamentals: Dict, news: List[Dict]) -> str:
        """
        生成 Markdown 格式報告
        
        Args:
            ticker: 股票代號
            fundamentals: 基本面數據
            news: 新聞列表
        
        Returns:
            str: Markdown 報告
        """
        report = f"""# 🤖 瓦爾基里情報報告 (Valkyrie Intel Report)
**標的代號**: {ticker}
**抓取時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 基本面數據 (Fundamentals)

"""
        
        # 基本面表格
        if '錯誤' in fundamentals:
            report += f"❌ 基本面數據抓取失敗: {fundamentals['錯誤']}\n\n"
        else:
            # 市值與估值
            market_cap = fundamentals.get('市值', 'N/A')
            if isinstance(market_cap, (int, float)):
                market_cap_str = f"${market_cap / 1e9:.2f}B" if market_cap > 1e9 else f"${market_cap / 1e6:.2f}M"
            else:
                market_cap_str = str(market_cap)
            
            report += f"**市值**: {market_cap_str}\n"
            report += f"**現價**: ${fundamentals.get('現價', 'N/A')}\n"
            report += f"**Forward PE**: {fundamentals.get('Forward PE', 'N/A')}\n"
            report += f"**PEG Ratio**: {fundamentals.get('PEG Ratio', 'N/A')}\n"
            report += f"**機構目標價**: ${fundamentals.get('機構目標價', 'N/A')}\n\n"
            
            # 成長性與獲利能力
            revenue_growth = fundamentals.get('營收成長 (YoY)', 'N/A')
            if isinstance(revenue_growth, (int, float)):
                revenue_growth_str = f"{revenue_growth * 100:.2f}%"
            else:
                revenue_growth_str = str(revenue_growth)
            
            gross_margin = fundamentals.get('毛利率', 'N/A')
            if isinstance(gross_margin, (int, float)):
                gross_margin_str = f"{gross_margin * 100:.2f}%"
            else:
                gross_margin_str = str(gross_margin)
            
            operating_margin = fundamentals.get('營業利益率', 'N/A')
            if isinstance(operating_margin, (int, float)):
                operating_margin_str = f"{operating_margin * 100:.2f}%"
            else:
                operating_margin_str = str(operating_margin)
            
            roe = fundamentals.get('ROE', 'N/A')
            if isinstance(roe, (int, float)):
                roe_str = f"{roe * 100:.2f}%"
            else:
                roe_str = str(roe)
            
            report += f"**營收成長 (YoY)**: {revenue_growth_str}\n"
            report += f"**毛利率**: {gross_margin_str}\n"
            report += f"**營業利益率**: {operating_margin_str}\n"
            report += f"**ROE**: {roe_str}\n\n"
            
            # 財務健康度
            debt_to_equity = fundamentals.get('負債比', 'N/A')
            free_cashflow = fundamentals.get('自由現金流', 'N/A')
            if isinstance(free_cashflow, (int, float)):
                fcf_str = f"${free_cashflow / 1e9:.2f}B" if free_cashflow > 1e9 else f"${free_cashflow / 1e6:.2f}M"
            else:
                fcf_str = str(free_cashflow)
            
            report += f"**負債比**: {debt_to_equity}\n"
            report += f"**自由現金流**: {fcf_str}\n\n"
            
            # 價格區間
            report += f"**52週高點**: ${fundamentals.get('52週高點', 'N/A')}\n"
            report += f"**52週低點**: ${fundamentals.get('52週低點', 'N/A')}\n\n"
            
            # 產業與簡介
            report += f"**產業**: {fundamentals.get('產業', 'N/A')}\n\n"
            
            business_summary = fundamentals.get('公司簡介', 'N/A')
            if business_summary != 'N/A' and len(business_summary) > 200:
                business_summary = business_summary[:200] + "..."
            report += f"**公司簡介**: {business_summary}\n\n"
        
        report += "---\n\n"
        
        # 新聞區塊
        report += "## 📰 最新新聞 (Latest News)\n\n"
        
        if not news:
            report += "⚠️ 未抓取到新聞，或該標的新聞較少。\n\n"
        else:
            for idx, item in enumerate(news, 1):
                report += f"**{idx}. {item['title']}**\n"
                report += f"   - 來源: {item['publisher']}\n"
                report += f"   - 時間: {item['time']}\n"
                report += f"   - [閱讀全文]({item['link']})\n\n"
        
        report += "---\n\n"
        report += "💡 **使用提示**: 以上數據由 Yahoo Finance 自動抓取，請搭配人工判斷使用。\n"
        
        return report


# ==========================================
# [5] AI 參謀本部 (TitanAgentCouncil) - COMPLETE PROMPT
# ==========================================

class TitanAgentCouncil:
    """
    V90.2 升級版: 五權分立角鬥士系統 + 20 條第一性原則
    具備: 幾何死神(Quant), 內部人(Insider), 大賣空(Burry), 創世紀(Visionary), 上帝裁決(Arbiter)
    
    CRITICAL: 完整保留所有 prompt 文字，無任何省略
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = None
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # V90.2: 優先使用最新的 Gemini 2.0 Flash
                try:
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                except:
                    # 回退到 1.5 Flash
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                st.warning(f"AI 模型初始化失敗: {e}")

    def generate_battle_prompt(self, ticker: str, price: float, geo_data: Dict, 
                               rating_info: Tuple, intel_text: str = "", 
                               commander_note: str = "", 
                               selected_principles: Optional[List[str]] = None) -> str:
        """
        [V90.2 核心] 生成史詩級辯論提示詞 (Anti-Laziness Protocol Enforced)
        
        Args:
            ticker: 股票代號
            price: 當前價格
            geo_data: 7D 幾何數據
            rating_info: (level, name, desc, color)
            intel_text: 法說會/財報情報 (含瓦爾基里自動抓取的內容)
            commander_note: 統帥第一性原則筆記
            selected_principles: 選擇的第一性原則清單
        
        Returns:
            str: 完整的 Ragnarök War Room prompt
        
        CRITICAL: 完整保留所有 prompt 文字，包括所有角色定義和輸出格式
        """
        level, name, desc, color = rating_info
        
        # 幾何數據格式化
        geo_str = f"""
1. 超長期視角 (35 年): 角度 {geo_data['35Y']['angle']}°, R² {geo_data['35Y']['r2']}, 斜率 {geo_data['35Y']['slope']}
2. 長期視角 (10 年): 角度 {geo_data['10Y']['angle']}°, R² {geo_data['10Y']['r2']}, 斜率 {geo_data['10Y']['slope']}
3. 中長期視角 (5 年): 角度 {geo_data['5Y']['angle']}°, R² {geo_data['5Y']['r2']}, 斜率 {geo_data['5Y']['slope']}
4. 中期視角 (3 年): 角度 {geo_data['3Y']['angle']}°, R² {geo_data['3Y']['r2']}, 斜率 {geo_data['3Y']['slope']}
5. 短中期視角 (1 年): 角度 {geo_data['1Y']['angle']}°, R² {geo_data['1Y']['r2']}, 斜率 {geo_data['1Y']['slope']}
6. 短期視角 (6 個月): 角度 {geo_data['6M']['angle']}°, R² {geo_data['6M']['r2']}, 斜率 {geo_data['6M']['slope']}
7. 極短期視角 (3 個月): 角度 {geo_data['3M']['angle']}°, R² {geo_data['3M']['r2']}, 斜率 {geo_data['3M']['slope']}

加速度: {geo_data['acceleration']}° (3M角度 - 1Y角度)
Phoenix 信號: {'🔥 觸發' if geo_data['phoenix_signal'] else '❄️ 未觸發'}
"""
        
        # 第一性原則格式化
        principles_str = ""
        if selected_principles:
            principles_str = "\n## 🎯 統帥指定第一性原則 (必須回答)\n"
            for idx, principle in enumerate(selected_principles, 1):
                principles_str += f"{idx}. {principle}\n"
        
        prompt = f"""
# 🏛️ Titan Protocol V90.2: 諸神黃昏戰情室 (The Ragnarök War Room)
# 目標代號: {ticker} | 現價: ${price:.2f}

你現在是 Titan 基金的「最高參謀本部」。我們正在決定是否要將此標的納入「2033 百倍股」的核心持倉。
這不是普通的分析，這是一場 **生死辯論**。

## 📊 戰場地形 (幾何數據)
{geo_str}

## 🏆 泰坦信評 (Titan Rating)
評級等級：{level}
評級名稱：{name}
評級描述：{desc}
(這是基於 22 階信評系統的初步判定，各位角鬥士可以挑戰或支持此評級)

## 🕵️ 實彈情報 (Insider Intel)
(以下資料來自法說會/財報/新聞/瓦爾基里自動抓取，必須被引用作為攻擊或防禦的武器)
{intel_text if intel_text else "無外部情報注入，請基於幾何數據與你的知識庫進行推演。"}
{principles_str}

## ✍️ 統帥第一性原則 (Commander's Override)
(這是最高指令，Arbiter 必須以此為最終裁決的邏輯基石)
{commander_note if commander_note else "無特殊指令，請依據最大利益原則裁決。"}

---

## ⚔️ 五大角鬥士戰鬥程序 (Battle Protocol)

請扮演以下五位角色，進行一場**史詩級的對話 (Epic Debate)**。

**【絕對規則 (Anti-Laziness Protocol)】**
1. **字數強制**：每一位角色的發言 **不得少於 800 字** (Arbiter 需 1000 字以上)。
2. **禁止客套**：這是一場你死我活的辯論。Burry 必須尖酸刻薄，Visionary 必須狂熱，Insider 必須狡猾。
3. **第一性原則**：所有論點必須回歸物理極限、現金流本質與技術邊界，禁止使用模糊的金融術語。
4. **數據引用**：每個論點必須明確引用上方的幾何數據或實彈情報。
5. **互動續寫**：每位角色發言時，必須引用前一位角色的觀點並進行反駁或補充，確保辯論連續性。

### 角色定義：

**1. 【幾何死神】(The Quant - 冷血數學家)**
* **性格**：冷血、無情、只相信數學。
* **任務**：根據上方的幾何數據 (35Y, 10Y, 3M 斜率與加速度)，判斷股價是否過熱？R² 是否穩定？
* **口頭禪**：「數據不會說謊，人類才會。」
* **論點要求**：至少 800 字，必須引用具體角度與 R² 數值。必須分析 7 個時間窗口的趨勢一致性。

**2. 【內部操盤手】(The Insider - CEO/CFO 化身)**
* **性格**：防禦性強、報喜不報憂、擅長畫大餅。
* **任務**：利用「實彈情報」中的數據，護航公司的成長故事。解釋為何現在是買點？
* **對抗**：當 Burry 攻擊估值時，你要拿出營收成長率反擊。並且必須引用 Quant 的幾何數據來支持你的觀點。
* **論點要求**：至少 800 字，若無實彈情報則從行業趨勢切入。必須引用瓦爾基里提供的基本面數據 (如毛利率、ROE)。

**3. 【大賣空獵人】(The Big Short - Michael Burry 化身)**
* **性格**：極度悲觀、被害妄想、尋找崩盤的前兆。
* **任務**：攻擊「內部人」的謊言。找出估值泡沫、毛利下滑、宏觀衰退的訊號。你必須引用 Insider 的論點並逐一駁斥。
* **第一性原則**：均值回歸是宇宙鐵律。所有拋物線最終都會墜毀。
* **論點要求**：至少 800 字，必須質疑信評等級的合理性。必須指出瓦爾基里數據中的風險點 (如負債比過高)。

**4. 【創世紀先知】(The Visionary - Cathie Wood/Elon Musk 化身)**
* **性格**：狂熱、指數級思維、無視短期虧損。
* **任務**：使用「萊特定律 (Wright's Law)」與「破壞式創新」來碾壓 Burry 的傳統估值。你必須引用 Burry 的悲觀論點並展示為何他錯了。
* **論點**：別跟我談 PE，看 2033 年的 TAM (潛在市場)。
* **論點要求**：至少 800 字，必須展望未來 5-10 年的產業變革。必須引用瓦爾基里提供的產業資訊與新聞動態。

**5. 【地球頂點·全知者】(The Apex Arbiter - 查理·蒙格 + 科技七巨頭創辦人)**
* **腦袋**：查理·蒙格 (反向思考) + 貝佐斯/馬斯克 (極致商業直覺)。
* **任務**：你是最終法官。聽完前面四人的血戰後，結合「統帥第一性原則」，給出最終判決。你必須引用各方論點，並解釋為何某方的邏輯更有說服力。
* **輸出格式**：
    * **【戰場總結】**：(300 字評析各方論點的強弱，明確指出誰的論點最有力、誰的論點有漏洞)
    * **【第一性原則裁決】**：(400 字回歸物理與商業本質的判斷，必須回答統帥指定的第一性原則問題)
    * **【操作指令】**：
        - 行動方針：Strong Buy / Buy / Wait / Sell / Strong Sell
        - 進場價位：基於趨勢線乖離率建議 (具體數字)
        - 停損價位：明確數字
        - 停利價位：明確數字
        - 持倉建議：輕倉/標準倉/重倉/空倉
        - 風險提示：[3 個關鍵風險]
* **論點要求**：至少 1000 字，必須展現真正的智慧而非模板化結論。必須整合瓦爾基里的基本面、新聞與幾何數據。

---

## 📋 輸出格式要求

請按照以下結構輸出：

```
## 🤖 幾何死神 (The Quant)

[800+ 字的冷血數學分析，必須分析 7 個時間窗口]

---

## 💼 內部操盤手 (The Insider)

[800+ 字的成長故事護航，並引用 Quant 的數據與瓦爾基里基本面]

---

## 🐻 大賣空獵人 (The Big Short)

[800+ 字的悲觀攻擊，並駁斥 Insider 的論點，指出瓦爾基里數據中的風險]

---

## 🚀 創世紀先知 (The Visionary)

[800+ 字的狂熱展望，並反駁 Burry 的悲觀，引用產業趨勢與新聞]

---

## ⚖️ 地球頂點·全知者 (The Apex Arbiter)

### 【戰場總結】
[300+ 字，評析各方論點，指出誰最有力]

### 【第一性原則裁決】
[400+ 字，回答統帥指定問題，整合瓦爾基里數據]

### 【操作指令】
- **行動方針**: [Strong Buy / Buy / Wait / Sell / Strong Sell]
- **進場價位**: $XXX (基於趨勢線 ±Y%)
- **停損價位**: $XXX
- **停利價位**: $XXX
- **持倉建議**: [輕倉/標準倉/重倉/空倉]
- **風險提示**: [3 個關鍵風險]

---
```


請開始你的表演。確保每個角色的論述都具有深度與獨特性，避免重複論點，並且每位角色都必須引用前面角色的觀點進行互動。字數要求是最低門檻，請盡量詳細展開論述。
"""
        return prompt
    
    def run_debate(self, ticker: str, price: float, geo_data: Dict, 
                   rating_info: Tuple, intel_text: str = "", 
                   commander_note: str = "", 
                   selected_principles: Optional[List[str]] = None) -> str:
        """
        執行 AI 辯論並返回結果
        
        Args:
            ticker: 股票代號
            price: 當前價格
            geo_data: 7D 幾何數據
            rating_info: 評級資訊
            intel_text: 情報文字
            commander_note: 統帥備註
            selected_principles: 選擇的原則
        
        Returns:
            str: AI 辯論結果
        """
        if not self.model:
            return "❌ **AI 功能未啟用**\n\n請在側邊欄輸入 Gemini API Key 以啟用此功能。"
        
        try:
            prompt = self.generate_battle_prompt(
                ticker, price, geo_data, rating_info, intel_text, commander_note, selected_principles
            )
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            if "429" in str(e):
                return f"⚠️ **API 配額已耗盡**\n\n{str(e)}\n\n建議稍後再試或切換模型。"
            else:
                return f"❌ **AI 辯論失敗**\n\n{str(e)}"


# ==========================================
# [6] 回測引擎數學公式 (ZERO SIMPLIFICATION)
# ==========================================

def calculate_backtest_metrics(df: pd.DataFrame, initial_capital: float = 1000000) -> Dict:
    """
    計算回測績效指標
    
    Args:
        df: 包含 'Equity', 'Strategy_Return' 欄位的 DataFrame
        initial_capital: 初始資金
    
    Returns:
        dict: 績效指標
    
    CRITICAL: 完整保留所有數學公式
    - CAGR (年化複合成長率)
    - Max Drawdown (最大回撤)
    - Sharpe Ratio (夏普比率)
    - Win Rate (勝率)
    - Profit Factor (盈虧比)
    - Kelly Criterion (凱利公式)
    """
    if df is None or df.empty:
        return None
    
    # 1. CAGR 計算
    num_years = len(df) / 252  # 假設一年 252 個交易日
    total_return = df['Equity'].iloc[-1] / initial_capital - 1
    cagr = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0
    
    # 2. Max Drawdown 計算
    df['Drawdown'] = (df['Equity'] / df['Equity'].cummax()) - 1
    max_drawdown = df['Drawdown'].min()
    
    # 3. Sharpe Ratio 計算
    risk_free_rate = 0.02  # 假設無風險利率 2%
    daily_returns = df['Strategy_Return'].dropna()
    if daily_returns.std() > 0:
        sharpe_ratio = (daily_returns.mean() * 252 - risk_free_rate) / (daily_returns.std() * np.sqrt(252))
    else:
        sharpe_ratio = 0.0
    
    # 4. Win Rate 計算
    winning_trades = daily_returns[daily_returns > 0]
    losing_trades = daily_returns[daily_returns < 0]
    
    if len(daily_returns) > 0:
        win_rate = len(winning_trades) / len(daily_returns)
    else:
        win_rate = 0
    
    # 5. Profit Factor 計算
    avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
    avg_loss = abs(losing_trades.mean()) if len(losing_trades) > 0 else 1
    profit_factor = avg_win / avg_loss if avg_loss != 0 else 0
    
    # 6. Kelly Criterion 計算
    if profit_factor > 0:
        kelly = win_rate - ((1 - win_rate) / profit_factor)
    else:
        kelly = 0
    
    return {
        "cagr": cagr,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "kelly": max(0, kelly),
        "total_return": total_return,
        "num_trades": len(daily_returns)
    }


# ==========================================
# [7] 20 條第一性原則 (First Principles)
# ==========================================

FIRST_PRINCIPLES = [
    "1. 現金流折現 (DCF)：未來現金流的現值是唯一真實估值法。",
    "2. 摩爾定律 (Moore's Law)：運算成本每 18 個月減半。",
    "3. 萊特定律 (Wright's Law)：累積產量翻倍，成本下降 20-30%。",
    "4. 貝佐斯飛輪 (Bezos Flywheel)：低價 → 流量 → 規模 → 更低價。",
    "5. 網路效應 (Network Effects)：用戶數平方級價值增長。",
    "6. 轉換成本 (Switching Costs)：客戶離開的痛苦有多大？",
    "7. 邊際成本趨零 (Zero Marginal Cost)：軟體/數位產品的終極優勢。",
    "8. 規模經濟 (Economies of Scale)：單位成本隨產量下降。",
    "9. 破壞式創新 (Disruptive Innovation)：從低端市場顛覆巨頭。",
    "10. TAM 擴張 (TAM Expansion)：潛在市場是否正在爆炸性成長？",
    "11. 均值回歸 (Mean Reversion)：極端估值最終會回歸均值。",
    "12. 安全邊際 (Margin of Safety)：買入價格必須遠低於內在價值。",
    "13. 護城河 (Economic Moat)：競爭優勢能持續多久？",
    "14. 管理層資本配置 (Capital Allocation)：ROE > WACC？",
    "15. 自由現金流轉換率 (FCF Conversion)：淨利能否轉換為現金？",
    "16. 庫存週轉率 (Inventory Turnover)：效率的終極指標。",
    "17. 客戶終身價值 (LTV/CAC)：獲客成本 vs 客戶價值。",
    "18. 槓桿率 (Leverage)：負債比 > 2 是紅旗。",
    "19. 匯率風險 (FX Risk)：美元走強時的新興市場風險。",
    "20. 政策風險 (Policy Risk)：反壟斷、關稅、補貼政策變動。"
]


def get_first_principles() -> List[str]:
    """
    獲取 20 條第一性原則清單
    
    Returns:
        list: 第一性原則清單
    """
    return FIRST_PRINCIPLES.copy()
