import streamlit as st
import pandas as pd
from database import init_db, get_firms, get_firm_balances
from styles import page_header, section_header, info_banner, stat_card

init_db()

page_header("Firma Qoldig'i", "building", "Har bir firmadagi xomashyo va mahsulotlar qoldig'i")

firms = get_firms()

if not firms:
    info_banner("Hali firmalar qo'shilmagan.", "alert-circle")
else:
    firm_options = [{"id": None, "name": "Barcha firmalar"}] + firms
    selected = st.selectbox(
        "Firma tanlang",
        firm_options,
        format_func=lambda f: f["name"],
    )

    firm_id = selected["id"]
    balances = get_firm_balances(firm_id=firm_id)

    if balances:
        df = pd.DataFrame(balances)
        display_df = df[["firm_name", "item_name", "item_type", "quantity", "item_unit"]].copy()
        display_df.columns = ["Firma", "Mahsulot", "Turi", "Miqdor", "Birlik"]

        type_map = {"xomashyo": "Xomashyo", "tayyor": "Tayyor"}
        display_df["Turi"] = display_df["Turi"].map(type_map)

        # Summary stats
        total_items = len(display_df)
        total_qty = display_df["Miqdor"].sum()
        unique_firms = display_df["Firma"].nunique()

        cols = st.columns(3)
        with cols[0]:
            st.markdown(stat_card("Mahsulot turlari", str(total_items), "package", "blue"), unsafe_allow_html=True)
        with cols[1]:
            st.markdown(stat_card("Jami miqdor", f"{total_qty:,.0f}", "scale", "orange"), unsafe_allow_html=True)
        with cols[2]:
            st.markdown(stat_card("Firmalar soni", str(unique_firms), "building", "purple"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        section_header("Batafsil ro'yxat", "file-text")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Miqdor": st.column_config.NumberColumn(format="%.2f"),
            },
        )

        section_header("Firma bo'yicha jami", "bar-chart")
        summary = display_df.groupby("Firma").agg(
            **{"Jami miqdor": ("Miqdor", "sum"),
               "Mahsulot turlari": ("Mahsulot", "count")}
        ).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        info_banner("Tanlangan firma uchun qoldiq mavjud emas.", "alert-circle")
