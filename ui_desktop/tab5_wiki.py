# ui_desktop/tab5_wiki.py
# Titan V100.0 - Desktop UI: Encyclopedia & Intel
# 狀態: 桌面版戰略百科

import streamlit as st

def render(df, intel_engine, kb):
    """Renders the Encyclopedia & Intel tab."""
    st.header("📚 戰略百科 (Encyclopedia & Intel)")

    with st.expander("5.1 SOP 戰略百科"):
        rules = kb.get_all_rules_for_ui()
        st.text_area("進出場紀律", rules['entry_exit']['entry'], height=200)
        st.text_area("特殊心法", "\n---\n".join(rules['special_tactics']), height=200)

    with st.expander("5.2 情報獵殺分析結果"):
        intel_files = st.session_state.get('intel_files', [])
        if not intel_files:
            st.info("請於左側上傳情報文件以進行分析。")
        else:
            for file in intel_files:
                st.write(f"分析報告: {file.name}")
                # Analysis logic would be here.