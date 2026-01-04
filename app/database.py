import sqlite3
import logging
from app.config import Config

class DatabaseManager:
    def __init__(self, db_path=Config.DB_PATH):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize database with tables if they don't exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Products Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        qr_code TEXT UNIQUE NOT NULL,
                        category TEXT, -- Battery / Inverter
                        brand_name TEXT,
                        model_name TEXT,
                        warranty_months INTEGER,
                        current_price REAL,
                        current_purchase_price REAL DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Customers Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT,
                        mobile_number TEXT UNIQUE NOT NULL,
                        address TEXT
                    )
                ''')
                
                # Invoices Header Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS invoices (
                        invoice_no TEXT PRIMARY KEY,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        customer_id INTEGER,
                        total_amount REAL,
                        old_battery_value REAL,
                        old_battery_description TEXT,
                        final_amount REAL,
                        FOREIGN KEY (customer_id) REFERENCES customers (id)
                    )
                ''')
                
                # Invoice Items Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS invoice_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_no TEXT,
                        product_id INTEGER,
                        quantity INTEGER,
                        unit_price REAL,
                        total_price REAL,
                        FOREIGN KEY (invoice_no) REFERENCES invoices (invoice_no),
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # Stock Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock (
                        product_id INTEGER PRIMARY KEY,
                        quantity_available INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')

                # Purchases Table (Distributor Tracking)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS purchases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        distributor_name TEXT,
                        product_id INTEGER,
                        quantity INTEGER,
                        purchase_price REAL,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')

                # Price History Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER,
                        old_price REAL,
                        new_price REAL,
                        change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reason TEXT,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

db = DatabaseManager()
