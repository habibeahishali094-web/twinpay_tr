from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    amount: float
    currency: str = "TRY"
    card_number: str
    expiry_month: str
    expiry_year: str
    cvc: str

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    amount: float
    currency: str
    status: str
    card_mask: str
    created_at: datetime

class PaymentCapture(BaseModel):
    amount: Optional[float] = None
