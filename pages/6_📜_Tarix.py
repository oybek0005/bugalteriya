import streamlit as st
import pandas as pd
from datetime import date, timedelta
from database import (
    init_db, get_firms, get_transactions,
    soft_delete_transaction, update_transaction,
)
from config import TX_TYPES
from styles import page_header, section_header, info_banner, icon, tx_badge

init_db()

page_header("Tarix", "history", "Barcha operatsiyalar tarixi — tahrirlash va o'chirish mumkin")

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
    date_from = st.date_input("Boshlanish sanasi", value=date.today() - timedelta(days=30))

with col4:
    date_to = st.date_input("Tugash sanasi", value=date.today())

show_deleted = st.checkbox("O'chirilganlarni ko'rsatish", value=False)

transactions = get_transactions(
    firm_id=firm_id,
    date_from=date_from,
    date_to=date_to,
    tx_type=tx_type,
    include_deleted=show_deleted,
)

if transactions:
    section_header(f"Natijalar — {len(transactions)} ta operatsiya", "file-text")

    for tx in transactions:
        is_deleted = tx.get("is_deleted", 0)
        badge = tx_badge(tx["tx_type"])
        deleted_mark = ' <span style="color:#ef4444; font-weight:600;">O\'CHIRILGAN</span>' if is_deleted else ""

        label = f"{tx['firm_name']} — {tx['item_name']} — {tx['quantity']:,.2f} — {tx['document_date'] or 'Sanasiz'}"

        with st.expander(label):
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                {badge} {deleted_mark}
            </div>
            """, unsafe_allow_html=True)

            col_info, col_actions = st.columns([3, 1])

            with col_info:
                st.markdown(f"""
                | | |
                |---|---|
                | **Firma** | {tx['firm_name']} |
                | **Mahsulot** | {tx['item_name']} ({tx['item_unit']}) |
                | **Miqdor** | {tx['quantity']:,.2f} |
                | **Hujjat №** | {tx['document_number'] or '—'} |
                | **Sana** | {tx['document_date'] or '—'} |
                | **Izoh** | {tx['note'] or '—'} |
                | **Manba** | {tx['source']} |
                | **Yaratilgan** | {tx['created_at']} |
                """)

            with col_actions:
                if not is_deleted:
                    with st.form(f"edit_{tx['id']}"):
                        new_qty = st.number_input("Miqdor", value=float(tx["quantity"]),
                                                   min_value=0.01, key=f"qty_{tx['id']}")
                        new_doc = st.text_input("Hujjat №", value=tx["document_number"] or "",
                                                key=f"doc_{tx['id']}")
                        new_date = st.date_input("Sana",
                                                  value=date.fromisoformat(tx["document_date"]) if tx["document_date"] else date.today(),
                                                  key=f"date_{tx['id']}")
                        new_note = st.text_input("Izoh", value=tx["note"] or "",
                                                 key=f"note_{tx['id']}")

                        if st.form_submit_button("Saqlash", type="primary"):
                            update_transaction(tx["id"], new_qty, new_doc, str(new_date), new_note)
                            st.success("Yangilandi!")
                            st.rerun()

                    if st.button("O'chirish", key=f"del_{tx['id']}", type="secondary"):
                        soft_delete_transaction(tx["id"])
                        st.warning("O'chirildi")
                        st.rerun()
else:
    info_banner("Tanlangan filtrlar bo'yicha operatsiyalar topilmadi.", "alert-circle")
