from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from twinpay_tr.db.base import Base

class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    chaos_mode_enabled = Column(Boolean, default=True, nullable=False)
    error_rate = Column(Integer, default=0, nullable=False)
    delay_ms = Column(Integer, default=0, nullable=False)
    seed = Column(String, nullable=True)
