# ui_desktop/tab1_macro.py
# Titan SOP V100.0 - Tab 1: 宏觀風控
# 修正：解決 ['name', 'stock_code', 'close'] not in index 崩潰問題

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_engine import get_market_benchmarks

def render():
    """
    渲染宏觀風控 Tab
    """
    st.subheader("🛡️ 宏觀風控面板")
    st.caption("實時監控市場恐慌度與風險信號")
    
    # 獲取 Session 中的數據
    df = st.session_state.get('df', pd.DataFrame())
    
    # ==========================================
    # 1. 宏觀指標 (VIX & 大盤) - 不依賴上傳數據
    # ==========================================
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📊 VIX 恐慌指數")
        with st.spinner("連線全球市場數據中..."):
            try:
                benchmarks = get_market_benchmarks(period='1mo')
                if not benchmarks.empty and '^VIX' in benchmarks.columns:
                    vix_current = benchmarks['^VIX'].iloc[-1]
                    vix_prev = benchmarks['^VIX'].iloc[-2]
                    delta = vix_current - vix_prev
                    
                    st.metric(
                        "VIX Index", 
                        f"{vix_current:.2f}", 
                        f"{delta:.2f}",
                        delta_color="inverse"
                    )
                    
                    # 燈號判斷
                    if vix_current < 15:
                        st.success("🟢 綠燈：市場情緒平穩，積極進攻")
                    elif vix_current < 25:
                        st.warning("🟡 黃燈：波動加劇，注意風險")
                    else:
                        st.error("🔴 紅燈：極度恐慌，現金為王")
                else:
                    st.info("⚠️ 暫時無法獲取 VIX 數據")
            except Exception as e:
                st.error("連線超時，請稍後再試")

    with col2:
        st.markdown("### 📈 大盤趨勢對比")
        if not benchmarks.empty:
            fig = go.Figure()
            for col in benchmarks.columns:
                fig.add_trace(go.Scatter(x=benchmarks.index, y=benchmarks[col], name=col))
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==========================================
    # 2. 族群熱力圖 (需要上傳數據)
    # ==========================================
    
    st.markdown("### 🔥 族群資金流向")
    
    # --- 關鍵修正：數據安檢門 ---
    # 檢查 df 是否為空，以及是否包含必要欄位
    required_cols = ['name', 'stock_code', 'close']
    missing_cols = [c for c in required_cols if c not in df.columns]
    
    if df.empty:
        st.info("👋 請在左側側邊欄上傳 Excel/CSV 檔案，以解鎖族群熱力圖分析。")
        return
        
    if missing_cols:
        st.warning(f"⚠️ 上傳的檔案缺少必要欄位：{missing_cols}")
        st.caption("請確認您的 Excel 包含：股票名稱、股票代號、收盤價")
        return
        
    # --- 如果通過安檢，才執行運算 ---
    try:
        # 簡單的族群分類邏輯 (範例：依據代號分類，實際應需產業欄位)
        # 這裡先做一個簡單的 TreeMap
        df['market_value'] = df['close'] * 1000 # 假設
        df['change'] = 0.0 # 暫時用 0，如果有漲跌幅欄位更好
        
        fig_tree = go.Figure(go.Treemap(
            labels=df['name'],
            parents=["台股"] * len(df),
            values=df['market_value'],
            textinfo="label+value",
        ))
        
        fig_tree.update_layout(
            template="plotly_dark",
            margin=dict(t=0, l=0, r=0, b=0),
            height=400
        )
        st.plotly_chart(fig_tree, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ 熱力圖繪製失敗: {e}")