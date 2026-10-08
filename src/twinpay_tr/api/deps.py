from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import hashlib

from twinpay_tr.db.session import SessionLocal
from twinpay_tr.models.user import User
from twinpay_tr.core.security import verify_api_key

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

security = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    api_key = credentials.credentials
    hashed_incoming = hashlib.sha256(api_key.encode()).hexdigest()
    
    user = db.query(User).filter(User.api_key_hash == hashed_incoming).first()
    
    if not user or not verify_api_key(api_key, user.api_key_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz API Anahtarı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_user_id(current_user: User = Depends(get_current_user)) -> int:
    """
    İzolasyon Kuralı: Tüm işlemler bu ID kullanılarak filtrelenmelidir.
    """
    return current_user.id
