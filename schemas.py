from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
import re

class Address(BaseModel):
    company: Optional[str] = Field(None)
    contact_person: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    attention: Optional[str] = Field(None)

class LineItem(BaseModel):
    item_code: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    quantity: Optional[Union[int, float]] = Field(None)
    unit_price: Optional[Union[float, str]] = Field(None)
    total: Optional[Union[float, str]] = Field(None)

    @validator('quantity', 'unit_price', 'total', pre=True)
    def convert_numbers(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            cleaned = re.sub(r'[^\d.]', '', v)
            return float(cleaned) if cleaned else None
        return v

class PartialInvoiceData(BaseModel):
    po_number: Optional[str] = Field(None)
    po_date: Optional[str] = Field(None)
    billing_info: Optional[Address] = Field(None)
    shipping_info: Optional[Address] = Field(None)
    line_items: Optional[List[LineItem]] = Field(None)
    subtotal: Optional[Union[float, str]] = Field(None)
    tax: Optional[Union[float, str]] = Field(None)
    tax_rate: Optional[str] = Field(None)
    shipping: Optional[Union[float, str]] = Field(None)
    total_amount: Optional[Union[float, str]] = Field(None)
    payment_terms: Optional[str] = Field(None)
    delivery_date: Optional[str] = Field(None)
    special_instructions: Optional[str] = Field(None)
    manager_approval: Optional[Union[str, dict]] = Field(None)
    budget_code: Optional[str] = Field(None)
    vendor_info: Optional[dict] = Field(None)
    buyer_info: Optional[dict] = Field(None)

    @validator('subtotal', 'tax', 'shipping', 'total_amount', pre=True)
    def convert_amounts(cls, v):
        return LineItem.convert_numbers(v)

class InvoiceData(PartialInvoiceData):
    """Strict version with required fields"""
    po_number: str = Field(...)
    po_date: str = Field(...)
    billing_info: Address = Field(...)
    line_items: List[LineItem] = Field(...)
    total_amount: Union[float, str] = Field(...)