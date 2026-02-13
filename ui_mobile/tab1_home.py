# ui_mobile/tab1_home.py
# Titan SOP V100.0 - Mobile Tab 1: Tinder 風格滑動介面
# 功能：一次顯示一張卡片、左滑跳過/右滑鎖定

import streamlit as st
import pandas as pd
from core_logic import compute_7d_geometry, titan_rating_system
from utils_ui import get_rating_color


def render():
    """
    渲染 Tinder 風格首頁
    
    功能：
    - 一次顯示一張卡片
    - 滑動操作（Pass/Lock）
    - 顯示 22 階信評
    """
    st.markdown("### 🏠 獵殺模式")
    st.caption("左滑跳過 · 右滑鎖定")
    
    # ==========================================
    # 檢查數據
    # ==========================================
    
    df = st.session_state.get('df')
    
    if df is None or df.empty:
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); border-radius: 20px; margin: 20px 0;">
                <div style="font-size: 80px; margin-bottom: 20px;">📱</div>
                <h2 style="color: #FFD700; margin-bottom: 20px;">請先上傳數據</h2>
                <p style="color: #AAAAAA; font-size: 16px; line-height: 1.6;">
                    移動版不支援直接上傳<br>
                    請切換到桌面版上傳 CB 清單<br>
                    然後再返回移動版
                </p>
                <div style="margin-top: 30px;">
                    <p style="color: #666; font-size: 14px;">💡 提示：點擊右下角「設定」切換模式</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # ==========================================
    # 獲取當前卡片
    # ==========================================
    
    current_index = st.session_state.get('current_index', 0)
    
    # 檢查是否已經看完所有卡片
    if current_index >= len(df):
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); border-radius: 20px; margin: 20px 0;">
                <div style="font-size: 80px; margin-bottom: 20px;">🎉</div>
                <h2 style="color: #00FF00; margin-bottom: 20px;">已掃描完畢！</h2>
                <p style="color: #AAAAAA; font-size: 16px; line-height: 1.6;">
                    已查看所有 CB 標的<br>
                    共鎖定 {} 檔
                </p>
            </div>
            """.format(len(st.session_state.watchlist)),
            unsafe_allow_html=True
        )
        
        if st.button("🔄 重新開始", use_container_width=True, type="primary"):
            st.session_state.current_index = 0
            st.rerun()
        
        return
    
    # 獲取當前行
    current_row = df.iloc[current_index]
    
    code = current_row.get('code', 'N/A')
    name = current_row.get('name', 'N/A')
    stock_code = current_row.get('stock_code', 'N/A')
    close = current_row.get('close', 0)
    
    # ==========================================
    # 計算 7D 幾何與信評
    # ==========================================
    
    with st.spinner("📐 計算中..."):
        try:
            geo_data = compute_7d_geometry(str(stock_code))
            
            if geo_data:
                rating_info = titan_rating_system(geo_data)
                rating_level, rating_name, rating_desc, rating_color = rating_info
                
                angle_3m = geo_data['3M']['angle']
                acceleration = geo_data['acceleration']
                r2_3m = geo_data['3M']['r2']
            else:
                rating_level = "N/A"
                rating_name = "無數據"
                rating_desc = "無法計算"
                rating_color = "#808080"
                angle_3m = 0
                acceleration = 0
                r2_3m = 0
        
        except Exception as e:
            rating_level = "ERROR"
            rating_name = "計算失敗"
            rating_desc = str(e)
            rating_color = "#FF0000"
            angle_3m = 0
            acceleration = 0
            r2_3m = 0
    
    # ==========================================
    # 顯示卡片
    # ==========================================
    
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {rating_color} 0%, #000000 100%); 
                    border-radius: 24px; 
                    padding: 40px 20px; 
                    text-align: center; 
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
                    margin: 20px 0;">
            
            <!-- CB 代號 -->
            <div style="font-size: 72px; 
                        font-weight: 900; 
                        color: #FFFFFF; 
                        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
                        margin-bottom: 10px;">
                {code}
            </div>
            
            <!-- CB 名稱 -->
            <div style="font-size: 24px; 
                        color: #FFFFFF; 
                        margin-bottom: 20px;
                        opacity: 0.9;">
                {name}
            </div>
            
            <!-- 分隔線 -->
            <div style="height: 2px; 
                        background: rgba(255, 255, 255, 0.2); 
                        margin: 20px auto; 
                        width: 80%;"></div>
            
            <!-- 信評等級 -->
            <div style="font-size: 48px; 
                        font-weight: bold; 
                        color: #FFFFFF; 
                        margin: 20px 0;
                        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);">
                {rating_level}
            </div>
            
            <!-- 信評名稱 -->
            <div style="font-size: 20px; 
                        color: #FFFFFF; 
                        margin-bottom: 30px;
                        opacity: 0.8;">
                {rating_name}
            </div>
            
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # 關鍵指標
    # ==========================================
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "CB 市價",
            f"{close:.2f}",
            help="可轉債市價"
        )
    
    with col2:
        angle_color = "normal" if angle_3m > 0 else "inverse"
        st.metric(
            "3M 角度",
            f"{angle_3m:+.1f}°",
            help="3 個月趨勢角度",
            delta_color=angle_color
        )
    
    with col3:
        accel_color = "normal" if acceleration > 0 else "inverse"
        st.metric(
            "加速度",
            f"{acceleration:+.1f}°",
            help="3M - 1Y 角度差",
            delta_color=accel_color
        )
    
    st.divider()
    
    # ==========================================
    # 詳細資訊
    # ==========================================
    
    with st.expander("📊 查看詳細資訊"):
        st.markdown(f"""
        **CB 資訊**:
        - CB 代號: {code}
        - CB 名稱: {name}
        - 標的代號: {stock_code}
        - CB 市價: {close}
        
        **信評資訊**:
        - 評級等級: {rating_level}
        - 評級名稱: {rating_name}
        - 評級描述: {rating_desc}
        
        **幾何指標**:
        - 3M 角度: {angle_3m:.2f}°
        - 加速度: {acceleration:.2f}°
        - R² (線性度): {r2_3m:.4f}
        """)
    
    st.divider()
    
    # ==========================================
    # 滑動操作按鈕
    # ==========================================
    
    st.markdown("### 🎯 操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pass 按鈕
        if st.button(
            "❌ 跳過", 
            use_container_width=True, 
            type="secondary",
            key="pass_btn"
        ):
            # 移動到下一張卡片
            st.session_state.current_index += 1
            st.success("✅ 已跳過")
            st.rerun()
    
    with col2:
        # Lock 按鈕
        if st.button(
            "✅ 鎖定", 
            use_container_width=True, 
            type="primary",
            key="lock_btn"
        ):
            # 檢查是否已在監控清單
            if code not in [item['code'] for item in st.session_state.watchlist]:
                # 加入監控清單
                st.session_state.watchlist.append({
                    'code': code,
                    'name': name,
                    'stock_code': stock_code,
                    'close': close,
                    'rating_level': rating_level,
                    'rating_name': rating_name,
                    'rating_color': rating_color,
                    'angle_3m': angle_3m,
                    'acceleration': acceleration
                })
                st.success(f"✅ {code} 已加入監控清單")
            else:
                st.warning(f"⚠️ {code} 已在監控清單中")
            
            # 移動到下一張卡片
            st.session_state.current_index += 1
            st.rerun()
    
    # ==========================================
    # 進度指示
    # ==========================================
    
    st.markdown("---")
    
    progress = (current_index + 1) / len(df)
    
    st.progress(progress)
    
    st.caption(f"📍 進度：{current_index + 1} / {len(df)} ({progress*100:.0f}%)")
    
    # 監控清單數量
    if st.session_state.watchlist:
        st.caption(f"🔒 已鎖定：{len(st.session_state.watchlist)} 檔")
