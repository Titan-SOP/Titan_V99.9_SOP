# ui_mobile/tab3_ai.py
# Titan SOP V100.0 - Mobile Tab 3: AI 聊天介面
# 功能：與 TitanAgentCouncil 聊天，獲取簡短分析

import streamlit as st
from core_logic import (
    TitanAgentCouncil, 
    TitanIntelAgency,
    compute_7d_geometry, 
    titan_rating_system
)
from data_engine import download_stock_price


def render():
    """
    渲染 AI 聊天介面
    
    功能：
    - 聊天式 UI
    - 快速 AI 分析（移動版簡化）
    """
    st.markdown("### 🤖 AI 助手")
    st.caption("與 Titan AI 對話")
    
    # ==========================================
    # 檢查 API Key
    # ==========================================
    
    api_key = st.session_state.get('api_key', '')
    
    if not api_key:
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%); border-radius: 20px; margin: 20px 0;">
                <div style="font-size: 80px; margin-bottom: 20px;">🔑</div>
                <h2 style="color: #FFD700; margin-bottom: 20px;">需要 API Key</h2>
                <p style="color: #AAAAAA; font-size: 16px; line-height: 1.6;">
                    請前往「設定」頁面<br>
                    輸入 Gemini API Key<br>
                    以啟用 AI 功能
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # ==========================================
    # 初始化聊天歷史
    # ==========================================
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # ==========================================
    # 快速選擇標的
    # ==========================================
    
    st.markdown("#### 🎯 選擇標的")
    
    # 從監控清單選擇
    watchlist = st.session_state.get('watchlist', [])
    
    if watchlist:
        # 創建選項
        options = [f"{item['code']} - {item['name']}" for item in watchlist]
        
        selected = st.selectbox(
            "從監控清單選擇",
            options,
            key="ai_ticker_select"
        )
        
        # 解析選擇
        if selected:
            selected_code = selected.split(' - ')[0]
            
            # 找到對應的 stock_code
            matched_item = next((item for item in watchlist if item['code'] == selected_code), None)
            
            if matched_item:
                ticker = matched_item['stock_code']
    
    else:
        # 手動輸入
        ticker = st.text_input(
            "或手動輸入標的代號",
            placeholder="例如：2330, NVDA",
            key="ai_ticker_input"
        )
    
    # ==========================================
    # 分析按鈕
    # ==========================================
    
    if st.button("🚀 分析標的", use_container_width=True, type="primary"):
        
        if not ticker:
            st.error("❌ 請選擇或輸入標的代號")
            return
        
        # 顯示載入動畫
        with st.spinner(f"🤖 AI 正在分析 {ticker}..."):
            
            try:
                # Step 1: 計算 7D 幾何
                geo_data = compute_7d_geometry(ticker)
                
                if geo_data is None:
                    st.error(f"❌ 無法獲取 {ticker} 的數據")
                    return
                
                # Step 2: 計算信評
                rating_info = titan_rating_system(geo_data)
                
                # Step 3: 獲取當前價格
                df_price = download_stock_price(ticker, period='1mo')
                
                if df_price is not None and not df_price.empty:
                    current_price = df_price['Close'].iloc[-1]
                else:
                    current_price = 100.0
                
                # Step 4: 生成移動版簡化 prompt
                simplified_prompt = generate_mobile_prompt(ticker, current_price, geo_data, rating_info)
                
                # Step 5: 調用 AI
                council = TitanAgentCouncil(api_key=api_key)
                
                # 使用簡化的直接調用
                try:
                    response = council.model.generate_content(simplified_prompt)
                    ai_response = response.text
                    
                    # 添加到聊天歷史
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': f"分析 {ticker}"
                    })
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': ai_response
                    })
                    
                    st.success("✅ 分析完成")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ AI 調用失敗: {e}")
            
            except Exception as e:
                st.error(f"❌ 分析失敗: {e}")
    
    st.divider()
    
    # ==========================================
    # 顯示聊天歷史
    # ==========================================
    
    st.markdown("#### 💬 對話記錄")
    
    if not st.session_state.chat_history:
        st.info("📝 暫無對話記錄。選擇標的並點擊「分析標的」開始。")
    else:
        # 顯示聊天訊息
        for message in st.session_state.chat_history:
            role = message['role']
            content = message['content']
            
            if role == 'user':
                # 用戶訊息（右側，金色）
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #5F4E1E 0%, #806A2A 100%); 
                                border-radius: 16px; 
                                padding: 15px 20px; 
                                margin: 10px 0 10px 20%; 
                                text-align: right;
                                border-bottom-right-radius: 4px;">
                        <div style="font-size: 12px; color: #FFD700; margin-bottom: 5px;">👤 你</div>
                        <div style="color: #FFFFFF; line-height: 1.5;">{content}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            else:
                # AI 訊息（左側，藍色）
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #1E3A5F 0%, #2A5280 100%); 
                                border-radius: 16px; 
                                padding: 15px 20px; 
                                margin: 10px 20% 10px 0; 
                                text-align: left;
                                border-bottom-left-radius: 4px;">
                        <div style="font-size: 12px; color: #00CED1; margin-bottom: 5px;">🤖 Titan AI</div>
                        <div style="color: #FFFFFF; line-height: 1.5; white-space: pre-wrap;">{content}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # ==========================================
    # 清除按鈕
    # ==========================================
    
    if st.session_state.chat_history:
        st.divider()
        
        if st.button("🗑️ 清除對話", use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ 對話已清除")
            st.rerun()


def generate_mobile_prompt(ticker: str, price: float, geo_data: dict, rating_info: tuple) -> str:
    """
    生成移動版簡化 prompt
    
    Args:
        ticker: 標的代號
        price: 當前價格
        geo_data: 7D 幾何數據
        rating_info: 信評資訊
    
    Returns:
        str: 簡化的 prompt
    """
    level, name, desc, color = rating_info
    
    # 幾何數據摘要
    geo_summary = f"""
標的: {ticker}
現價: ${price:.2f}

7D 幾何數據:
- 35Y 角度: {geo_data['35Y']['angle']}°
- 10Y 角度: {geo_data['10Y']['angle']}°
- 1Y 角度: {geo_data['1Y']['angle']}°
- 3M 角度: {geo_data['3M']['angle']}°
- 加速度: {geo_data['acceleration']}°

泰坦信評: {level} - {name}
評級描述: {desc}
"""
    
    prompt = f"""
# Titan AI 移動版 - 快速分析

{geo_summary}

請以 **300 字以內** 提供快速分析，包含：

1. **信評解讀** (50 字)：解釋 {level} 等級的含義

2. **趨勢判斷** (100 字)：基於 7D 幾何數據，判斷當前趨勢（多頭/空頭/盤整）

3. **操作建議** (100 字)：給出明確的操作方向（買入/觀望/賣出）與理由

4. **風險提示** (50 字)：1-2 個關鍵風險點

請使用簡潔、直白的語言，適合移動裝置閱讀。
"""
    
    return prompt
