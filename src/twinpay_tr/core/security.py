import secrets
import hashlib
import hmac

def generate_api_key() -> tuple[str, str, str]:
    """
    Generates a new API key, its prefix (first 8 chars), and its SHA-256 hash.
    Returns: (api_key, prefix, hashed_key)
    """
    api_key = f"sk_test_{secrets.token_urlsafe(32)}"
    prefix = api_key[:16] # e.g. "sk_test_" + 8 characters
    
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key, prefix, hashed_key

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verifies a plain API key against its hashed version.
    """
    hashed_plain = hashlib.sha256(plain_api_key.encode()).hexdigest()
    return hmac.compare_digest(hashed_plain, hashed_api_key)
