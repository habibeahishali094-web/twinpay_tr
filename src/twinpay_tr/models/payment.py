from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime, timezone
from twinpay_tr.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="TRY", nullable=False)
    status = Column(String, default="pending", nullable=False)
    card_mask = Column(String, nullable=False)
    installments = Column(Integer, default=1, nullable=False)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
