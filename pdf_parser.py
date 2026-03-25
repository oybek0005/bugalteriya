import re
import io
import pdfplumber


def parse_act_pdf(file_bytes):
    """Parse an outbound Act (Chiqim) PDF.
    Extracts: firm name, document number, date, and line items.
    Returns dict with keys: firm_name, doc_number, doc_date, items[]
    Each item: {name, quantity, unit}
    """
    result = {
        "firm_name": "",
        "doc_number": "",
        "doc_date": "",
        "items": [],
    }

    try:
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
    except Exception:
        return result

    full_text = ""
    all_tables = []

    for page in pdf.pages:
        text = page.extract_text() or ""
        full_text += text + "\n"
        tables = page.extract_tables()
        for table in tables:
            all_tables.append(table)

    pdf.close()

    # Extract document number (e.g., "Akt № 0-16", "№ 0-16")
    doc_match = re.search(r'[№#]\s*([\d\-/]+)', full_text)
    if doc_match:
        result["doc_number"] = doc_match.group(1).strip()

    # Extract date (common formats: dd.mm.yyyy, dd/mm/yyyy)
    date_match = re.search(r'(\d{2}[./]\d{2}[./]\d{4})', full_text)
    if date_match:
        date_str = date_match.group(1).replace("/", ".")
        parts = date_str.split(".")
        if len(parts) == 3:
            result["doc_date"] = f"{parts[2]}-{parts[1]}-{parts[0]}"  # ISO format

    # Extract firm name - look for common patterns
    firm_patterns = [
        r'(?:Олувчи|Qabul qiluvchi|Buyurtmachi|Firma)[:\s]*["\']?([A-Z][A-Z\s\-]+(?:LLC|OOO|МЧЖ|MCHJ)?)',
        r'(?:BUILDING|LENS|TEXTILE|INVEST|GROUP|BARAKA)[\s\-A-Z]+',
    ]
    for pattern in firm_patterns:
        firm_match = re.search(pattern, full_text, re.IGNORECASE)
        if firm_match:
            result["firm_name"] = firm_match.group(0).strip().strip('"\'')
            break

    # Parse table data
    if all_tables:
        for table in all_tables:
            if not table or len(table) < 2:
                continue
            # Try to identify header row and data rows
            header = table[0] if table[0] else []
            header_lower = [str(h).lower() if h else "" for h in header]

            # Find relevant columns
            name_col = _find_column(header_lower, ["наименование", "nomi", "mahsulot", "товар", "material"])
            qty_col = _find_column(header_lower, ["количество", "кол-во", "miqdor", "soni", "кол"])
            unit_col = _find_column(header_lower, ["единица", "ед", "birlik", "o'lchov"])

            for row in table[1:]:
                if not row or all(not cell for cell in row):
                    continue

                item = {"name": "", "quantity": 0, "unit": "dona"}

                if name_col is not None and name_col < len(row) and row[name_col]:
                    item["name"] = str(row[name_col]).strip()
                elif row[0]:
                    # If no header match, try first text column
                    for cell in row:
                        if cell and not _is_number(str(cell)):
                            item["name"] = str(cell).strip()
                            break

                if qty_col is not None and qty_col < len(row) and row[qty_col]:
                    item["quantity"] = _parse_number(str(row[qty_col]))
                else:
                    # Find first numeric value
                    for cell in row:
                        if cell and _is_number(str(cell)):
                            item["quantity"] = _parse_number(str(cell))
                            break

                if unit_col is not None and unit_col < len(row) and row[unit_col]:
                    item["unit"] = str(row[unit_col]).strip()

                if item["name"] and item["quantity"] > 0:
                    result["items"].append(item)

    return result


