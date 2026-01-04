from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QFrame, 
                               QScrollArea, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator, QIntValidator
from app.database import db

class ProductForm(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # Header
        header = QLabel("Product Management")
        header.setObjectName("SectionHeader")
        self.main_layout.addWidget(header)

        # Scroll Area for long forms
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(30)
        scroll.setWidget(content)

        # --- Section 1: Identification ---
        self.entry_qr = QLineEdit()
        self.entry_qr.setPlaceholderText("Scan or enter QR Code")
        self.entry_category = QComboBox()
        self.entry_category.addItems(["Battery", "Inverter", "Solar Panel", "Cable", "Other"])
        
        self.content_layout.addWidget(self.create_card_section(
            "Product Identity", 
            "Enter the tracking and classification details for this item.",
            [
                ("QR Code*", self.entry_qr),
                ("Category*", self.entry_category)
            ]
        ))

        # --- Section 2: Model Details ---
        self.entry_brand = QLineEdit()
        self.entry_brand.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z\s]*$")))
        self.entry_model = QLineEdit()
        self.entry_warranty = QLineEdit()
        self.entry_warranty.setValidator(QIntValidator(0, 999))
        self.entry_warranty.setPlaceholderText("Months")
        
        self.content_layout.addWidget(self.create_card_section(
            "Model Specification", 
            "Specify the manufacturer, model name, and warranty period.",
            [
                ("Brand Name*", self.entry_brand),
                ("Model Name*", self.entry_model),
                ("Warranty (Months)", self.entry_warranty)
            ]
        ))

        # --- Section 3: Pricing & Stock ---
        self.entry_price = QLineEdit()
        self.entry_price.setValidator(QIntValidator(0, 999999))
        self.entry_stock = QLineEdit("0")
        self.entry_stock.setValidator(QIntValidator(0, 9999))
        
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

        # Left Column: Info
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

        # Right Column: Fields
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
        
        self.btn_delete = QPushButton("Delete Product")
        self.btn_delete.setObjectName("Danger")
        self.btn_delete.clicked.connect(self.delete_product)
        l.addWidget(self.btn_delete)
        
        l.addStretch()
        
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("Secondary")
        btn_clear.clicked.connect(self.clear_form)
        l.addWidget(btn_clear)
        
        self.btn_save = QPushButton("Save Product")
        self.btn_save.clicked.connect(self.save_product)
        l.addWidget(self.btn_save)
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
                    UPDATE products 
                    SET category = ?, brand_name = ?, model_name = ?, warranty_months = ?, current_price = ?, is_active = 1
                    WHERE id = ?
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
        if not qr: 
            QMessageBox.warning(self, "Input Error", "Please enter a QR code to delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm", "Really delete this product and its stock?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM products WHERE qr_code = ?", (qr,))
            row = cursor.fetchone()
            if row:
                pid = row[0]
                cursor.execute("UPDATE products SET is_active = 0 WHERE id = ?", (pid,))
                conn.commit()
                QMessageBox.information(self, "Deleted", "Product has been archived and removed from active lists.")
                self.clear_form()
            else:
                QMessageBox.warning(self, "Not Found", "No product found with this QR code.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def clear_form(self):
        for w in [self.entry_qr, self.entry_brand, self.entry_model, self.entry_warranty, self.entry_price]:
            w.clear()
        self.entry_stock.setText("0")
        self.entry_category.setCurrentIndex(0)

    def load_data(self):
        self.clear_form()
