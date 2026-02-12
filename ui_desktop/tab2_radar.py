# ui_desktop/tab2_radar.py
# Titan V100.0 - Desktop UI: Hunter Radar
# 狀態: 桌面版獵殺雷達

import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
from datetime import datetime

def plot_candle_chart(stock_code):
    """Renders an interactive K-line chart for the given stock code."""
    target_code = str(stock_code).strip()
    if len(target_code) == 5 and target_code.isdigit():
        target_code = target_code[:4]
    
    try:
        df = yf.download(f"{target_code}.TW", period="2y", progress=False)
        if df.empty:
            df = yf.download(f"{target_code}.TWO", period="2y", progress=False)
        
        if not df.empty:
            df = df.reset_index()
            df['MA87'] = df['Close'].rolling(87).mean()
            df['MA284'] = df['Close'].rolling(284).mean()
            
            base = alt.Chart(df).encode(x=alt.X('Date:T', axis=alt.Axis(title='日期')))
            color_cond = alt.condition("datum.Open <= datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))
            candles = base.mark_rule().encode(y='Low', y2='High') + base.mark_bar().encode(y='Open', y2='Close', color=color_cond)
            ma87_line = base.mark_line(color='orange').encode(y='MA87')
            ma284_line = base.mark_line(color='cyan').encode(y='MA284')
            
            st.altair_chart((candles + ma87_line + ma284_line).interactive(), use_container_width=True)
        else:
            st.error(f"查無 K 線資料: {target_code}")
    except Exception as e:
        st.warning(f"K 線圖生成失敗: {e}")

def render(df, strategy_engine, kb):
    """Renders the Hunter Radar tab."""
    st.header("🏹 獵殺雷達 (CB Hunter Zone)")

    with st.expander("2.1 自動獵殺推薦 (Auto Sniper)", expanded=True):
        if not df.empty:
            if st.button("🚀 啟動 SOP 全市場普查", type="primary"):
                with st.spinner("執行全市場掃描..."):
                    scan_results_df = strategy_engine.scan_entire_portfolio(df)
                    st.session_state['scan_results'] = scan_results_df
                    st.success(f"掃描完成！共 {len(scan_results_df)} 筆資料。")
            
            if 'scan_results' in st.session_state:
                results = st.session_state['scan_results']
                st.dataframe(results[['code', 'name', 'price', 'stock_price', 'score', 'action', 'premium', 'converted_ratio']].head(20))
        else:
            st.info("請上傳 CB 清單以啟動掃描。")

    with st.expander("2.2 核心策略檢核 (The War Room)", expanded=False):
        if 'scan_results' in st.session_state:
            results = st.session_state['scan_results']
            if not results.empty:
                # Filter for top candidates
                candidates = results[results['score'] >= 60].sort_values('score', ascending=False)
                for _, row in candidates.head(10).iterrows():
                    with st.expander(f"👑 {row['name']} ({row['code']}) | 評分: {int(row['score'])}"):
                        st.markdown(row['full_report'], unsafe_allow_html=True)
                        plot_candle_chart(row['stock_code'])
            else:
                st.info("無符合條件的標的。")
        else:
            st.info("請先執行市場普查。")
            
    with st.expander("2.3 潛在風險雷達 (Risk Radar)", expanded=False):
        if 'scan_results' in st.session_state:
            results = st.session_state['scan_results']
            tab1, tab2, tab3 = st.tabs(["**☠️ 籌碼鬆動**", "**⚠️ 高溢價**", "**🧊 流動性陷阱**"])
            with tab1:
                st.dataframe(results[results['converted_ratio'] > 30])
            with tab2:
                st.dataframe(results[results['premium'] > 20])
            with tab3:
                st.dataframe(results[results['avg_volume'] < 10])
        else:
            st.info("請先執行市場普查。")