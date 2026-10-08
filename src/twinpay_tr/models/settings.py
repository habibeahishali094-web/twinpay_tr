from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from twinpay_tr.db.base import Base

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    language = Column(String, default="tr", nullable=False)
    chaos_mode_enabled = Column(Boolean, default=False, nullable=False)
    error_rate = Column(Integer, default=0, nullable=False)
    delay_ms = Column(Integer, default=0, nullable=False)
    seed = Column(String, nullable=True)
