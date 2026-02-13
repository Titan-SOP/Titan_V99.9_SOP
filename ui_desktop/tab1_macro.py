# ui_desktop/tab1_macro.py
# Titan SOP V100.0 - Tab 1: 宏觀風控
# 功能：VIX 恐慌指數、市場信號燈、產業熱圖

import streamlit as st
import plotly.graph_objects as go
from data_engine import get_market_benchmarks
from datetime import datetime


def render():
    """
    渲染宏觀風控 Tab
    
    功能：
    - VIX 恐慌指數
    - 市場信號燈
    - 大盤指數對比
    """
    st.subheader("🛡️ 宏觀風控面板")
    st.caption("實時監控市場恐慌度與風險信號")
    
    # ==========================================
    # 下載宏觀指標
    # ==========================================
    
    with st.spinner("正在下載宏觀數據..."):
        try:
            benchmarks = get_market_benchmarks(period='1mo')
            
            if benchmarks is None or benchmarks.empty:
                st.warning("⚠️ 無法獲取宏觀數據")
                return
            
        except Exception as e:
            st.error(f"❌ 數據載入失敗: {e}")
            return
    
    # ==========================================
    # VIX 恐慌指數
    # ==========================================
    
    st.markdown("### 📊 VIX 恐慌指數")
    
    if '^VIX' in benchmarks.columns:
        vix_current = benchmarks['^VIX'].iloc[-1]
        vix_change = benchmarks['^VIX'].iloc[-1] - benchmarks['^VIX'].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "VIX 當前值",
                f"{vix_current:.2f}",
                f"{vix_change:+.2f}",
                delta_color="inverse"
            )
        
        with col2:
            # 信號判斷
            if vix_current < 15:
                signal = "🟢 綠燈"
                signal_text = "市場平穩"
                signal_color = "#00FF00"
            elif vix_current < 20:
                signal = "🟡 黃燈"
                signal_text = "適度謹慎"
                signal_color = "#FFD700"
            elif vix_current < 30:
                signal = "🟠 橙燈"
                signal_text = "風險升溫"
                signal_color = "#FFA500"
            else:
                signal = "🔴 紅燈"
                signal_text = "恐慌模式"
                signal_color = "#FF0000"
            
            st.markdown(
                f"""
                <div style="text-align: center; padding: 20px; background-color: #1a1a2e; border-radius: 10px; border: 2px solid {signal_color};">
                    <div style="font-size: 36px; margin-bottom: 10px;">{signal}</div>
                    <div style="font-size: 18px; color: {signal_color}; font-weight: bold;">{signal_text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            # 風險等級說明
            st.markdown("""
            **VIX 風險等級**:
            - < 15: 低波動
            - 15-20: 正常
            - 20-30: 高波動
            - > 30: 極度恐慌
            """)
        
        # VIX 趨勢圖
        st.markdown("#### 📈 VIX 30 日趨勢")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=benchmarks.index,
            y=benchmarks['^VIX'],
            mode='lines',
            name='VIX',
            line=dict(color='#FF4500', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 69, 0, 0.2)'
        ))
        
        # 添加風險區間線
        fig.add_hline(y=15, line_dash="dash", line_color="#00FF00", annotation_text="低波動")
        fig.add_hline(y=20, line_dash="dash", line_color="#FFD700", annotation_text="正常")
        fig.add_hline(y=30, line_dash="dash", line_color="#FF0000", annotation_text="恐慌")
        
        fig.update_layout(
            height=400,
            template="plotly_dark",
            showlegend=False,
            xaxis_title="日期",
            yaxis_title="VIX 指數",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("⚠️ VIX 數據暫時無法獲取")
    
    st.divider()
    
    # ==========================================
    # 大盤對比
    # ==========================================
    
    st.markdown("### 🌍 全球指數對比")
    
    col1, col2, col3 = st.columns(3)
    
    # 台股加權指數
    with col1:
        if '^TWII' in benchmarks.columns:
            twii_current = benchmarks['^TWII'].iloc[-1]
            twii_change = (benchmarks['^TWII'].iloc[-1] / benchmarks['^TWII'].iloc[0] - 1) * 100
            
            st.metric(
                "台股加權 (^TWII)",
                f"{twii_current:,.0f}",
                f"{twii_change:+.2f}%"
            )
        else:
            st.info("台股數據載入中...")
    
    # 美股 S&P 500
    with col2:
        if '^GSPC' in benchmarks.columns:
            gspc_current = benchmarks['^GSPC'].iloc[-1]
            gspc_change = (benchmarks['^GSPC'].iloc[-1] / benchmarks['^GSPC'].iloc[0] - 1) * 100
            
            st.metric(
                "美股 S&P 500 (^GSPC)",
                f"{gspc_current:,.0f}",
                f"{gspc_change:+.2f}%"
            )
        else:
            st.info("S&P 500 數據載入中...")
    
    # 美元/台幣匯率
    with col3:
        if 'USDTWD=X' in benchmarks.columns:
            usdtwd_current = benchmarks['USDTWD=X'].iloc[-1]
            usdtwd_change = benchmarks['USDTWD=X'].iloc[-1] - benchmarks['USDTWD=X'].iloc[0]
            
            st.metric(
                "美元/台幣 (USDTWD)",
                f"{usdtwd_current:.2f}",
                f"{usdtwd_change:+.2f}",
                delta_color="off"
            )
        else:
            st.info("匯率數據載入中...")
    
    # 指數趨勢對比圖
    st.markdown("#### 📊 30 日表現對比")
    
    fig2 = go.Figure()
    
    # 標準化處理（以首日為 100）
    for col in benchmarks.columns:
        if col == '^VIX':
            continue  # VIX 已經單獨顯示
        
        normalized = (benchmarks[col] / benchmarks[col].iloc[0]) * 100
        
        fig2.add_trace(go.Scatter(
            x=benchmarks.index,
            y=normalized,
            mode='lines',
            name=col,
            line=dict(width=2)
        ))
    
    fig2.update_layout(
        height=400,
        template="plotly_dark",
        xaxis_title="日期",
        yaxis_title="相對表現 (首日 = 100)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    # ==========================================
    # 風險提示
    # ==========================================
    
    st.markdown("### ⚠️ 風險提示")
    
    # 根據 VIX 給出操作建議
    if '^VIX' in benchmarks.columns:
        vix_current = benchmarks['^VIX'].iloc[-1]
        
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
    
    # 更新時間
    st.caption(f"📅 數據更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
