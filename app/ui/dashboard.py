from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QFrame, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt
from app.database import db
from app.config import Config
from datetime import datetime

class StatCard(QFrame):
    def __init__(self, title, value, icon, subtitle="", color="#007BFF"):
        super().__init__()
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(10)

        # Header with Icon
        header_layout = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 24px; color: {color}; background: transparent;")
        header_layout.addWidget(icon_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Value and Title
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet("font-size: 32px; font-weight: 800; background: transparent;")
        layout.addWidget(self.val_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #6C757D; background: transparent;")
        layout.addWidget(title_lbl)

        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setObjectName("Description")
        self.sub_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(self.sub_lbl)

class Dashboard(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(30)
        scroll.setWidget(content)

        # 1. Stat Cards Grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        self.card_sales = StatCard("Today's Sales", "₹0.00", "💰", "Based on 0 invoices")
        self.card_invoices = StatCard("Total Invoices", "0", "📄", "Cumulative count")
        self.card_stock = StatCard("Low Stock Items", "0", "⚠️", "Requires attention", color="#DC3545")
        self.card_products = StatCard("Total Products", "0", "📦", "In inventory")

        stats_layout.addWidget(self.card_sales, 0, 0)
        stats_layout.addWidget(self.card_invoices, 0, 1)
        stats_layout.addWidget(self.card_stock, 0, 2)
        stats_layout.addWidget(self.card_products, 0, 3)

        self.content_layout.addLayout(stats_layout)

        # 2. Main Content
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(20)

        # Recent Invoices Card
        invoice_card = QFrame()
        invoice_card.setObjectName("Card")
        inv_v_layout = QVBoxLayout(invoice_card)
        inv_v_layout.setContentsMargins(25, 25, 25, 25)
        
        inv_header = QHBoxLayout()
        inv_title = QLabel("Recent Invoices")
        inv_title.setObjectName("SubHeader")
        inv_header.addWidget(inv_title)
        inv_header.addStretch()
        btn_all = QPushButton("View All")
        btn_all.setObjectName("Secondary")
        inv_header.addWidget(btn_all)
        inv_v_layout.addLayout(inv_header)

        self.table_invoices = QTableWidget(0, 4)
        self.table_invoices.setHorizontalHeaderLabels(["INVOICE #", "CUSTOMER", "TOTAL", "DATE"])
        self.table_invoices.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_invoices.setMinimumHeight(400)
        inv_v_layout.addWidget(self.table_invoices)

        # Quick Actions
        actions_card = QFrame()
        actions_card.setObjectName("Card")
        actions_card.setFixedWidth(320)
        act_v_layout = QVBoxLayout(actions_card)
        act_v_layout.setContentsMargins(25, 25, 25, 25)
        act_v_layout.setSpacing(15)
        
        act_title = QLabel("Quick Actions")
        act_title.setObjectName("SubHeader")
        act_v_layout.addWidget(act_title)
        act_v_layout.addSpacing(10)

        btn_bill = QPushButton("🛒 Create New Invoice")
        btn_bill.clicked.connect(lambda: self.controller.show_billing() if self.controller else None)
        act_v_layout.addWidget(btn_bill)

        btn_prod = QPushButton("📦 Add New Product")
        btn_prod.setObjectName("Secondary")
        btn_prod.clicked.connect(lambda: self.controller.show_products() if self.controller else None)
        act_v_layout.addWidget(btn_prod)

        btn_stock = QPushButton("📊 View Stock Ledger")
        btn_stock.setObjectName("Secondary")
        btn_stock.clicked.connect(lambda: self.controller.show_stock() if self.controller else None)
        act_v_layout.addWidget(btn_stock)
        
        act_v_layout.addStretch()
        
        tables_layout.addWidget(invoice_card, 2)
        tables_layout.addWidget(actions_card, 1)

        self.content_layout.addLayout(tables_layout)

    def load_data(self):
        conn = db.get_connection()
        cursor = conn.cursor()

        # Summary Stats
        cursor.execute("SELECT COUNT(*) FROM invoices")
        total_inv = cursor.fetchone()[0]
        self.card_invoices.val_lbl.setText(str(total_inv))

        cursor.execute("SELECT SUM(final_amount) FROM invoices WHERE DATE(date) = DATE('now')")
        today_sales = cursor.fetchone()[0] or 0
        self.card_sales.val_lbl.setText(f"₹{today_sales:,.2f}")
        
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE DATE(date) = DATE('now')")
        today_invoices_count = cursor.fetchone()[0] or 0
        self.card_sales.sub_lbl.setText(f"Based on {today_invoices_count} invoices today")
        
        cursor.execute("SELECT COUNT(*) FROM stock JOIN products ON stock.product_id = products.id WHERE products.is_active = 1 AND stock.quantity_available < 10")
        low_stock = cursor.fetchone()[0]
        self.card_stock.val_lbl.setText(str(low_stock))
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
        total_prod = cursor.fetchone()[0]
        self.card_products.val_lbl.setText(str(total_prod))

        # Recent Invoices Table
        cursor.execute("""
            SELECT i.invoice_no, c.full_name, i.final_amount, i.date
            FROM invoices i 
            JOIN customers c ON i.customer_id = c.id 
            ORDER BY i.date DESC LIMIT 10
        """)
        invoices = cursor.fetchall()
        self.table_invoices.setRowCount(len(invoices))
        for r, row in enumerate(invoices):
            self.table_invoices.setItem(r, 0, QTableWidgetItem(str(row[0])))
            self.table_invoices.setItem(r, 1, QTableWidgetItem(str(row[1])))
            self.table_invoices.setItem(r, 2, QTableWidgetItem(f"₹{row[2]:,.2f}"))
            date_str = row[3][:10] if row[3] else ''
            self.table_invoices.setItem(r, 3, QTableWidgetItem(date_str))
