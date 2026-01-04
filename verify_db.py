from app.database import db
import os
from app.config import Config

print(f"Checking DB at: {Config.DB_PATH}")
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
table_names = [t[0] for t in tables]
print("Tables found:", table_names)

required_tables = ['products', 'customers', 'invoices', 'invoice_items', 'stock', 'purchases', 'price_history']
missing = [t for t in required_tables if t not in table_names]

if missing:
    print(f"MISSING TABLES: {missing}")
    exit(1)

print("DB Verification PASSED")
