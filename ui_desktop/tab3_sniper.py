# ui_desktop/tab3_sniper.py
# Titan SOP V100.0 - Tab 3: 單兵狙擊
# 功能：K 線圖、技術指標、回測引擎

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data_engine import download_stock_price, run_fast_backtest


def render():
    """
    渲染單兵狙擊 Tab
    
    功能：
    - K 線圖表
    - 回測引擎
    - 績效指標
    """
    st.subheader("🎯 單兵狙擊")
    st.caption("技術圖表 + 極速回測引擎")
    
    # ==========================================
    # 標的選擇
    # ==========================================
    
    st.markdown("### 🎯 選擇標的")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "輸入標的代號 (台股/美股)",
            value=st.session_state.get('selected_ticker', '2330'),
            placeholder="例如：2330, NVDA, AAPL",
            key="sniper_ticker"
        )
        
        # 更新 session_state
        if ticker:
            st.session_state.selected_ticker = ticker
    
    with col2:
        period = st.selectbox(
            "時間範圍",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=3,
            key="sniper_period"
        )
    
    if not ticker:
        st.info("👆 請輸入標的代號開始分析")
        return
    
    # ==========================================
    # 下載數據
    # ==========================================
    
    with st.spinner(f"正在下載 {ticker} 的數據..."):
        try:
            df_price = download_stock_price(ticker, period=period)
            
            if df_price is None or df_price.empty:
                st.error(f"❌ 無法獲取 {ticker} 的數據。請檢查代號是否正確。")
                return
            
        except Exception as e:
            st.error(f"❌ 數據下載失敗: {e}")
            return
    
    # 顯示基本資訊
    current_price = df_price['Close'].iloc[-1]
    price_change = df_price['Close'].iloc[-1] - df_price['Close'].iloc[0]
    price_change_pct = (price_change / df_price['Close'].iloc[0]) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("當前價格", f"${current_price:.2f}")
    
    with col2:
        st.metric(
            "漲跌幅",
            f"{price_change_pct:+.2f}%",
            f"${price_change:+.2f}"
        )
    
    with col3:
        high_price = df_price['High'].max()
        st.metric("期間最高", f"${high_price:.2f}")
    
    with col4:
        low_price = df_price['Low'].min()
        st.metric("期間最低", f"${low_price:.2f}")
    
    st.divider()
    
    # ==========================================
    # K 線圖
    # ==========================================
    
    st.markdown("### 📈 K 線圖")
    
    # 計算移動平均線
    df_price['MA20'] = df_price['Close'].rolling(window=20).mean()
    df_price['MA60'] = df_price['Close'].rolling(window=60).mean()
    
    # 創建 K 線圖
    fig = go.Figure()
    
    # K 線
    fig.add_trace(go.Candlestick(
        x=df_price.index,
        open=df_price['Open'],
        high=df_price['High'],
        low=df_price['Low'],
        close=df_price['Close'],
        name='K線',
        increasing_line_color='#00FF00',
        decreasing_line_color='#FF0000'
    ))
    
    # MA20
    fig.add_trace(go.Scatter(
        x=df_price.index,
        y=df_price['MA20'],
        mode='lines',
        name='MA20',
        line=dict(color='#FFD700', width=1.5)
    ))
    
    # MA60
    fig.add_trace(go.Scatter(
        x=df_price.index,
        y=df_price['MA60'],
        mode='lines',
        name='MA60',
        line=dict(color='#00CED1', width=1.5)
    ))
    
    fig.update_layout(
        height=600,
        template="plotly_dark",
        xaxis_title="日期",
        yaxis_title="價格 ($)",
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ==========================================
    # 成交量
    # ==========================================
    
    st.markdown("#### 📊 成交量")
    
    fig_vol = go.Figure()
    
    # 成交量柱狀圖
    colors = ['#00FF00' if df_price['Close'].iloc[i] >= df_price['Open'].iloc[i] 
              else '#FF0000' for i in range(len(df_price))]
    
    fig_vol.add_trace(go.Bar(
        x=df_price.index,
        y=df_price['Volume'],
        name='成交量',
        marker_color=colors,
        showlegend=False
    ))
    
    fig_vol.update_layout(
        height=200,
        template="plotly_dark",
        xaxis_title="",
        yaxis_title="成交量",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_vol, use_container_width=True)
    
    st.divider()
    
    # ==========================================
    # 回測引擎
    # ==========================================
    
    st.markdown("### ⚡ 極速回測引擎")
    st.caption("策略：收盤價 > 20MA 時買入")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        backtest_start = st.date_input(
            "回測起始日期",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now(),
            key="backtest_start"
        )
    
    with col2:
        st.write("")  # 對齊用
        st.write("")
        run_backtest = st.button("🚀 執行回測", use_container_width=True, type="primary")
    
    if run_backtest:
        with st.spinner("正在執行回測..."):
            try:
                result = run_fast_backtest(
                    ticker=ticker,
                    start_date=backtest_start.strftime('%Y-%m-%d'),
                    initial_capital=1000000
                )
                
                if result is None:
                    st.error("❌ 回測失敗，請檢查數據")
                    return
                
                # 顯示結果
                st.success("✅ 回測完成！")
                
                # 績效指標
                st.markdown("#### 📊 績效指標")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "年化報酬率 (CAGR)",
                        f"{result['cagr']*100:.2f}%",
                        help="複合年化成長率"
                    )
                
                with col2:
                    st.metric(
                        "夏普比率",
                        f"{result['sharpe_ratio']:.2f}",
                        help="風險調整後報酬"
                    )
                
                with col3:
                    st.metric(
                        "最大回撤",
                        f"{result['max_drawdown']*100:.2f}%",
                        help="最大虧損幅度",
                        delta_color="inverse"
                    )
                
                st.divider()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "總報酬率",
                        f"{result['total_return']*100:.2f}%"
                    )
                
                with col2:
                    st.metric(
                        "勝率",
                        f"{result['win_rate']*100:.2f}%"
                    )
                
                with col3:
                    st.metric(
                        "Kelly 倉位",
                        f"{result['kelly']*100:.2f}%",
                        help="凱利公式建議倉位"
                    )
                
                # 交易統計
                st.markdown("#### 📈 交易統計")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**總交易次數**: {result['num_trades']}")
                    st.write(f"**盈虧比**: {result['profit_factor']:.2f}")
                
                with col2:
                    final_equity = result['total_return'] * 1000000 + 1000000
                    st.write(f"**初始資金**: $1,000,000")
                    st.write(f"**最終資金**: ${final_equity:,.0f}")
                
                # 績效評估
                st.markdown("#### 🎯 績效評估")
                
                if result['sharpe_ratio'] > 1.5:
                    st.success("✅ **優秀**: 夏普比率 > 1.5，風險調整後報酬優異")
                elif result['sharpe_ratio'] > 1.0:
                    st.info("ℹ️ **良好**: 夏普比率 > 1.0，表現穩健")
                elif result['sharpe_ratio'] > 0.5:
                    st.warning("⚠️ **普通**: 夏普比率 > 0.5，仍需優化")
                else:
                    st.error("❌ **不佳**: 夏普比率 < 0.5，策略需改進")
                
                if result['max_drawdown'] < -0.3:
                    st.warning(f"⚠️ 最大回撤 {result['max_drawdown']*100:.1f}% 較大，需注意風控")
                
                if result['kelly'] > 0.25:
                    st.warning("⚠️ Kelly 倉位 > 25%，建議降低槓桿")
                
            except Exception as e:
                st.error(f"❌ 回測執行失敗: {e}")
                st.code(str(e))
    
    # ==========================================
    # 技術指標說明
    # ==========================================
    
    with st.expander("📚 技術指標說明"):
        st.markdown("""
        ### MA (移動平均線)
        - **MA20**: 20 日移動平均，代表短期趨勢
        - **MA60**: 60 日移動平均，代表中期趨勢
        - **黃金交叉**: MA20 向上突破 MA60，看漲信號
        - **死亡交叉**: MA20 向下跌破 MA60，看跌信號
        
        ### 回測指標
        - **CAGR**: 複合年化成長率，衡量長期報酬
        - **夏普比率**: 風險調整後報酬，> 1 為良好
        - **最大回撤**: 最大虧損幅度，< -30% 需警惕
        - **凱利公式**: 最佳倉位建議，通常 < 25%
        """)
