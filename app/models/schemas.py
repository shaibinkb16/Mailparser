from typing import Optional, List
from pydantic import BaseModel, Field

class PurchaseOrderRequest(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    amount_due: Optional[str] = None
    payment_method: Optional[str] = None
    reference: Optional[str] = None

    # Changed invalid keys to valid Python identifiers using `alias`
    service: Optional[str] = Field(default=None, alias="-_service")
    hours: Optional[str] = Field(default=None, alias="-_hours")
    rate: Optional[str] = Field(default=None, alias="-_rate")

    account_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    bank: Optional[str] = None
    tel: Optional[str] = None
    important: Optional[str] = None
    email_subject: Optional[str] = None
    id: Optional[str] = None
    received_at: Optional[str] = None
    received_at_timestamp: Optional[int] = None
    received_at_iso8601: Optional[str] = None
    processed_at: Optional[str] = None
    processed_at_timestamp: Optional[int] = None
    processed_at_iso8601: Optional[str] = None

    class Config:
        allow_population_by_field_name = True  # Needed to allow alias fields to be populated


class ProcessedOrder(BaseModel):
    po_number: Optional[str] = None
    customer: Optional[str] = None
    items: Optional[List[str]] = []  # typed properly
    total: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None
