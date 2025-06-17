from typing import List, Optional
from pydantic import BaseModel

class InvoiceItem(BaseModel):
    item_code: Optional[str]
    description: str
    quantity: int
    unit_price: float
    line_total: float

class ExtractedInvoice(BaseModel):
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    due_date: Optional[str]
    payment_terms: Optional[str]
    vendor: Optional[str]
    buyer: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    shipping_address: Optional[str]
    billing_address: Optional[str]
    items: List[InvoiceItem]
    subtotal: Optional[float]
    tax: Optional[float]
    shipping_charges: Optional[float]
    total: Optional[float]
    delivery_date: Optional[str]
    budget_code: Optional[str]
    approval_manager: Optional[str]
