# ui_mobile/tab2_analysis.py
# Titan SOP V100.0 - Mobile Tab 2: 監控清單與簡單圖表
# 功能：顯示鎖定的股票、簡單線圖

import streamlit as st
import pandas as pd
from data_engine import download_stock_price


def render():
    """
    渲染監控清單與分析頁面
    
    功能：
    - 顯示鎖定的股票列表
    - 點擊顯示簡單線圖
    """
    st.markdown("### 📊 監控雷達")
    st.caption("已鎖定的標的列表")
    
    # ==========================================
    # 檢查監控清單
    # ==========================================
    
    watchlist = st.session_state.get('watchlist', [])
    
    if not watchlist:
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); border-radius: 20px; margin: 20px 0;">
                <div style="font-size: 80px; margin-bottom: 20px;">📭</div>
                <h2 style="color: #FFD700; margin-bottom: 20px;">監控清單為空</h2>
                <p style="color: #AAAAAA; font-size: 16px; line-height: 1.6;">
                    前往「首頁」滑動鎖定標的<br>
                    鎖定後會顯示在這裡
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # ==========================================
    # 顯示監控清單統計
    # ==========================================
    
    st.markdown("#### 📈 統計")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("總數量", f"{len(watchlist)} 檔")
    
    with col2:
        # 計算平均角度
        avg_angle = sum(item['angle_3m'] for item in watchlist) / len(watchlist)
        st.metric("平均角度", f"{avg_angle:.1f}°")
    
    with col3:
        # 計算平均加速度
        avg_accel = sum(item['acceleration'] for item in watchlist) / len(watchlist)
        st.metric("平均加速", f"{avg_accel:+.1f}°")
    
    st.divider()
    
    # ==========================================
    # 顯示清單
    # ==========================================
    
    st.markdown("#### 🔒 鎖定清單")
    
    # 初始化選擇的標的
    if 'selected_watchlist_item' not in st.session_state:
        st.session_state.selected_watchlist_item = None
    
    # 顯示每個標的為卡片
    for idx, item in enumerate(watchlist):
        code = item['code']
        name = item['name']
        stock_code = item['stock_code']
        rating_level = item['rating_level']
        rating_name = item['rating_name']
        rating_color = item['rating_color']
        angle_3m = item['angle_3m']
        acceleration = item['acceleration']
        
        # 卡片樣式
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); 
                        border-radius: 16px; 
                        padding: 20px; 
                        margin: 10px 0;
                        border-left: 4px solid {rating_color};">
                
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 24px; font-weight: bold; color: #FFFFFF; margin-bottom: 5px;">
                            {code} - {name}
                        </div>
                        <div style="font-size: 14px; color: #AAAAAA;">
                            標的: {stock_code}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 20px; font-weight: bold; color: {rating_color};">
                            {rating_level}
                        </div>
                        <div style="font-size: 12px; color: #AAAAAA;">
                            {rating_name}
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 15px; display: flex; justify-content: space-between;">
                    <div style="text-align: center;">
                        <div style="font-size: 12px; color: #888;">3M 角度</div>
                        <div style="font-size: 18px; font-weight: bold; color: {'#00FF00' if angle_3m > 0 else '#FF4500'};">
                            {angle_3m:+.1f}°
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 12px; color: #888;">加速度</div>
                        <div style="font-size: 18px; font-weight: bold; color: {'#00FF00' if acceleration > 0 else '#FF4500'};">
                            {acceleration:+.1f}°
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 操作按鈕
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"📈 查看圖表", key=f"view_{idx}", use_container_width=True):
                st.session_state.selected_watchlist_item = stock_code
                st.rerun()
        
        with col2:
            if st.button(f"🗑️ 移除", key=f"remove_{idx}", use_container_width=True):
                st.session_state.watchlist.pop(idx)
                st.success(f"✅ 已移除 {code}")
                st.rerun()
    
    st.divider()
    
    # ==========================================
    # 顯示圖表
    # ==========================================
    
    selected_ticker = st.session_state.get('selected_watchlist_item')
    
    if selected_ticker:
        st.markdown(f"#### 📈 {selected_ticker} - K 線圖")
        
        with st.spinner("正在載入圖表..."):
            try:
                # 下載數據
                df_price = download_stock_price(selected_ticker, period='3mo')
                
                if df_price is not None and not df_price.empty:
                    # 使用簡單線圖（移動版優化）
                    st.line_chart(df_price['Close'], height=300)
                    
                    # 顯示基本統計
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        current_price = df_price['Close'].iloc[-1]
                        st.metric("當前價格", f"${current_price:.2f}")
                    
                    with col2:
                        price_change = df_price['Close'].iloc[-1] - df_price['Close'].iloc[0]
                        price_change_pct = (price_change / df_price['Close'].iloc[0]) * 100
                        st.metric(
                            "漲跌幅",
                            f"{price_change_pct:+.2f}%",
                            f"${price_change:+.2f}"
                        )
                    
                    with col3:
                        max_price = df_price['Close'].max()
                        st.metric("期間最高", f"${max_price:.2f}")
                    
                    # 關閉圖表按鈕
                    if st.button("❌ 關閉圖表", use_container_width=True):
                        st.session_state.selected_watchlist_item = None
                        st.rerun()
                
                else:
                    st.error(f"❌ 無法載入 {selected_ticker} 的數據")
            
            except Exception as e:
                st.error(f"❌ 圖表載入失敗: {e}")
    
    # ==========================================
    # 批次操作
    # ==========================================
    
    st.divider()
    
    st.markdown("#### ⚙️ 批次操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 匯出清單", use_container_width=True):
            # 轉換為 DataFrame
            df_export = pd.DataFrame(watchlist)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="⬇️ 下載 CSV",
                data=csv,
                file_name="titan_watchlist.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("🗑️ 清空清單", use_container_width=True):
            if st.session_state.watchlist:
                st.session_state.watchlist = []
                st.success("✅ 清單已清空")
                st.rerun()
