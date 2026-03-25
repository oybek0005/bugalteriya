import streamlit as st
from database import init_db
from config import LABELS
from styles import inject_css, icon, page_header

st.set_page_config(
    page_title=LABELS["app_title"],
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_css()

# Welcome hero
st.markdown(f"""
<div class="welcome-card">
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:12px;">
        {icon("package", size=36, color="white")}
        <h2 style="margin:0!important;">Davalshina Boshqaruv Tizimi</h2>
    </div>
    <p>Xomashyo va tayyor mahsulotlarni firmalar bo'yicha kuzatib borish uchun zamonaviy platforma</p>
</div>
""", unsafe_allow_html=True)

# Feature cards
features = [
    ("layout-dashboard", "#dbeafe", "#2563eb", "Asosiy Panel", "Ombor va firmalar bo'yicha umumiy statistika"),
    ("send", "#fef3c7", "#d97706", "Xomashyo Chiqimi", "Xomashyoni firmaga yuborish — Akt asosida"),
    ("inbox", "#dcfce7", "#16a34a", "Tayyor Mahsulot", "Tayyor mahsulotni firmadan qabul qilish"),
    ("building", "#e9d5ff", "#7c3aed", "Firma Qoldig'i", "Har bir firmadagi qoldiq holati"),
    ("warehouse", "#fed7aa", "#ea580c", "Ombor Qoldig'i", "Asosiy ombordagi mahsulotlar"),
    ("history", "#fecaca", "#dc2626", "Tarix", "Barcha operatsiyalar — tahrirlash/o'chirish"),
    ("bar-chart", "#cffafe", "#0891b2", "Hisobot", "Excel formatida hisobotlar yuklash"),
]

cols = st.columns(4)
for i, (ic, bg, fg, title, desc) in enumerate(features):
    with cols[i % 4]:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon" style="background:{bg}; color:{fg};">
                {icon(ic, size=22, color=fg)}
            </div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

st.markdown("")
st.markdown("")

# Sidebar - firm & product management
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding:8px 0;">
        {icon("package", size=24, color="#60a5fa")}
        <span style="font-size:1.1rem; font-weight:600; color:#f1f5f9;">Davalshina</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    with st.expander("Yangi firma qo'shish"):
        from database import add_firm
        fname = st.text_input("Firma nomi", key="new_firm_name")
        fstir = st.text_input("STIR (INN)", key="new_firm_stir")
        fphone = st.text_input("Telefon", key="new_firm_phone")
        faddr = st.text_input("Manzil", key="new_firm_addr")
        if st.button("Qo'shish", key="add_firm_btn"):
            if fname:
                if add_firm(fname, fstir, fphone, faddr):
                    st.success("Firma qo'shildi!")
                    st.rerun()
                else:
                    st.error("Bu nomli firma mavjud!")
            else:
                st.warning("Firma nomini kiriting!")

    with st.expander("Yangi mahsulot qo'shish"):
        from database import add_inventory_item
        from config import UNITS, ITEM_TYPES
        pname = st.text_input("Mahsulot nomi", key="new_prod_name")
        punit = st.selectbox("Birlik", UNITS, key="new_prod_unit")
        ptype = st.selectbox("Turi", list(ITEM_TYPES.keys()),
                             format_func=lambda x: ITEM_TYPES[x], key="new_prod_type")
        if st.button("Qo'shish", key="add_prod_btn"):
            if pname:
                if add_inventory_item(pname, punit, ptype):
                    st.success("Mahsulot qo'shildi!")
                    st.rerun()
                else:
                    st.error("Bu nomli mahsulot mavjud!")
            else:
                st.warning("Mahsulot nomini kiriting!")