def parse_report_pdf(file_bytes):
    """Parse an inbound Report (Kirim/Hisobot) PDF.
    Extracts: firm name, document number, date, input items, output items, waste.
    Returns dict with keys: firm_name, doc_number, doc_date, items[]
    Each item: {name, quantity, unit, category} where category is 'kirim'|'sarf'|'chiqindi'
    """
    result = {
        "firm_name": "",
        "doc_number": "",
        "doc_date": "",
        "items": [],
    }

    try:
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
    except Exception:
        return result

    full_text = ""
    all_tables = []

    for page in pdf.pages:
        text = page.extract_text() or ""
        full_text += text + "\n"
        tables = page.extract_tables()
        for table in tables:
            all_tables.append(table)

    pdf.close()

    # Extract document info (same logic as Act)
    doc_match = re.search(r'[№#]\s*([\d\-/]+)', full_text)
    if doc_match:
        result["doc_number"] = doc_match.group(1).strip()

    date_match = re.search(r'(\d{2}[./]\d{2}[./]\d{4})', full_text)
    if date_match:
        date_str = date_match.group(1).replace("/", ".")
        parts = date_str.split(".")
        if len(parts) == 3:
            result["doc_date"] = f"{parts[2]}-{parts[1]}-{parts[0]}"

    firm_patterns = [
        r'(?:Олувчи|Qabul qiluvchi|Buyurtmachi|Firma|Подрядчик|Ishlab chiqaruvchi)[:\s]*["\']?([A-Z][A-Z\s\-]+)',
        r'(?:BUILDING|LENS|TEXTILE|INVEST|GROUP|BARAKA)[\s\-A-Z]+',
    ]
    for pattern in firm_patterns:
        firm_match = re.search(pattern, full_text, re.IGNORECASE)
        if firm_match:
            result["firm_name"] = firm_match.group(0).strip().strip('"\'')
            break

    # Parse tables - report may have sections for input, usage, waste
    current_category = "kirim"

    section_markers = {
        "kirim": ["кирим", "kirim", "приход", "qabul", "input", "kirish"],
        "sarf": ["сарф", "sarf", "расход", "ishlatilgan", "usage", "использовано"],
        "chiqindi": ["чиқинди", "chiqindi", "отход", "brak", "waste", "брак", "otxod"],
    }

    if all_tables:
        for table in all_tables:
            if not table or len(table) < 2:
                continue

            header = table[0] if table[0] else []
            header_text = " ".join(str(h).lower() for h in header if h)

            # Detect section
            for cat, markers in section_markers.items():
                if any(m in header_text for m in markers):
                    current_category = cat
                    break

            header_lower = [str(h).lower() if h else "" for h in header]
            name_col = _find_column(header_lower, ["наименование", "nomi", "mahsulot", "товар", "material"])
            qty_col = _find_column(header_lower, ["количество", "кол-во", "miqdor", "soni", "кол"])
            unit_col = _find_column(header_lower, ["единица", "ед", "birlik", "o'lchov"])

            for row in table[1:]:
                if not row or all(not cell for cell in row):
                    continue

                row_text = " ".join(str(c).lower() for c in row if c)
                for cat, markers in section_markers.items():
                    if any(m in row_text for m in markers):
                        current_category = cat

                item = {"name": "", "quantity": 0, "unit": "dona", "category": current_category}

                if name_col is not None and name_col < len(row) and row[name_col]:
                    item["name"] = str(row[name_col]).strip()
                elif row[0]:
                    for cell in row:
                        if cell and not _is_number(str(cell)):
                            item["name"] = str(cell).strip()
                            break

                if qty_col is not None and qty_col < len(row) and row[qty_col]:
                    item["quantity"] = _parse_number(str(row[qty_col]))
                else:
                    for cell in row:
                        if cell and _is_number(str(cell)):
                            item["quantity"] = _parse_number(str(cell))
                            break

                if unit_col is not None and unit_col < len(row) and row[unit_col]:
                    item["unit"] = str(row[unit_col]).strip()

                if item["name"] and item["quantity"] > 0:
                    result["items"].append(item)

    return result


def extract_raw_tables(file_bytes):
    """Extract meaningful tables from PDF.
    Filters out: signing pages, signature tables, tiny tables.
    Returns list of tables, each is a dict with 'headers' and 'rows'.
    """
    tables = []

    try:
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
    except Exception:
        return tables

    for page_num, page in enumerate(pdf.pages, 1):
        # Sahifa tekstini tekshirish — imzo protokoli sahifalarni o'tkazish
        page_text = (page.extract_text() or "").lower()
        skip_keywords = ["имзолаш протоколи", "протокол подписания", "ҳужжат имзоланган"]
        if any(kw in page_text for kw in skip_keywords):
            continue

        raw_tables = page.extract_tables()

        if not raw_tables:
            raw_tables = page.extract_tables({
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
            })

        for t_idx, table in enumerate(raw_tables):
            if not table or len(table) < 3:
                # Kamida 3 qator (header + 2 data) — kichik jadvallar skip
                continue

            max_cols = max(len(row) for row in table if row)

            # 2 yoki kamroq ustunli jadvallar skip (imzolar, izohlar)
            if max_cols <= 2:
                continue

            # Header topish: birinchi qatordan, yoki sarlavha qatori bo'lsa
            # keyingi qatordan olish
            header_row_idx = 0
            first_row = table[0]

            # Agar birinchi qator birlashtirilgan (ko'p None) bo'lsa — sarlavha
            # qatori, keyingisini header qilish
            non_none = sum(1 for c in first_row if c)
            if non_none <= 2 and len(table) > 2:
                header_row_idx = 1
                first_row = table[1]

            header = []
            for i in range(max_cols):
                if first_row and i < len(first_row) and first_row[i]:
                    h = str(first_row[i]).strip().replace("\n", " ")
                    header.append(h if h else f"Ustun {i+1}")
                else:
                    header.append(f"Ustun {i+1}")

            # Data qatorlari
            rows = []
            for row in table[header_row_idx + 1:]:
                if not row:
                    continue
                cleaned = []
                for i in range(max_cols):
                    if i < len(row) and row[i]:
                        cleaned.append(str(row[i]).strip().replace("\n", " "))
                    else:
                        cleaned.append("")
                if any(cell for cell in cleaned):
                    rows.append(cleaned)

            if not rows:
                continue

            # Takroriy ustun nomlarini unique qilish
            seen = {}
            unique_header = []
            for h in header:
                if h in seen:
                    seen[h] += 1
                    unique_header.append(f"{h} ({seen[h]})")
                else:
                    seen[h] = 0
                    unique_header.append(h)

            tables.append({
                "page": page_num,
                "table_index": t_idx,
                "headers": unique_header,
                "rows": rows,
            })

    pdf.close()
    return tables


def extract_columns_from_table(table_data, column_indices):
    """Extract specific columns from a raw table by index.
    column_indices: list of int (0-based)
    Returns list of dicts with header:value pairs.
    """
    headers = table_data["headers"]
    result = []
    for row in table_data["rows"]:
        item = {}
        for idx in column_indices:
            if idx < len(headers):
                item[headers[idx]] = row[idx] if idx < len(row) else ""
        result.append(item)
    return result


def _find_column(header_lower, keywords):
    for i, h in enumerate(header_lower):
        for kw in keywords:
            if kw in h:
                return i
    return None


def _is_number(s):
    s = s.replace(" ", "").replace(",", ".")
    try:
        float(s)
        return True
    except ValueError:
        return False


def _parse_number(s):
    s = s.replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0
