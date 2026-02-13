# ui_desktop/tab4_decision.py
# Titan SOP V100.0 - Tab 4: 全球決策
# 功能：AI 參謀本部、五大角鬥士辯論

import streamlit as st
from core_logic import (
    TitanAgentCouncil, 
    TitanIntelAgency,
    compute_7d_geometry, 
    titan_rating_system,
    get_first_principles
)


def render():
    """
    渲染全球決策 Tab (AI War Room)
    
    功能：
    - 自動情報抓取
    - AI 五大角鬥士辯論
    - 操作指令生成
    """
    st.subheader("🚀 全球決策 - AI 戰情室")
    st.caption("五權分立角鬥士系統 × Ragnarök War Room")
    
    # ==========================================
    # 檢查 API Key
    # ==========================================
    
    api_key = st.session_state.get('api_key', '')
    
    if not api_key:
        st.warning("⚠️ 請先在側邊欄輸入 Gemini API Key 以啟用 AI 功能")
        
        st.info("""
        ### 🔑 如何獲取 API Key
        
        1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. 登入 Google 帳號
        3. 點擊 "Get API Key"
        4. 複製 API Key 並貼上到側邊欄
        
        ### 💡 AI 功能
        - 自動抓取財報、新聞
        - 五大角鬥士辯論（每位 800+ 字）
        - 最終裁決與操作指令
        """)
        return
    
    # ==========================================
    # 標的選擇
    # ==========================================
    
    st.markdown("### 🎯 選擇分析標的")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "輸入標的代號",
            value=st.session_state.get('selected_ticker', '2330'),
            placeholder="例如：2330, NVDA, AAPL",
            key="decision_ticker"
        )
    
    with col2:
        st.write("")  # 對齊用
        st.write("")
        auto_intel = st.checkbox("自動抓取情報", value=True)
    
    if not ticker:
        st.info("👆 請輸入標的代號開始分析")
        return
    
    # ==========================================
    # 情報輸入區
    # ==========================================
    
    st.markdown("### 🕵️ 實彈情報 (Insider Intel)")
    
    intel_text = ""
    
    if auto_intel:
        st.info("🤖 瓦爾基里情報引擎 - 自動抓取模式")
        
        if st.button("📡 啟動自動抓取", type="primary"):
            with st.spinner(f"正在抓取 {ticker} 的情報..."):
                try:
                    intel_agency = TitanIntelAgency()
                    intel_report = intel_agency.fetch_full_report(ticker)
                    
                    st.success("✅ 情報抓取完成")
                    
                    # 顯示情報
                    with st.expander("📄 查看完整情報", expanded=True):
                        st.markdown(intel_report)
                    
                    # 儲存到 session_state
                    st.session_state.intel_report = intel_report
                    intel_text = intel_report
                
                except Exception as e:
                    st.error(f"❌ 情報抓取失敗: {e}")
                    intel_text = ""
        
        # 如果已經抓取過，直接使用
        if 'intel_report' in st.session_state:
            intel_text = st.session_state.intel_report
    
    else:
        st.info("✍️ 手動輸入模式 - 貼上法說會/財報重點")
        
        intel_text = st.text_area(
            "貼上情報內容",
            height=200,
            placeholder="例如：Q3 營收 YoY +25%, 毛利率提升至 45%, 新產品預計 Q1 量產...",
            key="manual_intel"
        )
    
    st.divider()
    
    # ==========================================
    # 第一性原則選擇
    # ==========================================
    
    st.markdown("### 🎯 統帥第一性原則 (可選)")
    st.caption("選擇需要 AI 重點回答的問題")
    
    principles = get_first_principles()
    
    selected_principles = st.multiselect(
        "選擇第一性原則",
        principles,
        default=None,
        key="selected_principles"
    )
    
    # 統帥備註
    commander_note = st.text_area(
        "統帥額外指令 (選填)",
        placeholder="例如：重點分析現金流狀況、關注競爭對手動態...",
        height=100,
        key="commander_note"
    )
    
    st.divider()
    
    # ==========================================
    # 啟動 AI 辯論
    # ==========================================
    
    st.markdown("### ⚔️ 啟動五大角鬥士辯論")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("""
        **辯論流程**:
        1. 🤖 幾何死神 (The Quant) - 冷血數學分析
        2. 💼 內部操盤手 (The Insider) - 成長故事
        3. 🐻 大賣空獵人 (The Big Short) - 悲觀攻擊
        4. 🚀 創世紀先知 (The Visionary) - 狂熱展望
        5. ⚖️ 地球頂點 (The Apex Arbiter) - 最終裁決
        """)
    
    with col2:
        st.write("")  # 對齊用
        start_debate = st.button(
            "⚔️ 開始辯論",
            use_container_width=True,
            type="primary",
            key="start_debate"
        )
    
    if start_debate:
        # ==========================================
        # Step 1: 計算 7D 幾何數據
        # ==========================================
        
        with st.spinner("📐 正在計算 7D 幾何數據..."):
            try:
                geo_data = compute_7d_geometry(ticker)
                
                if geo_data is None:
                    st.error(f"❌ 無法獲取 {ticker} 的幾何數據")
                    return
                
                # 計算評級
                rating_info = titan_rating_system(geo_data)
                
                st.success(f"✅ 幾何數據計算完成 | 評級: {rating_info[0]} - {rating_info[1]}")
            
            except Exception as e:
                st.error(f"❌ 幾何計算失敗: {e}")
                return
        
        # ==========================================
        # Step 2: 獲取當前價格
        # ==========================================
        
        try:
            from data_engine import download_stock_price
            df_price = download_stock_price(ticker, period='1mo')
            
            if df_price is not None and not df_price.empty:
                current_price = df_price['Close'].iloc[-1]
            else:
                current_price = 100.0  # 預設值
        except:
            current_price = 100.0
        
        # ==========================================
        # Step 3: 執行 AI 辯論
        # ==========================================
        
        with st.spinner("⚔️ AI 角鬥士正在激烈辯論中... (可能需要 30-60 秒)"):
            try:
                council = TitanAgentCouncil(api_key=api_key)
                
                debate_result = council.run_debate(
                    ticker=ticker,
                    price=current_price,
                    geo_data=geo_data,
                    rating_info=rating_info,
                    intel_text=intel_text,
                    commander_note=commander_note,
                    selected_principles=selected_principles if selected_principles else None
                )
                
                st.success("✅ 辯論完成！")
                
                # ==========================================
                # 顯示辯論結果
                # ==========================================
                
                st.markdown("---")
                st.markdown("## 🏛️ 諸神黃昏戰情室 - 辯論記錄")
                st.markdown("---")
                
                # 顯示幾何數據摘要
                with st.expander("📐 戰場地形 (幾何數據)", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("35Y 角度", f"{geo_data['35Y']['angle']}°")
                        st.metric("10Y 角度", f"{geo_data['10Y']['angle']}°")
                        st.metric("5Y 角度", f"{geo_data['5Y']['angle']}°")
                    
                    with col2:
                        st.metric("3Y 角度", f"{geo_data['3Y']['angle']}°")
                        st.metric("1Y 角度", f"{geo_data['1Y']['angle']}°")
                        st.metric("6M 角度", f"{geo_data['6M']['angle']}°")
                    
                    with col3:
                        st.metric("3M 角度", f"{geo_data['3M']['angle']}°")
                        st.metric("加速度", f"{geo_data['acceleration']}°")
                        
                        phoenix_status = "🔥 觸發" if geo_data['phoenix_signal'] else "❄️ 未觸發"
                        st.metric("Phoenix 信號", phoenix_status)
                
                # 顯示信評
                st.markdown(f"""
                ### 🏆 泰坦信評
                
                <div style="background-color: {rating_info[3]}; color: #000000; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2>{rating_info[0]} - {rating_info[1]}</h2>
                    <p style="font-size: 18px; margin-top: 10px;">{rating_info[2]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # 顯示完整辯論
                st.markdown(debate_result)
                
                # 儲存結果
                st.session_state.debate_result = debate_result
                st.session_state.last_ticker = ticker
                
            except Exception as e:
                st.error(f"❌ AI 辯論失敗: {e}")
                st.code(str(e))
    
    # ==========================================
    # 顯示歷史辯論記錄
    # ==========================================
    
    if 'debate_result' in st.session_state:
        st.divider()
        
        if st.button("📄 查看上次辯論記錄"):
            st.markdown("### 📜 上次辯論記錄")
            st.caption(f"標的: {st.session_state.get('last_ticker', 'N/A')}")
            st.markdown(st.session_state.debate_result)
