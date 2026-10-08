from urllib.parse import urlparse
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from twinpay_tr.api import deps
from twinpay_tr.models.webhook import WebhookEndpoint
from twinpay_tr.schemas.webhook import WebhookEndpointCreate, WebhookEndpointResponse
from typing import List

router = APIRouter()

def validate_webhook_url(url: str):
    try:
        parsed = urlparse(str(url))
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            raise HTTPException(status_code=400, detail="Localhost veya iç ağ IP'leri webhook olarak kullanılamaz (SSRF koruması).")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Geçersiz URL formatı")

@router.post("/", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook_in: WebhookEndpointCreate,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    validate_webhook_url(webhook_in.url)
    endpoint = WebhookEndpoint(user_id=user_id, url=webhook_in.url)
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint

@router.get("/", response_model=List[WebhookEndpointResponse])
def get_webhooks(
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    return db.query(WebhookEndpoint).filter(WebhookEndpoint.user_id == user_id).all()
