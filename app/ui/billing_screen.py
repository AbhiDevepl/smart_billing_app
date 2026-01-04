from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QMessageBox, 
                               QRadioButton, QButtonGroup, QGridLayout, QScrollArea, QFrame)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
import os
import logging
from app.database import db
from app.services.invoice_service import InvoiceService
from app.services.whatsapp_service import WhatsAppService

class StepperWidget(QWidget):
    def __init__(self, steps):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.step_labels = []
        
        for i, step in enumerate(steps):
            lbl = QLabel(f"{i+1} {step}")
            lbl.setStyleSheet("""
                padding: 10px 20px;
                background-color: #f0f0f0;
                border-radius: 20px;
                font-weight: bold;
                color: #888;
            """)
            layout.addWidget(lbl)
            self.step_labels.append(lbl)
            if i < len(steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Plain)
                line.setStyleSheet("background-color: #ddd; max-height: 2px;")
                layout.addWidget(line, 1)

    def set_active_step(self, index):
        for i, lbl in enumerate(self.step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    padding: 10px 20px;
                    background-color: #2196F3;
                    border-radius: 20px;
                    font-weight: bold;
                    color: white;
                """)
            elif i < index:
                lbl.setStyleSheet("""
                    padding: 10px 20px;
                    background-color: #e3f2fd;
                    border-radius: 20px;
                    font-weight: bold;
                    color: #2196F3;
                """)

class BillingScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.invoice_service = InvoiceService()
        self.cart = []
        self.current_stock = 0
        self.setup_ui()
        self.load_product_list()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)

        # Header Section
        header_layout = QHBoxLayout()
        header = QLabel("New Invoice")
        header.setObjectName("SectionHeader")
        header_layout.addWidget(header)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # Stepper
        self.stepper = StepperWidget(["About you", "Product choice", "Invoice items", "Finalization"])
        self.stepper.set_active_step(0)
        self.main_layout.addWidget(self.stepper)

        # Scroll Area for the content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(scroll)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(40)
        scroll.setWidget(content_widget)

        # --- Section 1: Customer Details ---
        self.entry_mobile = QLineEdit()
        self.entry_mobile.setMaxLength(10)
        self.entry_mobile.setValidator(QRegularExpressionValidator(QRegularExpression(r"\d+")))
        self.entry_name = QLineEdit()
        self.entry_address = QLineEdit()
        
        self.content_layout.addWidget(self.create_card_section(
            "About you", 
            "Provide your customer contact information.",
            [
                ("Phone No*", self.entry_mobile),
                ("Full Name*", self.entry_name),
                ("Address", self.entry_address)
            ]
        ))
        self.entry_mobile.setPlaceholderText("10-digit number")
        self.entry_mobile.editingFinished.connect(self.on_mobile_leave)

        # --- Section 2: Product Addition ---
        self.combo_product = QComboBox()
        self.combo_product.setEditable(True)
        self.entry_price = QLineEdit()
        self.entry_qty = QLineEdit("1")
        
        self.content_layout.addWidget(self.create_card_section(
            "Product Choice", 
            "Select the battery or inverter model.",
            [
                ("Select Product*", self.combo_product),
                ("Selling Price (₹)", self.entry_price),
                ("Quantity", self.entry_qty),
            ],
            footer_widget=self.create_product_footer()
        ))
        self.combo_product.currentIndexChanged.connect(self.on_product_select)
        self.entry_qty.textChanged.connect(self.on_qty_change)

        # --- Section 3: Cart Table ---
        self.table = QTableWidget(0, 4)
        self.content_layout.addWidget(self.create_card_section(
            "Invoice Items", 
            "Review items being added to the bill.",
            [], 
            full_width_widget=self.table
        ))
        self.table.setHorizontalHeaderLabels(["PRODUCT", "QTY", "PRICE", "TOTAL"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(200)

        # --- Section 4: Exchange & Finalization ---
        self.entry_ex_val = QLineEdit("0")
        self.entry_ex_desc = QLineEdit()
        
        self.content_layout.addWidget(self.create_card_section(
            "Finalization", 
            "Apply deductions and generate the PDF invoice.",
            [
                ("Old Battery Value (Deduction)", self.entry_ex_val),
                ("Deduction Note", self.entry_ex_desc),
            ],
            footer_widget=self.create_final_footer()
        ))
        self.entry_ex_val.textChanged.connect(self.update_total)

    def create_card_section(self, title, desc, fields, footer_widget=None, full_width_widget=None):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(50)

        # Left Column: Header/Desc
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

    def create_product_footer(self):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 10, 0, 0)
        
        self.lbl_stock_badge = QLabel("-")
        self.lbl_stock_badge.hide()
        l.addWidget(self.lbl_stock_badge)
        
        l.addStretch()
        
        btn_add = QPushButton("Add to Cart")
        btn_add.clicked.connect(self.add_to_cart)
        l.addWidget(btn_add)
        return w

    def create_final_footer(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 20, 0, 0)
        
        total_row = QHBoxLayout()
        self.lbl_total = QLabel("Total: ₹0.00")
        self.lbl_total.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        total_row.addWidget(self.lbl_total)
        total_row.addStretch()
        l.addLayout(total_row)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("Secondary")
        btn_cancel.clicked.connect(lambda: self.controller.go_home() if self.controller else None)
        btn_row.addWidget(btn_cancel)
        
        btn_gen = QPushButton("Generate & Share")
        btn_gen.clicked.connect(self.generate_invoice)
        btn_row.addWidget(btn_gen)
        
        l.addLayout(btn_row)
        return w

    def load_product_list(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, brand_name, model_name, current_price, quantity_available FROM products JOIN stock ON products.id = stock.product_id")
        self.products = cursor.fetchall()
        self.prod_map = {}
        self.combo_product.clear()
        self.combo_product.addItem("Select Product...")
        for p in self.products:
            name = f"{p[1]} {p[2]} (₹{p[3]})"
            self.prod_map[name] = p
            self.combo_product.addItem(name)

    def on_product_select(self):
        name = self.combo_product.currentText()
        if name in self.prod_map:
            p = self.prod_map[name]
            self.current_stock = p[4]
            self.entry_price.setText(str(p[3]))
            self.update_stock_badge()
            self.on_qty_change()
            self.stepper.set_active_step(1)

    def update_stock_badge(self):
        self.lbl_stock_badge.show()
        if self.current_stock > 10:
            self.lbl_stock_badge.setText(f"IN STOCK: {self.current_stock}")
            self.lbl_stock_badge.setObjectName("BadgeSuccess")
        elif self.current_stock > 0:
            self.lbl_stock_badge.setText(f"LOW STOCK: {self.current_stock}")
            self.lbl_stock_badge.setObjectName("BadgeWarning")
        else:
            self.lbl_stock_badge.setText("OUT OF STOCK")
            self.lbl_stock_badge.setObjectName("BadgeDanger")
        self.lbl_stock_badge.style().unpolish(self.lbl_stock_badge)
        self.lbl_stock_badge.style().polish(self.lbl_stock_badge)

    def on_qty_change(self):
        try:
            qty = int(self.entry_qty.text() or 0)
            if qty > self.current_stock:
                self.lbl_stock_badge.setObjectName("BadgeDanger")
            else:
                self.update_stock_badge()
        except: pass

    def on_mobile_leave(self):
        mobile = self.entry_mobile.text().strip()
        if len(mobile) == 10:
            cursor = db.get_connection().cursor()
            cursor.execute("SELECT full_name, address FROM customers WHERE mobile_number = ?", (mobile,))
            row = cursor.fetchone()
            if row:
                self.entry_name.setText(row[0])
                self.entry_address.setText(row[1])
            self.stepper.set_active_step(1)

    def add_to_cart(self):
        name = self.combo_product.currentText()
        if name not in self.prod_map: return
        p = self.prod_map[name]
        try:
            qty = int(self.entry_qty.text())
            price = float(self.entry_price.text())
        except: return
        
        if qty > p[4]:
            QMessageBox.warning(self, "Stock Warning", f"Only {p[4]} available!")
            return
            
        self.cart.append({
            'product_id': p[0], 'product_name': f"{p[1]} {p[2]}",
            'qty': qty, 'selling_price': price, 'total': qty * price
        })
        self.refresh_cart_table()
        self.stepper.set_active_step(2)

    def refresh_cart_table(self):
        self.table.setRowCount(len(self.cart))
        for r, item in enumerate(self.cart):
            self.table.setItem(r, 0, QTableWidgetItem(item['product_name']))
            self.table.setItem(r, 1, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(r, 2, QTableWidgetItem(str(item['selling_price'])))
            self.table.setItem(r, 3, QTableWidgetItem(f"₹{item['total']:.2f}"))
        self.update_total()

    def update_total(self):
        subtotal = sum(i['total'] for i in self.cart)
        try: d = float(self.entry_ex_val.text() or 0)
        except: d = 0
        self.lbl_total.setText(f"Grand Total: ₹{subtotal - d:,.2f}")
        if self.cart:
            self.stepper.set_active_step(3)

    def generate_invoice(self):
        if not self.cart: return
        mobile = self.entry_mobile.text().strip()
        name = self.entry_name.text().strip()
        if not name or len(mobile) != 10:
            QMessageBox.warning(self, "Validation", "Need name and 10-digit mobile.")
            return
        
        subtotal = sum(i['total'] for i in self.cart)
        try: ex_v = float(self.entry_ex_val.text() or 0)
        except: ex_v = 0
        
        try:
            inv_no, pdf_path = self.invoice_service.create_invoice(
                {'name': name, 'mobile': mobile, 'address': self.entry_address.text()},
                self.cart, {'amount': ex_v, 'description': self.entry_ex_desc.text()}
            )
            QMessageBox.information(self, "Success", f"Invoice {inv_no} Generated!")
            if os.path.exists(pdf_path): os.startfile(pdf_path)
            self.cart = []; self.refresh_cart_table(); self.load_product_list()
            self.stepper.set_active_step(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
