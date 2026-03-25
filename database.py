import sqlite3
import os
from datetime import datetime
from config import DB_PATH


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS firms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stir TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            unit TEXT NOT NULL DEFAULT 'dona',
            item_type TEXT NOT NULL CHECK(item_type IN ('xomashyo', 'tayyor')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS firm_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_id INTEGER NOT NULL REFERENCES firms(id),
            inventory_id INTEGER NOT NULL REFERENCES inventory(id),
            quantity REAL NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(firm_id, inventory_id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_id INTEGER NOT NULL REFERENCES firms(id),
            inventory_id INTEGER NOT NULL REFERENCES inventory(id),
            tx_type TEXT NOT NULL CHECK(tx_type IN ('chiqim', 'kirim', 'sarf', 'chiqindi', 'tuzatish')),
            quantity REAL NOT NULL,
            document_number TEXT,
            document_date DATE,
            note TEXT,
            source TEXT DEFAULT 'manual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()


# --- Firms ---

def get_firms():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM firms ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_firm(name, stir="", phone="", address=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO firms (name, stir, phone, address) VALUES (?, ?, ?, ?)",
            (name.strip(), stir.strip(), phone.strip(), address.strip()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_firm(firm_id, name, stir="", phone="", address=""):
    conn = get_connection()
    conn.execute(
        "UPDATE firms SET name=?, stir=?, phone=?, address=? WHERE id=?",
        (name.strip(), stir.strip(), phone.strip(), address.strip(), firm_id),
    )
    conn.commit()
    conn.close()


# --- Inventory ---

def get_inventory(item_type=None):
    conn = get_connection()
    if item_type:
        rows = conn.execute(
            "SELECT * FROM inventory WHERE item_type=? ORDER BY name", (item_type,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM inventory ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_inventory_item(name, unit="dona", item_type="xomashyo"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO inventory (name, unit, item_type) VALUES (?, ?, ?)",
            (name.strip(), unit, item_type),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_or_create_inventory(name, unit="dona", item_type="xomashyo"):
    conn = get_connection()
    row = conn.execute("SELECT * FROM inventory WHERE name=?", (name.strip(),)).fetchone()
    if row:
        conn.close()
        return dict(row)
    conn.execute(
        "INSERT INTO inventory (name, unit, item_type) VALUES (?, ?, ?)",
        (name.strip(), unit, item_type),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM inventory WHERE name=?", (name.strip(),)).fetchone()
    conn.close()
    return dict(row)


# --- Transactions ---

def add_transaction(firm_id, inventory_id, tx_type, quantity, document_number="",
                    document_date=None, note="", source="manual"):
    conn = get_connection()
    conn.execute(
        """INSERT INTO transactions
           (firm_id, inventory_id, tx_type, quantity, document_number, document_date, note, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (firm_id, inventory_id, tx_type, quantity, document_number, document_date, note, source),
    )
    _update_balance(conn, firm_id, inventory_id, tx_type, quantity)
    conn.commit()
    conn.close()


def get_transactions(firm_id=None, date_from=None, date_to=None, tx_type=None, include_deleted=False):
    conn = get_connection()
    query = """
        SELECT t.*, f.name as firm_name, i.name as item_name, i.unit as item_unit
        FROM transactions t
        JOIN firms f ON t.firm_id = f.id
        JOIN inventory i ON t.inventory_id = i.id
        WHERE 1=1
    """
    params = []

    if not include_deleted:
        query += " AND t.is_deleted = 0"

    if firm_id:
        query += " AND t.firm_id = ?"
        params.append(firm_id)
    if date_from:
        query += " AND t.document_date >= ?"
        params.append(str(date_from))
    if date_to:
        query += " AND t.document_date <= ?"
        params.append(str(date_to))
    if tx_type:
        query += " AND t.tx_type = ?"
        params.append(tx_type)

    query += " ORDER BY t.created_at DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def soft_delete_transaction(tx_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM transactions WHERE id=? AND is_deleted=0", (tx_id,)).fetchone()
    if not row:
        conn.close()
        return False
    tx = dict(row)
    # Reverse the balance effect
    _update_balance(conn, tx["firm_id"], tx["inventory_id"], tx["tx_type"], -tx["quantity"])
    conn.execute("UPDATE transactions SET is_deleted=1 WHERE id=?", (tx_id,))
    conn.commit()
    conn.close()
    return True


def update_transaction(tx_id, quantity, document_number, document_date, note):
    conn = get_connection()
    old = conn.execute("SELECT * FROM transactions WHERE id=? AND is_deleted=0", (tx_id,)).fetchone()
    if not old:
        conn.close()
        return False
    old = dict(old)
    # Reverse old balance, apply new
    _update_balance(conn, old["firm_id"], old["inventory_id"], old["tx_type"], -old["quantity"])
    _update_balance(conn, old["firm_id"], old["inventory_id"], old["tx_type"], quantity)
    conn.execute(
        """UPDATE transactions SET quantity=?, document_number=?, document_date=?, note=?
           WHERE id=?""",
        (quantity, document_number, document_date, note, tx_id),
    )
    conn.commit()
    conn.close()
    return True


def _update_balance(conn, firm_id, inventory_id, tx_type, quantity):
    """Update firm_balances based on transaction type.
    chiqim (outbound): increases firm's debt (they hold more of our materials)
    kirim (inbound): decreases firm's debt (they returned finished goods)
    sarf (usage): decreases firm's debt (materials consumed)
    chiqindi (waste): decreases firm's debt (materials lost)
    tuzatish (adjustment): direct adjustment to balance
    """
    if tx_type == "chiqim":
        delta = quantity
    elif tx_type in ("kirim", "sarf", "chiqindi"):
        delta = -quantity
    else:  # tuzatish
        delta = quantity

    existing = conn.execute(
        "SELECT id, quantity FROM firm_balances WHERE firm_id=? AND inventory_id=?",
        (firm_id, inventory_id),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE firm_balances SET quantity = quantity + ?, updated_at = ? WHERE id = ?",
            (delta, datetime.now().isoformat(), existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO firm_balances (firm_id, inventory_id, quantity, updated_at) VALUES (?, ?, ?, ?)",
            (firm_id, inventory_id, delta, datetime.now().isoformat()),
        )


# --- Balances ---

def get_firm_balances(firm_id=None):
    conn = get_connection()
    query = """
        SELECT fb.*, f.name as firm_name, i.name as item_name, i.unit as item_unit, i.item_type
        FROM firm_balances fb
        JOIN firms f ON fb.firm_id = f.id
        JOIN inventory i ON fb.inventory_id = i.id
        WHERE fb.quantity != 0
    """
    params = []
    if firm_id:
        query += " AND fb.firm_id = ?"
        params.append(firm_id)
    query += " ORDER BY f.name, i.name"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_warehouse_stock():
    """Main warehouse stock = total inventory minus what's at firms."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.id, i.name, i.unit, i.item_type,
               COALESCE(SUM(CASE WHEN t.tx_type = 'chiqim' THEN t.quantity ELSE 0 END), 0) as total_sent,
               COALESCE(SUM(CASE WHEN t.tx_type = 'kirim' THEN t.quantity ELSE 0 END), 0) as total_received,
               COALESCE(SUM(CASE WHEN t.tx_type = 'sarf' THEN t.quantity ELSE 0 END), 0) as total_used,
               COALESCE(SUM(CASE WHEN t.tx_type = 'chiqindi' THEN t.quantity ELSE 0 END), 0) as total_waste
        FROM inventory i
        LEFT JOIN transactions t ON i.id = t.inventory_id AND t.is_deleted = 0
        GROUP BY i.id
        ORDER BY i.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_summary():
    conn = get_connection()
    total_firms = conn.execute("SELECT COUNT(*) as cnt FROM firms").fetchone()["cnt"]

    total_out = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) as total FROM transactions WHERE tx_type='chiqim' AND is_deleted=0"
    ).fetchone()["total"]

    total_in = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) as total FROM transactions WHERE tx_type='kirim' AND is_deleted=0"
    ).fetchone()["total"]

    total_at_firms = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) as total FROM firm_balances WHERE quantity > 0"
    ).fetchone()["total"]

    conn.close()
    return {
        "total_firms": total_firms,
        "total_out": total_out,
        "total_in": total_in,
        "total_at_firms": total_at_firms,
    }


def recalculate_all_balances():
    """Rebuild firm_balances from transactions. Use if balances drift."""
    conn = get_connection()
    conn.execute("DELETE FROM firm_balances")
    rows = conn.execute("""
        SELECT firm_id, inventory_id, tx_type, SUM(quantity) as total_qty
        FROM transactions
        WHERE is_deleted = 0
        GROUP BY firm_id, inventory_id, tx_type
    """).fetchall()

    for row in rows:
        r = dict(row)
        _update_balance(conn, r["firm_id"], r["inventory_id"], r["tx_type"], r["total_qty"])

    conn.commit()
    conn.close()
