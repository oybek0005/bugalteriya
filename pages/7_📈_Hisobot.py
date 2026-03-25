import streamlit as st
from datetime import date, timedelta
from database import init_db, get_firms
from config import TX_TYPES
from export import build_report_df, export_to_excel
from styles import page_header, section_header, info_banner, stat_card, icon

init_db()

page_header("Hisobot", "bar-chart", "Ma'lumotlarni filtrlash va Excel formatida yuklash")

# Filters
section_header("Filtrlar", "filter")
col1, col2, col3, col4 = st.columns(4)

firms = get_firms()
with col1:
    firm_options = [None] + [f["id"] for f in firms]
    firm_labels = ["Barcha firmalar"] + [f["name"] for f in firms]
    selected_firm_idx = st.selectbox("Firma", range(len(firm_options)),
                                     format_func=lambda i: firm_labels[i])
    firm_id = firm_options[selected_firm_idx]

with col2:
    tx_options = [None] + list(TX_TYPES.keys())
    tx_labels = ["Barcha turlar"] + list(TX_TYPES.values())
    selected_tx_idx = st.selectbox("Operatsiya turi", range(len(tx_options)),
                                    format_func=lambda i: tx_labels[i])
    tx_type = tx_options[selected_tx_idx]

with col3:
    date_from = st.date_input("Boshlanish", value=date.today() - timedelta(days=30))

with col4:
    date_to = st.date_input("Tugash", value=date.today())

# Build report
df = build_report_df(firm_id=firm_id, date_from=date_from, date_to=date_to, tx_type=tx_type)

if not df.empty:
    # Stats
    cols = st.columns(3)
    with cols[0]:
        st.markdown(stat_card("Jami yozuvlar", str(len(df)), "file-text", "blue"), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(stat_card("Jami miqdor", f"{df['Miqdor'].sum():,.0f}", "package", "green"), unsafe_allow_html=True)
    with cols[2]:
        st.markdown(stat_card("Firmalar", str(df['Firma'].nunique()), "building", "purple"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    section_header("Ma'lumotlar jadvali", "file-text")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Summary
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        section_header("Turi bo'yicha jami", "bar-chart")
        summary = df.groupby("Turi")["Miqdor"].sum().reset_index()
        summary.columns = ["Turi", "Jami miqdor"]
        st.dataframe(summary, use_container_width=True, hide_index=True)

    with col_s2:
        section_header("Firma bo'yicha jami", "building")
        firm_summary = df.groupby("Firma")["Miqdor"].sum().reset_index()
        firm_summary.columns = ["Firma", "Jami miqdor"]
        st.dataframe(firm_summary, use_container_width=True, hide_index=True)

    # Export
    st.markdown("<br>", unsafe_allow_html=True)
    excel_bytes = export_to_excel(df)
    st.download_button(
        label=f"  Excel yuklash  ({len(df)} yozuv)",
        data=excel_bytes,
        file_name=f"hisobot_{date_from}_{date_to}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary",
    )
else:
    info_banner("Tanlangan filtrlar bo'yicha ma'lumot topilmadi.", "alert-circle")
