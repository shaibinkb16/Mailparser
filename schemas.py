from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re

class Address(BaseModel):
    company: str
    contact_person: Optional[str] = Field(None, description="Contact person name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    address: str
    attention: Optional[str] = Field(None, description="Attention line")

class LineItem(BaseModel):
    item_code: Optional[str] = Field(None, description="Item code/SKU")
    description: str
    quantity: int
    unit_price: float
    total: float

    @validator('quantity', 'unit_price', 'total', pre=True)
    def convert_numbers(cls, v):
        if isinstance(v, str):
            # Remove commas and dollar signs
            cleaned = re.sub(r'[^\d.]', '', v)
            return float(cleaned) if cleaned else 0.0
        return v

class InvoiceData(BaseModel):
    po_number: str = Field(..., description="Purchase order number")
    po_date: str
    billing_info: Address
    shipping_info: Address
    line_items: List[LineItem]
    subtotal: float
    tax: float
    tax_rate: Optional[str] = Field(None, description="Tax rate percentage")
    shipping: float
    total_amount: float
    payment_terms: str
    delivery_date: str
    special_instructions: Optional[str] = None
    manager_approval: Optional[str] = None
    budget_code: Optional[str] = None
    vendor_info: Optional[dict] = Field(None, description="Vendor information")
    buyer_info: Optional[dict] = Field(None, description="Buyer information")