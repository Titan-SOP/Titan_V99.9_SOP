# ui_desktop/tab2_radar.py
# Titan SOP V100.0 - Tab 2: 獵殺雷達
# 功能：CB 全景掃描、智慧篩選、即時排序

import streamlit as st
import pandas as pd
import numpy as np


def render():
    """
    渲染獵殺雷達 Tab
    
    功能：
    - 顯示完整 CB 清單
    - 智慧搜索與篩選
    - 可點擊選擇標的
    """
    st.subheader("🏹 獵殺雷達")
    st.caption("CB 全景掃描 - 一鍵鎖定優質標的")
    
    # 獲取數據
    df = st.session_state.get('df', pd.DataFrame())
    
    if df.empty:
        st.warning("⚠️ 請先在側邊欄上傳 CB 清單")
        return
    
    # ==========================================
    # 搜索與篩選
    # ==========================================
    
    st.markdown("### 🔍 智慧搜索")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "搜索 CB 代號或名稱",
            placeholder="例如：17897、信邦、鈊象",
            label_visibility="collapsed"
        )
    
    with col2:
        sort_by = st.selectbox(
            "排序依據",
            ["無排序", "市價 (高到低)", "市價 (低到高)", "代號"],
            label_visibility="collapsed"
        )
    
    with col3:
        show_count = st.number_input(
            "顯示筆數",
            min_value=10,
            max_value=len(df),
            value=min(50, len(df)),
            step=10,
            label_visibility="collapsed"
        )
    
    # ==========================================
    # 數據處理
    # ==========================================
    
    # 複製數據避免修改原始 DataFrame
    df_display = df.copy()
    
    # 搜索過濾
    if search_query:
        mask = (
            df_display['code'].astype(str).str.contains(search_query, case=False, na=False) |
            df_display['name'].astype(str).str.contains(search_query, case=False, na=False)
        )
        df_display = df_display[mask]
        
        if df_display.empty:
            st.warning(f"🔍 未找到符合 '{search_query}' 的結果")
            return
    
    # 排序
    if sort_by == "市價 (高到低)":
        df_display = df_display.sort_values('close', ascending=False)
    elif sort_by == "市價 (低到高)":
        df_display = df_display.sort_values('close', ascending=True)
    elif sort_by == "代號":
        df_display = df_display.sort_values('code')
    
    # 限制顯示筆數
    df_display = df_display.head(show_count)
    
    # ==========================================
    # 統計面板
    # ==========================================
    
    st.markdown("### 📊 統計面板")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("總數量", f"{len(df)} 檔")
    
    with col2:
        if 'close' in df.columns:
            avg_price = df['close'].mean()
            st.metric("平均市價", f"{avg_price:.2f}")
    
    with col3:
        if 'close' in df.columns:
            max_price = df['close'].max()
            st.metric("最高市價", f"{max_price:.2f}")
    
    with col4:
        if 'close' in df.columns:
            min_price = df['close'].min()
            st.metric("最低市價", f"{min_price:.2f}")
    
    st.divider()
    
    # ==========================================
    # 數據表格
    # ==========================================
    
    st.markdown(f"### 📋 CB 清單 (顯示 {len(df_display)} / {len(df)} 檔)")
    
    # 準備顯示欄位
    display_columns = ['code', 'name', 'stock_code', 'close']
    
    # 檢查可選欄位
    optional_columns = {
        'conversion_price': '轉換價',
        'underlying_price': '標的股價',
        'converted_ratio': '已轉換比例',
        'avg_volume': '均量'
    }
    
    for col_name, col_label in optional_columns.items():
        if col_name in df_display.columns:
            display_columns.append(col_name)
    
    # 重命名欄位（中文顯示）
    column_names = {
        'code': 'CB代號',
        'name': 'CB名稱',
        'stock_code': '標的代號',
        'close': 'CB市價',
        'conversion_price': '轉換價',
        'underlying_price': '標的股價',
        'converted_ratio': '已轉換比例',
        'avg_volume': '均量'
    }
    
    df_show = df_display[display_columns].copy()
    df_show.rename(columns=column_names, inplace=True)
    
    # 格式化數值欄位
    if 'CB市價' in df_show.columns:
        df_show['CB市價'] = df_show['CB市價'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    
    if '轉換價' in df_show.columns:
        df_show['轉換價'] = df_show['轉換價'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    
    if '標的股價' in df_show.columns:
        df_show['標的股價'] = df_show['標的股價'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    
    if '已轉換比例' in df_show.columns:
        df_show['已轉換比例'] = df_show['已轉換比例'].apply(
            lambda x: f"{x*100:.2f}%" if pd.notna(x) and x != 0 else "N/A"
        )
    
    if '均量' in df_show.columns:
        df_show['均量'] = df_show['均量'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
    
    # 顯示表格
    st.dataframe(
        df_show,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # ==========================================
    # 選擇標的
    # ==========================================
    
    st.divider()
    
    st.markdown("### 🎯 選擇標的進行分析")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 創建選項列表
        options = []
        for _, row in df_display.iterrows():
            code = row.get('code', 'N/A')
            name = row.get('name', 'N/A')
            stock_code = row.get('stock_code', 'N/A')
            options.append(f"{code} - {name} (標的: {stock_code})")
        
        selected = st.selectbox(
            "選擇 CB",
            options,
            key="radar_select"
        )
    
    with col2:
        st.write("")  # 對齊用
        st.write("")
        if st.button("🎯 進入狙擊模式", use_container_width=True, type="primary"):
            # 解析選擇的標的代號
            if selected:
                selected_code = selected.split(' - ')[0]
                
                # 從 DataFrame 中找到對應的 stock_code
                matched_row = df_display[df_display['code'] == selected_code]
                
                if not matched_row.empty:
                    stock_code = matched_row.iloc[0]['stock_code']
                    st.session_state.selected_ticker = str(stock_code)
                    st.success(f"✅ 已選擇標的: {stock_code}")
                    st.info("💡 請切換到「單兵狙擊」Tab 查看詳細分析")
    
    # ==========================================
    # 快速統計
    # ==========================================
    
    with st.expander("📊 進階統計"):
        if 'close' in df.columns:
            st.markdown("#### 市價分佈")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 價格區間統計
                bins = [0, 100, 110, 120, 130, float('inf')]
                labels = ['< 100', '100-110', '110-120', '120-130', '> 130']
                
                df['price_range'] = pd.cut(df['close'], bins=bins, labels=labels)
                price_dist = df['price_range'].value_counts().sort_index()
                
                st.markdown("**價格區間分佈**:")
                for idx, count in price_dist.items():
                    st.write(f"- {idx}: {count} 檔")
            
            with col2:
                # 基本統計
                st.markdown("**價格統計**:")
                st.write(f"- 中位數: {df['close'].median():.2f}")
                st.write(f"- 標準差: {df['close'].std():.2f}")
                st.write(f"- 25% 分位: {df['close'].quantile(0.25):.2f}")
                st.write(f"- 75% 分位: {df['close'].quantile(0.75):.2f}")
