import random
import time
import os
from app.database import db
from app.models import Invoice, InvoiceItem

class InvoiceService:
    @staticmethod
    def generate_invoice_number():
        # Format: INV-YYYYMMDD-XXXX
        date_str = time.strftime("%Y%m%d")
        rand_str = str(random.randint(1000, 9999))
        return f"INV-{date_str}-{rand_str}"

    @staticmethod
    def get_or_create_customer(full_name, mobile, address):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM customers WHERE mobile_number = ?", (mobile,))
        res = cursor.fetchone()
        
        if res:
            return res[0]
        else:
            cursor.execute("INSERT INTO customers (full_name, mobile_number, address) VALUES (?, ?, ?)", 
                           (full_name, mobile, address))
            conn.commit()
            return cursor.lastrowid

    def create_invoice(self, customer_data, cart_items, old_battery_data):
        """
        customer_data: dict(name, mobile, address)
        cart_items: list of dict(product_id, qty, selling_price, product_name)
        old_battery_data: dict(amount, description)
        """
        conn = db.get_connection()
        try:
            cart_total = sum(item['qty'] * item['selling_price'] for item in cart_items)
            old_battery_amount = old_battery_data.get('amount', 0.0)
            old_battery_desc = old_battery_data.get('description', '')
            final_amount = cart_total - old_battery_amount
            
            # rule: final amount >= 0
            if final_amount < 0:
                raise Exception("Final amount cannot be negative. Deduction exceeds total.")

            customer_id = self.get_or_create_customer(
                customer_data['name'], 
                customer_data['mobile'], 
                customer_data['address']
            )
            
            invoice_no = self.generate_invoice_number()
            date_now = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Start Transaction
            cursor = conn.cursor()
            
            # 1. Insert Invoice Header
            cursor.execute("""
                INSERT INTO invoices (invoice_no, customer_id, total_amount, old_battery_value, old_battery_description, final_amount, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (invoice_no, customer_id, cart_total, old_battery_amount, old_battery_desc, final_amount, date_now))

            # 2. Process Items
            for item in cart_items:
                pid = item['product_id']
                qty = item['qty']
                price = item['selling_price']
                total_line_price = qty * price
                
                # Check Stock
                cursor.execute("SELECT quantity_available FROM stock WHERE product_id = ?", (pid,))
                stock_res = cursor.fetchone()
                if not stock_res or stock_res[0] < qty:
                    raise Exception(f"Insufficient Stock for Product ID: {pid}")
                
                # Deduct Stock
                cursor.execute("UPDATE stock SET quantity_available = quantity_available - ? WHERE product_id = ?", (qty, pid))
                
                # Insert Invoice Item
                cursor.execute("""
                    INSERT INTO invoice_items (invoice_no, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (invoice_no, pid, qty, price, total_line_price))
            
            # 3. Generate PDF 
            from app.services.pdf_service import PDFService
            from app.config import Config
            import re

            def sanitize(text):
                return re.sub(r'[^\w\-_\. ]', '_', str(text)).replace(' ', '_')

            cust_name_clean = sanitize(customer_data['name'])
            # Use first product name for the filename
            prod_name_clean = sanitize(cart_items[0]['product_name']) if cart_items else "NoProduct"
            time_stamp = time.strftime("%Y%m%d_%H%M%S")
            date_folder_name = time.strftime("%Y-%m-%d")
            
            daily_folder = os.path.join(Config.INVOICE_DIR, date_folder_name)
            os.makedirs(daily_folder, exist_ok=True)
            
            filename = f"{cust_name_clean}_{prod_name_clean}_{time_stamp}.pdf"
            pdf_path = os.path.join(daily_folder, filename)
            
            inv_data_for_pdf = {
                'invoice_no': invoice_no,
                'date': date_now,
                'customer_name': customer_data['name'],
                'customer_mobile': customer_data['mobile'],
                'customer_address': customer_data['address'],
                'total': cart_total,
                'old_val': old_battery_amount,
                'final': final_amount
            }
            
            PDFService.generate_invoice_pdf(inv_data_for_pdf, cart_items, old_battery_data, pdf_path)
            
            conn.commit()
            return invoice_no, pdf_path

        except Exception as e:
            conn.rollback()
            raise e
