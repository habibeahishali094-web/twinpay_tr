from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from twinpay_tr.api import deps
from twinpay_tr.models.webhook import WebhookEndpoint
from twinpay_tr.schemas.webhook import WebhookEndpointCreate, WebhookEndpointResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook_in: WebhookEndpointCreate,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
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
