from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QFrame, QScrollArea, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt
from app.database import db

class StockScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # Header
        header = QLabel("Stock & Inventory Ledger")
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

        # --- Section 1: Search & Lookup ---
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText("Enter QR code, Brand or Model name...")
        self.entry_search.textChanged.connect(self.on_search)
        
        self.content_layout.addWidget(self.create_card_section(
            "Search & Scan", 
            "Quickly find a product by scanning its QR code or searching by name.",
            [
                ("Quick Search", self.entry_search)
            ],
            footer_widget=self.create_search_footer()
        ))

        # --- Section 2: Stock Ledger ---
        self.table_stock = QTableWidget(0, 5)
        self.table_stock.setHorizontalHeaderLabels(["ID", "PRODUCT", "CATEGORY", "QR CODE", "AVAILABLE"])
        self.table_stock.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_stock.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_stock.setSelectionMode(QTableWidget.SingleSelection)
        self.table_stock.setMinimumHeight(500)
        
        self.content_layout.addWidget(self.create_card_section(
            "Inventory Ledger", 
            "View and manage current stock levels across all registered items.",
            [], 
            full_width_widget=self.table_stock
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
        
        btn_add = QPushButton(" + Register New Product")
        btn_add.clicked.connect(lambda: self.controller.show_products() if self.controller else None)
        l.addWidget(btn_add)
        
        l.addStretch()
        
        btn_refresh = QPushButton("Refresh Table")
        btn_refresh.setObjectName("Secondary")
        btn_refresh.clicked.connect(self.load_data)
        l.addWidget(btn_refresh)

        btn_delete = QPushButton("🗑️ Delete Selected")
        btn_delete.setObjectName("Danger")
        btn_delete.clicked.connect(self.delete_selected)
        l.addWidget(btn_delete)
        return w

    def load_data(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.brand_name || ' ' || p.model_name, p.category, p.qr_code, s.quantity_available 
            FROM products p
            JOIN stock s ON p.id = s.product_id
            WHERE p.is_active = 1
            ORDER BY s.quantity_available ASC
        """)
        rows = cursor.fetchall()
        self.render_table(rows)

    def render_table(self, rows):
        self.table_stock.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if c == 4: # Stock Column
                    qty = int(val)
                    if qty < 10: item.setForeground(Qt.red)
                self.table_stock.setItem(r, c, item)

    def on_search(self):
        query = self.entry_search.text().strip()
        if not query:
            self.load_data()
            return
            
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.brand_name || ' ' || p.model_name, p.category, p.qr_code, s.quantity_available 
            FROM products p
            JOIN stock s ON p.id = s.product_id
            WHERE p.is_active = 1 AND (p.qr_code LIKE ? OR p.brand_name LIKE ? OR p.model_name LIKE ?)
            ORDER BY s.quantity_available ASC
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        
        if not rows and len(query) > 5: # Likely a QR code scan
            reply = QMessageBox.question(self, "QR Code Not Found", 
                                          f"The code '{query}' is not in the system. \n\nWould you like to register this as a new product?",
                                          QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes and self.controller:
                self.controller.show_products()
                # Pre-fill the QR in the product form
                if 'products' in self.controller.screens:
                    self.controller.screens['products'].entry_qr.setText(query)
            return

        self.render_table(rows)

    def delete_selected(self):
        row = self.table_stock.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a product from the table to delete.")
            return
            
        pid_item = self.table_stock.item(row, 0)
        pname_item = self.table_stock.item(row, 1)
        
        if not pid_item or not pname_item:
            return
            
        pid = pid_item.text()
        pname = pname_item.text()
        
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                      f"Are you sure you want to delete '{pname}' (ID: {pid})? \n\nThis will remove all stock records for this product.",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
            
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            # Archiving instead of hard deleting for safety and history
            cursor.execute("UPDATE products SET is_active = 0 WHERE id = ?", (pid,))
            conn.commit()
            
            QMessageBox.information(self, "Deleted", f"Product '{pname}' has been successfully archived and removed from active views.")
            self.load_data()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to archive product: {str(e)}")
