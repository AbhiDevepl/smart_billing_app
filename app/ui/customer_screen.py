from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QFrame, QScrollArea, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt
from app.database import db

class CustomerScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # Header
        header = QLabel("Customer Directory")
        header.setObjectName("SectionHeader")
        self.main_layout.addWidget(header)

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

        # --- Section 1: Search & Filter ---
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText("Search by name or phone number...")
        self.entry_search.textChanged.connect(self.on_search)
        
        self.content_layout.addWidget(self.create_card_section(
            "Lookup Customers", 
            "Quickly find a customer's record to view their details or address.",
            [
                ("Quick Search", self.entry_search)
            ],
            footer_widget=self.create_search_footer()
        ))

        # --- Section 2: Customer Table ---
        self.table_customers = QTableWidget(0, 4)
        self.table_customers.setHorizontalHeaderLabels(["ID", "NAME", "PHONE", "ADDRESS"])
        self.table_customers.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_customers.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_customers.setSelectionMode(QTableWidget.SingleSelection)
        self.table_customers.setMinimumHeight(500)
        
        self.content_layout.addWidget(self.create_card_section(
            "Registered Records", 
            "A complete listing of all customers stored in the system.",
            [], 
            full_width_widget=self.table_customers
        ))

    def create_card_section(self, title, desc, fields, footer_widget=None, full_width_widget=None):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(50)

        # Left Column
        left_col = QVBoxLayout()
        h = QLabel(title)
        h.setObjectName("SubHeader")
        left_col.addWidget(h)
        
        d = QLabel(desc)
        d.setObjectName("Description")
        d.setWordWrap(True)
        left_col.addWidget(d)
        left_col.addStretch()
        card_layout.addLayout(left_col, 1)

        # Right Column
        right_col = QVBoxLayout()
        if fields:
            grid = QGridLayout()
            grid.setSpacing(15)
            for i, (label_text, widget) in enumerate(fields):
                grid.addWidget(QLabel(label_text), i, 0)
                grid.addWidget(widget, i, 1)
            right_col.addLayout(grid)
            
        if full_width_widget:
            right_col.addWidget(full_width_widget)
            
        if footer_widget:
            right_col.addWidget(footer_widget)
            
        card_layout.addLayout(right_col, 2)
        return card

    def create_search_footer(self):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 10, 0, 0)
        
        btn_refresh = QPushButton("Refresh List")
        btn_refresh.setObjectName("Secondary")
        btn_refresh.clicked.connect(self.load_data)
        l.addWidget(btn_refresh)
        
        l.addStretch()
        
        btn_new_bill = QPushButton("🛒 New Bill for Selected")
        btn_new_bill.clicked.connect(self.start_bill_for_selected)
        l.addWidget(btn_new_bill)
        return w

    def load_data(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, mobile_number, address FROM customers ORDER BY full_name ASC")
        rows = cursor.fetchall()
        self.render_table(rows)

    def render_table(self, rows):
        self.table_customers.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.table_customers.setItem(r, c, QTableWidgetItem(str(val)))

    def on_search(self):
        query = self.entry_search.text().strip()
        conn = db.get_connection()
        cursor = conn.cursor()
        if not query:
            self.load_data()
            return
            
        cursor.execute("""
            SELECT id, full_name, mobile_number, address FROM customers 
            WHERE full_name LIKE ? OR mobile_number LIKE ?
            ORDER BY full_name ASC
        """, (f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        self.render_table(rows)

    def start_bill_for_selected(self):
        row = self.table_customers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a customer from the table.")
            return
            
        phone = self.table_customers.item(row, 2).text()
        if self.controller:
            self.controller.show_billing()
            # If billing screen is already in cache
            if 'billing' in self.controller.screens:
                bill_screen = self.controller.screens['billing']
                bill_screen.entry_mobile.setText(phone)
                bill_screen.on_mobile_leave()
