import io
import pandas as pd
from database import get_transactions


def build_report_df(firm_id=None, date_from=None, date_to=None, tx_type=None):
    rows = get_transactions(
        firm_id=firm_id, date_from=date_from, date_to=date_to, tx_type=tx_type
    )
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df[["document_date", "document_number", "firm_name", "item_name",
             "tx_type", "quantity", "item_unit", "note", "source", "created_at"]]
    df.columns = [
        "Sana", "Hujjat №", "Firma", "Mahsulot",
        "Turi", "Miqdor", "Birlik", "Izoh", "Manba", "Yaratilgan"
    ]

    type_map = {
        "chiqim": "Chiqim",
        "kirim": "Kirim",
        "sarf": "Sarf",
        "chiqindi": "Chiqindi",
        "tuzatish": "Tuzatish",
    }
    df["Turi"] = df["Turi"].map(type_map).fillna(df["Turi"])

    return df


def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Hisobot")
    return output.getvalue()
