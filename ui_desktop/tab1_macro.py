# ui_desktop/tab1_macro.py
# Titan SOP V100.0 - Tab 1: 宏觀風控 (Macro Risk Command Center)
# 功能：7D 全景風控儀表板 (Command Center Layout)
# 美學：Black/Gold/Neon + Bloomberg Terminal Style

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from data_engine import get_market_benchmarks, download_stock_price
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def render():
    """
    渲染宏觀風控 Tab - Command Center Layout
    
    結構：
    - Row 1: The HUD (VIX + Signal + PR90 + Bull/Bear)
    - Row 2: WTX Predator (Hero Section - Baseball Chart)
    - Row 3: Market Intelligence (PR90 Histogram + Top 50 Scatter)
    - Row 4: Sector & Volume (Heatmap + Dynamic List)
    """
    
    # ==========================================
    # Header: Glowing Title
    # ==========================================
    
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="
                font-size: 3em;
                color: #FFD700;
                text-shadow: 0 0 20px rgba(255, 215, 0, 0.7), 0 0 40px rgba(255, 215, 0, 0.5);
                font-weight: 700;
                letter-spacing: 2px;
                margin: 0;
            ">🛡️ 宏觀風控指揮中心</h1>
            <p style="
                color: #AAAAAA;
                font-size: 1.2em;
                margin-top: 10px;
            ">Macro Risk Command Center | 全景戰情儀表板</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # Check if CB data is loaded
    # ==========================================
    
    df = st.session_state.get('df', pd.DataFrame())
    
    # ==========================================
    # ROW 1: THE HUD (High-Impact Metrics)
    # ==========================================
    
    st.markdown("### 🎯 戰情總覽 (The HUD)")
    
    with st.spinner("正在下載宏觀數據..."):
        try:
            benchmarks = get_market_benchmarks(period='1mo')
            
            if benchmarks is None or benchmarks.empty:
                st.warning("⚠️ 宏觀數據暫時無法獲取，顯示模擬數據")
                vix_current = 20.5
                vix_change = -2.3
            else:
                vix_current = benchmarks['^VIX'].iloc[-1] if '^VIX' in benchmarks.columns else 20.5
                vix_change = benchmarks['^VIX'].iloc[-1] - benchmarks['^VIX'].iloc[0] if '^VIX' in benchmarks.columns else -2.3
        
        except Exception as e:
            st.error(f"數據載入失敗: {e}")
            vix_current = 20.5
            vix_change = -2.3
    
    # HUD Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "😱 VIX 恐慌指數",
            f"{vix_current:.2f}",
            f"{vix_change:+.2f}",
            delta_color="inverse"
        )
    
    with col2:
        # Signal Light Logic
        if vix_current < 15:
            signal = "🟢"
            signal_text = "綠燈 (平穩)"
            signal_color = "#00FF00"
        elif vix_current < 20:
            signal = "🟡"
            signal_text = "黃燈 (謹慎)"
            signal_color = "#FFD700"
        elif vix_current < 30:
            signal = "🟠"
            signal_text = "橙燈 (風險)"
            signal_color = "#FFA500"
        else:
            signal = "🔴"
            signal_text = "紅燈 (恐慌)"
            signal_color = "#FF0000"
        
        st.markdown(
            f"""
            <div style="text-align: center; padding: 15px; background-color: #1a1a2e; border-radius: 10px; border: 2px solid {signal_color};">
                <div style="font-size: 48px; margin-bottom: 5px;">{signal}</div>
                <div style="font-size: 14px; color: {signal_color}; font-weight: bold;">{signal_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        # PR90 (Phase 1 Placeholder)
        if not df.empty and 'close' in df.columns:
            pr90_value = df['close'].quantile(0.9)
            st.metric("🔥 PR90 市場熱度", f"{pr90_value:.2f}", "實時計算")
        else:
            st.metric("🔥 PR90 市場熱度", "125.0", "Phase 1 Demo")
    
    with col4:
        # Bull/Bear Thermometer (Phase 1 Placeholder)
        st.metric("📊 多空溫度計", "🐂 65% / 🐻 35%", "Phase 1 Demo")
    
    st.divider()
    
    # ==========================================
    # ROW 2: WTX PREDATOR (Hero Section)
    # ==========================================
    
    st.markdown("### 🎯 台指期獵殺者 (WTX Predator)")
    st.caption("獨門戰法：12 個月結算慣性推導本月虛擬 K 棒與目標價")
    
    col_chart, col_targets = st.columns([7, 3])
    
    with col_chart:
        # [PHASE 1] Baseball Chart with demo data
        st.info("🚧 Phase 1: 使用模擬數據展示 Baseball Chart 結構")
        
        # Demo data
        anchor_price = 22000
        current_price = 22300
        hr_target = 23500
        b3_target = 22800
        b2_target = 22500
        b1_target = 22200
        
        # Create baseball chart
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=['定錨價', '當前', '1B', '2B', '3B', 'HR'],
            y=[anchor_price, current_price, b1_target, b2_target, b3_target, hr_target],
            marker_color=['#444', '#FFD700', '#00FF00', '#00FF00', '#00FF00', '#FF0000'],
            text=[f"{anchor_price}", f"{current_price}", f"{b1_target}", f"{b2_target}", f"{b3_target}", f"{hr_target}"],
            textposition='auto',
        ))
        
        fig.update_layout(
            height=300,
            template="plotly_dark",
            showlegend=False,
            xaxis_title="",
            yaxis_title="點位",
            hovermode='x'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_targets:
        st.markdown("#### 🎯 獵殺目標")
        
        targets_df = pd.DataFrame({
            '等級': ['🏆 HR', '⚾ 3B', '⚾ 2B', '⚾ 1B'],
            '目標價': [23500, 22800, 22500, 22200],
            '距離': ['+1,200', '+500', '+200', '-100']
        })
        
        st.dataframe(
            targets_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown(f"""
        **當前狀態**:
        - 定錨價: 22,000
        - 現價: 22,300
        - 距HR: +1,200
        """)
    
    st.divider()
    
    # ==========================================
    # ROW 3: MARKET INTELLIGENCE
    # ==========================================
    
    st.markdown("### 📊 市場情報 (Market Intelligence)")
    
    col_hist, col_scatter = st.columns(2)
    
    with col_hist:
        st.markdown("#### 📈 PR90 籌碼分佈圖")
        
        if not df.empty and 'close' in df.columns:
            # Real histogram
            fig_hist = go.Figure()
            
            fig_hist.add_trace(go.Histogram(
                x=df['close'],
                nbinsx=20,
                marker_color='#00FF00',
                opacity=0.7
            ))
            
            # Add PR90 line
            pr90 = df['close'].quantile(0.9)
            fig_hist.add_vline(
                x=pr90,
                line_dash="dash",
                line_color="#FFD700",
                annotation_text=f"PR90: {pr90:.2f}"
            )
            
            fig_hist.update_layout(
                height=300,
                template="plotly_dark",
                showlegend=False,
                xaxis_title="CB 市價",
                yaxis_title="數量"
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("📂 請上傳 CB 清單以顯示籌碼分佈圖")
    
    with col_scatter:
        st.markdown("#### 🎯 高價權值股趨勢雷達 (Top 50)")
        
        st.info("🚧 Phase 1: 趨勢雷達尚未完整移植")
        
        # Placeholder scatter
        demo_data = pd.DataFrame({
            'R²': np.random.rand(20) * 100,
            'Slope': np.random.rand(20) * 50 - 25,
            'Stock': [f"標的{i}" for i in range(20)]
        })
        
        fig_scatter = px.scatter(
            demo_data,
            x='R²',
            y='Slope',
            text='Stock',
            color='Slope',
            color_continuous_scale=['red', 'yellow', 'green']
        )
        
        fig_scatter.update_layout(
            height=300,
            template="plotly_dark",
            showlegend=False
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.divider()
    
    # ==========================================
    # ROW 4: SECTOR & VOLUME
    # ==========================================
    
    st.markdown("### 🗺️ 族群熱度雷達 (Sector Heatmap)")
    
    if not df.empty:
        st.info("🚧 Phase 1: 族群熱度雷達尚未完整移植 (需要族群分類數據)")
        
        # Placeholder treemap
        demo_sectors = pd.DataFrame({
            'Sector': ['半導體', 'AI', '航運', '金融', '傳產', '生技'],
            'Count': [15, 12, 8, 10, 6, 5],
            'AvgChange': [5.2, 3.8, -1.2, 0.5, -2.1, 1.0]
        })
        
        fig_tree = px.treemap(
            demo_sectors,
            path=['Sector'],
            values='Count',
            color='AvgChange',
            color_continuous_scale=['red', 'yellow', 'green'],
            color_continuous_midpoint=0
        )
        
        fig_tree.update_layout(
            height=300,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.info("📂 請上傳 CB 清單以顯示族群熱度雷達")
    
    # Dynamic Top 100 (Hidden in Expander)
    with st.expander("📋 成交重心即時預測 (動態 Top 100)", expanded=False):
        st.info("🚧 Phase 1: 動態 Top 100 尚未完整移植 (需要即時成交數據)")
        
        st.markdown("""
        **Phase 2 將包含**:
        - 即時成交量排行
        - 資金流向分析
        - 主力進出追蹤
        """)
    
    st.divider()
    
    # ==========================================
    # FOOTER: VIX Trend Chart
    # ==========================================
    
    st.markdown("### 📈 VIX 30 日趨勢")
    
    if benchmarks is not None and not benchmarks.empty and '^VIX' in benchmarks.columns:
        fig_vix = go.Figure()
        
        fig_vix.add_trace(go.Scatter(
            x=benchmarks.index,
            y=benchmarks['^VIX'],
            mode='lines',
            name='VIX',
            line=dict(color='#FF4500', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 69, 0, 0.2)'
        ))
        
        # Add risk zones
        fig_vix.add_hline(y=15, line_dash="dash", line_color="#00FF00", annotation_text="低波動")
        fig_vix.add_hline(y=20, line_dash="dash", line_color="#FFD700", annotation_text="正常")
        fig_vix.add_hline(y=30, line_dash="dash", line_color="#FF0000", annotation_text="恐慌")
        
        fig_vix.update_layout(
            height=300,
            template="plotly_dark",
            showlegend=False,
            xaxis_title="日期",
            yaxis_title="VIX 指數",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_vix, use_container_width=True)
    else:
        st.warning("VIX 趨勢圖暫時無法顯示")
    
    # ==========================================
    # RISK WARNING
    # ==========================================
    
    st.markdown("### ⚠️ 風險提示")
    
    if vix_current < 15:
        st.success("""
        **🟢 綠燈操作建議**:
        - 市場情緒平穩，可積極佈局
        - 適合進攻型策略
        - 關注高 Beta 標的
        """)
    
    elif vix_current < 20:
        st.info("""
        **🟡 黃燈操作建議**:
        - 維持正常倉位
        - 注意防守型配置
        - 避免過度槓桿
        """)
    
    elif vix_current < 30:
        st.warning("""
        **🟠 橙燈操作建議**:
        - 降低倉位至 50%
        - 增加現金比重
        - 嚴格設定停損
        """)
    
    else:
        st.error("""
        **🔴 紅燈操作建議**:
        - 現金為王，空倉觀望
        - 等待恐慌情緒消退
        - 準備撿便宜清單
        """)
    
    # Update timestamp
    st.caption(f"📅 數據更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
