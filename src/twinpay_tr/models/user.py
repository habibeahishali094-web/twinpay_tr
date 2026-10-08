from sqlalchemy import Column, Integer, String
from twinpay_tr.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    api_key_prefix = Column(String, nullable=False)
    api_key_hash = Column(String, unique=True, nullable=False)
