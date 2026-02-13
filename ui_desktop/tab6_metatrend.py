# ui_desktop/tab6_metatrend.py
# Titan SOP V100.0 - Tab 6: 元趨勢戰法
# 功能：7D 幾何引擎、22 階信評、獵殺清單

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core_logic import compute_7d_geometry, titan_rating_system
from utils_ui import get_rating_color, format_rating_badge


def render():
    """
    渲染元趨勢戰法 Tab
    
    功能：
    - 7D 幾何全景
    - 22 階泰坦信評
    - 獵殺清單管理
    """
    st.subheader("🧠 元趨勢戰法")
    st.caption("7 維度幾何 × 22 階信評 × 獵殺清單")
    
    # ==========================================
    # 標的輸入
    # ==========================================
    
    st.markdown("### 🎯 輸入分析標的")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "輸入標的代號 (支援台股/美股)",
            value=st.session_state.get('selected_ticker', '2330'),
            placeholder="例如：2330 (上市), 5274 (上櫃), NVDA (美股)",
            key="metatrend_ticker"
        )
    
    with col2:
        st.write("")  # 對齊用
        st.write("")
        scan_button = st.button("📐 啟動掃描", use_container_width=True, type="primary")
    
    if not ticker:
        st.info("👆 請輸入標的代號開始分析")
        return
    
    # ==========================================
    # 執行 7D 幾何掃描
    # ==========================================
    
    if scan_button or 'geo_results' in st.session_state:
        
        if scan_button:
            with st.spinner(f"正在計算 {ticker} 的 7D 幾何數據..."):
                try:
                    geo_results = compute_7d_geometry(ticker)
                    
                    if geo_results is None:
                        st.error(f"❌ 無法獲取 {ticker} 的數據。已嘗試 .TW 和 .TWO，請檢查代號。")
                        return
                    
                    # 計算信評
                    rating_info = titan_rating_system(geo_results)
                    
                    # 儲存到 session_state
                    st.session_state.geo_results = geo_results
                    st.session_state.rating_info = rating_info
                    st.session_state.current_ticker = ticker
                    
                    st.success(f"✅ 掃描完成！信評等級: **{rating_info[0]} - {rating_info[1]}**")
                
                except Exception as e:
                    st.error(f"❌ 掃描失敗: {e}")
                    return
        
        # 獲取數據
        geo = st.session_state.get('geo_results')
        rating = st.session_state.get('rating_info')
        current_ticker = st.session_state.get('current_ticker', ticker)
        
        if geo is None or rating is None:
            return
        
        st.divider()
        
        # ==========================================
        # 信評顯示
        # ==========================================
        
        st.markdown("### 🏆 泰坦信評系統")
        
        level, name, desc, color = rating
        
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, {color} 0%, #000000 100%); 
                        color: #FFFFFF; 
                        padding: 30px; 
                        border-radius: 15px; 
                        text-align: center;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);">
                <h1 style="margin: 0; font-size: 48px; text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);">
                    {level}
                </h1>
                <h2 style="margin: 10px 0; font-size: 32px;">
                    {name}
                </h2>
                <p style="margin: 10px 0; font-size: 18px; opacity: 0.9;">
                    {desc}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.divider()
        
        # ==========================================
        # 7D 幾何數據
        # ==========================================
        
        st.markdown("### 📐 7D 幾何全景")
        
        # 創建表格數據
        periods = ['35Y', '10Y', '5Y', '3Y', '1Y', '6M', '3M']
        period_labels = {
            '35Y': '超長期 (35年)',
            '10Y': '長期 (10年)',
            '5Y': '中長期 (5年)',
            '3Y': '中期 (3年)',
            '1Y': '短中期 (1年)',
            '6M': '短期 (6月)',
            '3M': '極短期 (3月)'
        }
        
        # 顯示數據表格
        geo_data = []
        for period in periods:
            data = geo[period]
            geo_data.append({
                '時間窗口': period_labels[period],
                '角度 (°)': f"{data['angle']:.2f}",
                'R² (線性度)': f"{data['r2']:.4f}",
                '斜率': f"{data['slope']:.6f}"
            })
        
        df_geo = pd.DataFrame(geo_data)
        
        st.dataframe(
            df_geo,
            use_container_width=True,
            hide_index=True
        )
        
        # 關鍵指標
        st.markdown("#### 🔑 關鍵指標")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "加速度",
                f"{geo['acceleration']:+.2f}°",
                help="3M 角度 - 1Y 角度"
            )
        
        with col2:
            phoenix_status = "🔥 觸發" if geo['phoenix_signal'] else "❄️ 未觸發"
            phoenix_color = "normal" if geo['phoenix_signal'] else "off"
            
            st.metric(
                "Phoenix 信號",
                phoenix_status,
                help="長空短多，逆轉信號",
                delta_color=phoenix_color
            )
        
        with col3:
            # 趨勢一致性
            angles = [geo[p]['angle'] for p in periods]
            consistency = sum(1 for a in angles if a > 0) / len(angles) * 100
            
            st.metric(
                "趨勢一致性",
                f"{consistency:.0f}%",
                help="正向角度比例"
            )
        
        st.divider()
        
        # ==========================================
        # 幾何視覺化
        # ==========================================
        
        st.markdown("### 📊 幾何視覺化")
        
        # 角度雷達圖
        fig = go.Figure()
        
        angles_data = [geo[p]['angle'] for p in periods]
        
        fig.add_trace(go.Scatterpolar(
            r=angles_data,
            theta=[period_labels[p] for p in periods],
            fill='toself',
            name='角度',
            line=dict(color='#00FF00', width=2)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-90, 90]
                )
            ),
            showlegend=False,
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # R² 線性度圖
        st.markdown("#### 📈 R² 線性度分析")
        
        fig_r2 = go.Figure()
        
        r2_data = [geo[p]['r2'] for p in periods]
        
        fig_r2.add_trace(go.Bar(
            x=[period_labels[p] for p in periods],
            y=r2_data,
            marker_color='#FFD700',
            text=[f"{r:.3f}" for r in r2_data],
            textposition='outside'
        ))
        
        fig_r2.add_hline(y=0.9, line_dash="dash", line_color="#00FF00", annotation_text="優秀 (0.9)")
        fig_r2.add_hline(y=0.7, line_dash="dash", line_color="#FFD700", annotation_text="良好 (0.7)")
        
        fig_r2.update_layout(
            template="plotly_dark",
            yaxis_title="R² (線性度)",
            xaxis_title="時間窗口",
            height=400,
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig_r2, use_container_width=True)
        
        st.divider()
        
        # ==========================================
        # 獵殺清單管理
        # ==========================================
        
        st.markdown("### 📝 獵殺清單")
        
        # 初始化獵殺清單
        if 'hunt_list' not in st.session_state:
            st.session_state.hunt_list = []
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"當前分析標的: **{current_ticker}** | 評級: **{level} - {name}**")
        
        with col2:
            if st.button("➕ 加入清單", use_container_width=True):
                # 檢查是否已存在
                existing = [item for item in st.session_state.hunt_list if item['ticker'] == current_ticker]
                
                if existing:
                    st.warning(f"⚠️ {current_ticker} 已在清單中")
                else:
                    # 添加到清單
                    st.session_state.hunt_list.append({
                        'ticker': current_ticker,
                        'rating_level': level,
                        'rating_name': name,
                        'color': color,
                        'angle_3m': geo['3M']['angle'],
                        'acceleration': geo['acceleration']
                    })
                    st.success(f"✅ {current_ticker} 已加入獵殺清單")
                    st.rerun()
        
        # 顯示獵殺清單
        if st.session_state.hunt_list:
            st.markdown("#### 🎯 當前清單")
            
            df_hunt = pd.DataFrame(st.session_state.hunt_list)
            
            # 格式化顯示
            df_hunt_display = df_hunt[['ticker', 'rating_level', 'rating_name', 'angle_3m', 'acceleration']].copy()
            df_hunt_display.columns = ['標的代號', '評級', '評級名稱', '3M角度', '加速度']
            
            st.dataframe(
                df_hunt_display,
                use_container_width=True,
                hide_index=True
            )
            
            # 操作按鈕
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 匯出清單", use_container_width=True):
                    csv = df_hunt.to_csv(index=False)
                    st.download_button(
                        label="⬇️ 下載 CSV",
                        data=csv,
                        file_name="titan_hunt_list.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("🔄 重新掃描", use_container_width=True):
                    st.info("功能開發中...")
            
            with col3:
                if st.button("🗑️ 清空清單", use_container_width=True):
                    st.session_state.hunt_list = []
                    st.success("✅ 清單已清空")
                    st.rerun()
        
        else:
            st.info("📝 獵殺清單為空，開始添加標的吧！")
        
        st.divider()
        
        # ==========================================
        # 信評解讀
        # ==========================================
        
        with st.expander("📚 22 階信評系統說明"):
            st.markdown("""
            ### 🏆 泰坦信評系統 (22 階)
            
            **神級 (SSS-AAA)**:
            - **SSS - Titan**: 全週期超過 45°，神級標的
            - **AAA - Dominator**: 短期加速向上，完美趨勢
            - **Phoenix**: 浴火重生，長空短多逆轉
            - **Launchpad**: 發射台，線性度極高
            
            **優質 (AA)**:
            - **AA+**: 一年期強勢上攻
            - **AA**: 中短期穩定上升
            - **AA-**: 趨勢健康向上
            
            **良好 (A-BBB)**:
            - **A+/A**: 溫和至弱多頭
            - **BBB+/BBB/BBB-**: 中性區間
            
            **警示 (Divergence)**:
            - 價格創高但動能衰竭
            
            **風險 (BB-D)**:
            - **BB**: 弱至強空
            - **B**: 重度空至蕭條
            - **C/D**: 結構衰退至崩盤
            
            **特殊 (Reversal)**:
            - 觸底反彈，V 型反轉
            """)
