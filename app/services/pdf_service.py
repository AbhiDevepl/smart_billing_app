import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.config import Config

class PDFService:
    @staticmethod
    def generate_invoice_pdf(invoice_data, cart_items, old_battery, file_path):
        """
        invoice_data: dict(invoice_no, date, customer_name, customer_mobile, customer_address, total, old_val, final)
        cart_items: list of dict(product_name, qty, price, total)
        old_battery: dict(amount, description)
        file_path: absolute path to save the PDF
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph(Config.APP_TITLE, styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Header Info
        header_data = [
            [f"Invoice No: {invoice_data['invoice_no']}", f"Date: {invoice_data['date']}"],
            [f"Customer: {invoice_data['customer_name']}", f"Mobile: {invoice_data['customer_mobile']}"],
            [f"Address: {invoice_data['customer_address']}", ""]
        ]
        header_table = Table(header_data, colWidths=[250, 200])
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Items Table
        data = [['Product', 'Qty', 'Unit Price', 'Total']]
        for item in cart_items:
            data.append([
                item['product_name'],
                str(item['qty']),
                f"₹{item['selling_price']:.2f}",
                f"₹{item['total']:.2f}"
            ])
            
        data.append(["", "", "Subtotal:", f"₹{invoice_data['total']:.2f}"])
        if old_battery['amount'] > 0:
            data.append(["", "", f"Old Battery ({old_battery['description']}):", f"-₹{old_battery['amount']:.2f}"])
        data.append(["", "", "Grand Total:", f"₹{invoice_data['final']:.2f}"])
        
        table = Table(data, colWidths=[250, 50, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(table)
        
        # Footer
        elements.append(Spacer(1, 50))
        elements.append(Paragraph("Thank you for your business!", styles['Italic']))
        
        doc.build(elements)
        return file_path
