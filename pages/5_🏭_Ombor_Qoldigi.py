import streamlit as st
import pandas as pd
from database import init_db, get_warehouse_stock
from styles import page_header, section_header, info_banner, stat_card

init_db()

page_header("Ombor Qoldig'i", "warehouse", "Asosiy ombordagi barcha mahsulotlar holati")

stock = get_warehouse_stock()

if stock:
    df = pd.DataFrame(stock)
    df["at_firms"] = df["total_sent"] - df["total_received"] - df["total_used"] - df["total_waste"]

    # Overall stats
    total_sent = df["total_sent"].sum()
    total_received = df["total_received"].sum()
    total_waste = df["total_waste"].sum()
    total_at_firms = df["at_firms"].sum()

    cols = st.columns(4)
    with cols[0]:
        st.markdown(stat_card("Yuborilgan", f"{total_sent:,.0f}", "send", "orange"), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(stat_card("Qaytgan", f"{total_received:,.0f}", "inbox", "green"), unsafe_allow_html=True)
    with cols[2]:
        st.markdown(stat_card("Chiqindi", f"{total_waste:,.0f}", "trash", "red"), unsafe_allow_html=True)
    with cols[3]:
        st.markdown(stat_card("Firmadagi", f"{total_at_firms:,.0f}", "package", "blue"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    display_df = df[["name", "item_type", "unit", "total_sent", "total_received",
                     "total_used", "total_waste", "at_firms"]].copy()
    display_df.columns = [
        "Mahsulot", "Turi", "Birlik",
        "Yuborilgan", "Qaytgan", "Sarflangan", "Chiqindi", "Firmadagi"
    ]

    type_map = {"xomashyo": "Xomashyo", "tayyor": "Tayyor"}
    display_df["Turi"] = display_df["Turi"].map(type_map)

    num_config = {col: st.column_config.NumberColumn(format="%.2f")
                  for col in ["Yuborilgan", "Qaytgan", "Sarflangan", "Chiqindi", "Firmadagi"]}

    tab_xom, tab_tay, tab_all = st.tabs(["Xomashyo", "Tayyor mahsulot", "Barchasi"])

    with tab_xom:
        xom_df = display_df[display_df["Turi"] == "Xomashyo"]
        if not xom_df.empty:
            section_header("Xomashyo holati", "package")
            st.dataframe(xom_df, use_container_width=True, hide_index=True, column_config=num_config)
        else:
            info_banner("Xomashyo mavjud emas", "alert-circle")

    with tab_tay:
        tay_df = display_df[display_df["Turi"] == "Tayyor"]
        if not tay_df.empty:
            section_header("Tayyor mahsulot holati", "package-check")
            st.dataframe(tay_df, use_container_width=True, hide_index=True, column_config=num_config)
        else:
            info_banner("Tayyor mahsulot mavjud emas", "alert-circle")

    with tab_all:
        section_header("Barcha mahsulotlar", "warehouse")
        st.dataframe(display_df, use_container_width=True, hide_index=True, column_config=num_config)
else:
    info_banner("Hali mahsulotlar qo'shilmagan.", "alert-circle")
