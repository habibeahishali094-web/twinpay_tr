from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from twinpay_tr.api import deps
from twinpay_tr.models.payment import Payment
from twinpay_tr.models.webhook import WebhookEndpoint
from twinpay_tr.models.idempotency import IdempotencyKey
from twinpay_tr.models.settings import Settings
from twinpay_tr.models.scenario import Scenario

router = APIRouter()

@router.post("/reset")
def reset_sandbox(
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    db.query(Scenario).filter(Scenario.user_id == user_id).delete()
    db.query(Settings).filter(Settings.user_id == user_id).delete()
    db.query(Payment).filter(Payment.user_id == user_id).delete()
    db.query(WebhookEndpoint).filter(WebhookEndpoint.user_id == user_id).delete()
    db.query(IdempotencyKey).filter(IdempotencyKey.user_id == user_id).delete()
    db.commit()
    return {"message": "Sandbox verileriniz başarıyla sıfırlandı."}
