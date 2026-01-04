from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Product:
    id: Optional[int]
    qr_code: str
    category: str
    brand_name: str
    model_name: str
    warranty_months: int
    current_price: float
    current_purchase_price: float = 0.0
    last_updated: Optional[datetime] = None

@dataclass
class Customer:
    id: Optional[int]
    full_name: str
    mobile_number: str
    address: str

@dataclass
class InvoiceItem:
    id: Optional[int]
    invoice_no: str
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

@dataclass
class Invoice:
    invoice_no: str
    customer_id: int
    total_amount: float
    old_battery_value: float
    final_amount: float
    old_battery_description: str = ""
    date: Optional[datetime] = None
    items: List[InvoiceItem] = None

@dataclass
class Purchase:
    id: Optional[int]
    distributor_name: str
    product_id: int
    quantity: int
    purchase_price: float
    date: Optional[datetime] = None

@dataclass
class Stock:
    product_id: int
    quantity_available: int
    last_updated: Optional[datetime] = None
