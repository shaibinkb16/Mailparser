from pydantic import BaseModel
from typing import List, Optional, Dict

class Item(BaseModel):
    name: str
    quantity: int

class ProcessedOrder(BaseModel):
    po_number: Optional[str] = None
    customer: Optional[str] = None
    items: Optional[List[Item]] = []
    total: Optional[float] = None
    source: str
    email_metadata: Dict[str, str]
    filename: Optional[str] = None
    status: Optional[str] = "success"
    note: Optional[str] = None