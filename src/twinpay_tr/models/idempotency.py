from sqlalchemy import Column, Integer, String, ForeignKey
from twinpay_tr.db.base import Base

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String, nullable=False, index=True)
    response_status_code = Column(Integer, nullable=False)
    response_body = Column(String, nullable=False)
