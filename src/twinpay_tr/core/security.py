import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_api_key() -> tuple[str, str, str]:
    raw_api_key = f"twp_{secrets.token_urlsafe(32)}"
    prefix = raw_api_key[:8]
    hashed_key = get_password_hash(raw_api_key)
    return raw_api_key, prefix, hashed_key

def verify_api_key(api_key: str, hashed_key: str) -> bool:
    return verify_password(api_key, hashed_key)
