from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QGroupBox, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QMessageBox, QFormLayout, QGridLayout)
from PySide6.QtCore import Qt
import logging
from app.database import db

class ProductForm(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        
        # Title
        lbl_title = QLabel("Product Management")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(lbl_title)

        # Form Group
        form_group = QGroupBox("Add / Edit Product")
        form_layout = QGridLayout(form_group)
        
        form_layout.addWidget(QLabel("QR Code:"), 0, 0)
        self.entry_qr = QLineEdit()
        form_layout.addWidget(self.entry_qr, 0, 1)
        
        form_layout.addWidget(QLabel("Category:"), 0, 2)
        self.combo_category = QComboBox()
        self.combo_category.addItems(["Battery", "Inverter"])
        form_layout.addWidget(self.combo_category, 0, 3)
        
        form_layout.addWidget(QLabel("Brand:"), 1, 0)
        self.entry_brand = QLineEdit()
        form_layout.addWidget(self.entry_brand, 1, 1)
        
        form_layout.addWidget(QLabel("Model:"), 1, 2)
        self.entry_model = QLineEdit()
        form_layout.addWidget(self.entry_model, 1, 3)
        
        form_layout.addWidget(QLabel("Warranty (Mo):"), 2, 0)
        self.entry_warranty = QLineEdit()
        form_layout.addWidget(self.entry_warranty, 2, 1)
        
        form_layout.addWidget(QLabel("Selling Price:"), 2, 2)
        self.entry_price = QLineEdit()
        form_layout.addWidget(self.entry_price, 2, 3)
        
        form_layout.addWidget(QLabel("Opening Stock:"), 3, 0)
        self.entry_stock = QLineEdit("0")
        form_layout.addWidget(self.entry_stock, 3, 1)

        # Buttons Row
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Product")
        self.btn_save.clicked.connect(self.save_product)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_delete = QPushButton("Delete Product")
        self.btn_delete.setObjectName("danger")
        
        self.content_layout.addWidget(self.create_card_section(
            "Inventory & Pricing", 
            "Set the current market price and initial stock level.",
            [
                ("Current Price (₹)*", self.entry_price),
                ("Opening Stock", self.entry_stock)
            ],
            footer_widget=self.create_form_footer()
        ))

    def create_card_section(self, title, desc, fields, footer_widget=None):
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
        grid = QGridLayout()
        grid.setSpacing(15)
        for i, (label_text, widget) in enumerate(fields):
            grid.addWidget(QLabel(label_text), i, 0)
            grid.addWidget(widget, i, 1)
        right_col.addLayout(grid)
            
        if footer_widget:
            right_col.addWidget(footer_widget)
            
        card_layout.addLayout(right_col, 2)
        return card

    def create_form_footer(self):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 20, 0, 0)
        
        btn_delete = QPushButton("Delete Product")
        btn_delete.setObjectName("Danger")
        btn_delete.clicked.connect(self.delete_product)
        l.addWidget(btn_delete)
        
        l.addStretch()
        
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("Secondary")
        btn_clear.clicked.connect(self.clear_form)
        l.addWidget(btn_clear)
        
        btn_save = QPushButton("Save Product")
        btn_save.clicked.connect(self.save_product)
        l.addWidget(btn_save)
        return w

    def save_product(self):
        qr = self.entry_qr.text().strip()
        cat = self.entry_category.currentText()
        brand = self.entry_brand.text().strip()
        model = self.entry_model.text().strip()
        
        if not qr or not brand or not model:
            QMessageBox.warning(self, "Validation", "Please fill mandatory fields (*)")
            return
            
        try:
            warranty = int(self.entry_warranty.text() or 0)
            price = float(self.entry_price.text() or 0)
            opening_stock = int(self.entry_stock.text() or 0)
        except:
            QMessageBox.warning(self, "Error", "Numeric fields are invalid.")
            return

        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM products WHERE qr_code = ?", (qr,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("""
                    UPDATE products SET category=?, brand_name=?, model_name=?, warranty_months=?, current_price=? 
                    WHERE id=?
                """, (cat, brand, model, warranty, price, existing[0]))
            else:
                cursor.execute("""
                    INSERT INTO products (qr_code, category, brand_name, model_name, warranty_months, current_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (qr, cat, brand, model, warranty, price))
                pid = cursor.lastrowid
                cursor.execute("INSERT INTO stock (product_id, quantity_available) VALUES (?, ?)", (pid, opening_stock))
            conn.commit()
            QMessageBox.information(self, "Success", "Product Saved!")
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def delete_product(self):
        qr = self.entry_qr.text().strip()
        if not qr: return
        
        reply = QMessageBox.question(self, "Confirm", "Really delete this product and its stock?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM products WHERE qr_code = ?", (qr,))
            row = cursor.fetchone()
            if row:
                pid = row[0]
                # Check if linked to invoices
                cursor.execute("SELECT COUNT(*) FROM invoice_items WHERE product_id = ?", (pid,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Cannot Delete", "Product is linked to existing invoices.")
                    return
                cursor.execute("DELETE FROM stock WHERE product_id = ?", (pid,))
                cursor.execute("DELETE FROM products WHERE id = ?", (pid,))
                conn.commit()
                QMessageBox.information(self, "Deleted", "Product removed.")
                self.clear_form()
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))

    def clear_form(self):
        for entry in [self.entry_qr, self.entry_brand, self.entry_model, self.entry_warranty, self.entry_price]:
            entry.clear()
        self.entry_stock.setText("0")
        self.table.clearSelection()
        self.btn_delete.setEnabled(False)
