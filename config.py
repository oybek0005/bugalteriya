import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "bugalteriya.db")

UNITS = ["dona", "kg", "metr", "litr", "tonna", "pachka", "komplekt"]

TX_TYPES = {
    "chiqim": "Chiqim (Xomashyo yuborish)",
    "kirim": "Kirim (Tayyor mahsulot qabul qilish)",
    "sarf": "Sarf (Ishlatilgan material)",
    "chiqindi": "Chiqindi / Brak",
    "tuzatish": "Tuzatish (Qo'lda o'zgartirish)",
}

ITEM_TYPES = {
    "xomashyo": "Xomashyo",
    "tayyor": "Tayyor mahsulot",
}

# Uzbek UI labels
LABELS = {
    "app_title": "Davalshina — Xomashyo Boshqaruv Tizimi",
    "dashboard": "Asosiy Panel",
    "warehouse": "Ombor Qoldig'i",
    "outbound": "Xomashyo Chiqimi (Akt)",
    "inbound": "Tayyor Mahsulot (Hisobot)",
    "firm_balance": "Firma Qoldig'i",
    "history": "Tarix",
    "reports": "Hisobot",
    "save": "Saqlash",
    "edit": "Tahrirlash",
    "delete": "O'chirish",
    "cancel": "Bekor qilish",
    "confirm": "Tasdiqlash",
    "date_range": "Sana Oralig'i",
    "firm": "Firma",
    "material": "Material",
    "quantity": "Miqdor",
    "unit": "Birlik",
    "document_number": "Hujjat raqami",
    "document_date": "Hujjat sanasi",
    "note": "Izoh",
    "total": "Jami",
    "no_data": "Ma'lumot topilmadi",
    "success": "Muvaffaqiyatli saqlandi!",
    "error": "Xatolik yuz berdi",
    "upload_pdf": "PDF yuklash",
    "manual_entry": "Qo'lda kiritish",
    "all_firms": "Barcha firmalar",
    "export_excel": "Excel yuklash",
    "remaining": "Qoldiq",
    "waste_percent": "Chiqindi %",
    "items_sent": "Yuborilgan mahsulotlar",
    "items_received": "Qabul qilingan mahsulotlar",
    "items_in_transit": "Firmadagi qoldiq",
    "total_firms": "Jami firmalar",
}
