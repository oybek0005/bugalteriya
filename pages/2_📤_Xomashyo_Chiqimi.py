import streamlit as st
import pandas as pd
import base64
import io
from datetime import date
from database import (
    init_db, get_firms, get_inventory, add_transaction,
    get_or_create_inventory,
)
from config import UNITS
from pdf_parser import extract_raw_tables
from styles import page_header, section_header, icon, info_banner

init_db()

page_header("Xomashyo Chiqimi", "send", "Xomashyoni firmaga yuborish — Akt asosida yoki qo'lda kiritish")

tab_pdf, tab_manual = st.tabs([
    f"  PDF yuklash  ",
    f"  Qo'lda kiritish  ",
])

# --- PDF Upload Tab ---
with tab_pdf:
    uploaded_files = st.file_uploader(
        "PDF fayllarni yuklang (bir nechta bo'lishi mumkin)",
        type="pdf",
        key="act_pdf",
        accept_multiple_files=True,
    )

    if uploaded_files:
        if "chiqim_items" not in st.session_state:
            st.session_state.chiqim_items = []

        for file_idx, uploaded_file in enumerate(uploaded_files):
            file_bytes = uploaded_file.read()
            st.markdown(f"---\n### {uploaded_file.name}")

            col_pdf, col_table = st.columns([1, 1])

            # CHAP: PDF ko'rish
            with col_pdf:
                section_header("PDF ko'rish", "eye")
                b64 = base64.b64encode(file_bytes).decode()
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{b64}" '
                    f'width="100%" height="600" style="border:1px solid #ddd; border-radius:8px;"></iframe>',
                    unsafe_allow_html=True,
                )

            # O'NG: HAMMA jadvallar
            with col_table:
                raw_tables = extract_raw_tables(file_bytes)

                if not raw_tables:
                    st.warning("Bu PDF da jadval topilmadi.")
                    continue

                st.success(f"Jami {len(raw_tables)} ta jadval topildi")

                for t_idx, tbl in enumerate(raw_tables):
                    headers = tbl["headers"]
                    rows = tbl["rows"]

                    st.markdown(f"#### {t_idx + 1}-jadval (sahifa {tbl['page']}, {len(rows)} qator, {len(headers)} ustun)")

                    full_df = pd.DataFrame(rows, columns=headers)
                    st.dataframe(full_df, use_container_width=True, height=min(200, 50 + len(rows) * 35))

                    # Ustunlar ro'yxati
                    cols_text = "  |  ".join([f"`{i+1}`={h}" for i, h in enumerate(headers)])
                    st.caption(cols_text)

                    # Ustun raqamini kiritish
                    col_input = st.text_input(
                        "Kerakli ustun raqamlarini kiriting (masalan: 2,4) yoki bo'sh qoldiring — hammasi olinadi",
                        key=f"cols_{file_idx}_{t_idx}",
                        placeholder="2,4",
                    )

                    # Tanlangan ustunlar bo'yicha df tayyorlash
                    if col_input:
                        try:
                            indices = [int(x.strip()) - 1 for x in col_input.split(",")]
                            bad = [i+1 for i in indices if i < 0 or i >= len(headers)]
                            if bad:
                                st.error(f"Noto'g'ri: {bad}. 1 dan {len(headers)} gacha.")
                                selected_df = full_df
                            else:
                                selected_cols = [headers[i] for i in indices]
                                selected_df = full_df[selected_cols]
                        except ValueError:
                            st.error("Faqat raqam va vergul. Masalan: 2,4")
                            selected_df = full_df
                    else:
                        selected_df = full_df

                    btn_col1, btn_col2 = st.columns(2)

                    # Excel yuklab olish
                    with btn_col1:
                        excel_buf = io.BytesIO()
                        selected_df.to_excel(excel_buf, index=False, engine="openpyxl")
                        label = f"Excel ({t_idx+1}-jadval" + (f", ustunlar: {col_input}" if col_input else ", hammasi") + ")"
                        st.download_button(
                            label,
                            data=excel_buf.getvalue(),
                            file_name=f"{uploaded_file.name}_{t_idx+1}_jadval.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{file_idx}_{t_idx}",
                        )

                    # Ro'yxatga qo'shish
                    with btn_col2:
                        if st.button("Ro'yxatga qo'shish", key=f"get_{file_idx}_{t_idx}"):
                            items = selected_df.to_dict("records")
                            st.session_state.chiqim_items.extend(items)
                            st.success(f"{len(items)} qator qo'shildi!")
                            st.rerun()

                    st.markdown("---")

        # --- Yig'ilgan ma'lumotlar ---
        if st.session_state.chiqim_items:
            section_header("Yig'ilgan ma'lumotlar", "package-check")

            result_df = pd.DataFrame(st.session_state.chiqim_items)
            edited_df = st.data_editor(result_df, num_rows="dynamic", key="chiqim_edit", use_container_width=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                excel_buf = io.BytesIO()
                edited_df.to_excel(excel_buf, index=False, engine="openpyxl")
                st.download_button(
                    "Excel yuklab olish",
                    data=excel_buf.getvalue(),
                    file_name="chiqim_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            with col2:
                if st.button("Tozalash", key="clear_chiqim"):
                    st.session_state.chiqim_items = []
                    st.rerun()

            # Bazaga saqlash
            with st.expander("Bazaga saqlash"):
                firms = get_firms()
                firm_names = [f["name"] for f in firms]
                if not firm_names:
                    st.warning("Avval firma qo'shing!")
                else:
                    selected_firm = st.selectbox("Firma", firm_names, key="pdf_act_firm")
                    doc_num = st.text_input("Hujjat raqami", key="pdf_act_docnum")
                    doc_date = st.date_input("Hujjat sanasi", value=date.today(), key="pdf_act_date")
                    df_cols = list(edited_df.columns)
                    name_col = st.selectbox("Qaysi ustun = Mahsulot nomi?", df_cols, key="map_name")
                    qty_col = st.selectbox("Qaysi ustun = Miqdor?", df_cols, key="map_qty")

                    if st.button("Bazaga saqlash", key="save_chiqim_db", type="primary"):
                        firm = next(f for f in firms if f["name"] == selected_firm)
                        saved = 0
                        for _, row in edited_df.iterrows():
                            name_val = str(row[name_col]).strip()
                            try:
                                qty_val = float(str(row[qty_col]).replace(" ", "").replace(",", "."))
                            except ValueError:
                                qty_val = 0
                            if name_val and qty_val > 0:
                                inv = get_or_create_inventory(name_val, "dona", "xomashyo")
                                add_transaction(
                                    firm_id=firm["id"], inventory_id=inv["id"],
                                    tx_type="chiqim", quantity=qty_val,
                                    document_number=doc_num, document_date=str(doc_date),
                                    note=f"PDF: {', '.join(f.name for f in uploaded_files)}",
                                    source="pdf",
                                )
                                saved += 1
                        st.session_state.chiqim_items = []
                        st.success(f"{saved} ta mahsulot saqlandi!")
                        st.rerun()

# --- Manual Entry Tab ---
with tab_manual:
    firms = get_firms()
    inventory = get_inventory("xomashyo")

    if not firms:
        info_banner("Avval firma qo'shing (bosh sahifadagi sidebar orqali)", "alert-circle")
    elif not inventory:
        info_banner("Avval xomashyo qo'shing (bosh sahifadagi sidebar orqali)", "alert-circle")
    else:
        with st.form("manual_chiqim_form"):
            col1, col2 = st.columns(2)
            with col1:
                firm = st.selectbox("Firma", firms, format_func=lambda f: f["name"])
                inv_item = st.selectbox("Xomashyo", inventory, format_func=lambda i: f"{i['name']} ({i['unit']})")
                qty = st.number_input("Miqdor", min_value=0.01, step=1.0, format="%.2f")
            with col2:
                doc_num = st.text_input("Hujjat raqami (Akt №)")
                doc_date = st.date_input("Hujjat sanasi", value=date.today())
                note = st.text_area("Izoh", height=68)

            submitted = st.form_submit_button("Saqlash", use_container_width=True, type="primary")
            if submitted:
                add_transaction(
                    firm_id=firm["id"], inventory_id=inv_item["id"],
                    tx_type="chiqim", quantity=qty,
                    document_number=doc_num, document_date=str(doc_date),
                    note=note, source="manual",
                )
                st.success(f"{qty} {inv_item['unit']} {inv_item['name']} — {firm['name']} ga yuborildi!")
                st.rerun()

    st.markdown("---")
    with st.expander("Tez qo'shish: Yangi xomashyo"):
        new_name = st.text_input("Nomi", key="quick_xom_name")
        new_unit = st.selectbox("Birlik", UNITS, key="quick_xom_unit")
        if st.button("Qo'shish", key="quick_xom_btn"):
            if new_name:
                from database import add_inventory_item
                if add_inventory_item(new_name, new_unit, "xomashyo"):
                    st.success("Qo'shildi!")
                    st.rerun()
                else:
                    st.error("Bu nomli mahsulot mavjud!")
