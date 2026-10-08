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
    installments: int = 1
    require_3d_secure: bool = False

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    amount: float
    currency: str
    status: str
    card_mask: str
    installments: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    three_d_secure_url: Optional[str] = None
    formatted_amount: Optional[str] = None
    formatted_date: Optional[str] = None

class PaymentCapture(BaseModel):
    amount: Optional[float] = None

class Complete3DSecure(BaseModel):
    success: bool
    error_code: Optional[str] = None
