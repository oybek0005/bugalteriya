import streamlit as st
import pandas as pd
from database import init_db, get_dashboard_summary, get_firm_balances
from styles import page_header, stat_card, section_header, icon, info_banner

init_db()

page_header("Asosiy Panel", "layout-dashboard", "Ombor va firmalar bo'yicha umumiy ko'rinish")

summary = get_dashboard_summary()

# Stat cards row
cols = st.columns(4)
cards = [
    ("Jami firmalar", f"{summary['total_firms']}", "building", "purple"),
    ("Yuborilgan", f"{summary['total_out']:,.0f}", "send", "orange"),
    ("Qabul qilingan", f"{summary['total_in']:,.0f}", "inbox", "green"),
    ("Firmadagi qoldiq", f"{summary['total_at_firms']:,.0f}", "package", "blue"),
]
for i, (label, value, ic, color) in enumerate(cards):
    with cols[i]:
        st.markdown(stat_card(label, value, ic, color), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Firm balances
section_header("Firmalar bo'yicha qoldiq", "scale")

balances = get_firm_balances()
if balances:
    df = pd.DataFrame(balances)
    display_df = df[["firm_name", "item_name", "quantity", "item_unit"]].copy()
    display_df.columns = ["Firma", "Mahsulot", "Miqdor", "Birlik"]

    firm_summary = display_df.groupby("Firma")["Miqdor"].sum().reset_index()
    firm_summary.columns = ["Firma", "Jami qoldiq"]

    col_left, col_right = st.columns(2)
    with col_left:
        section_header("Firma bo'yicha jami", "building")
        st.dataframe(firm_summary, use_container_width=True, hide_index=True)

    with col_right:
        section_header("Batafsil", "file-text")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    info_banner("Hali ma'lumot mavjud emas. Xomashyo chiqimi yoki tayyor mahsulot qabul qiling.", "alert-circle")
