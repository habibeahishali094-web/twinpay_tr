import json
from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks, status, Response
from sqlalchemy.orm import Session
from typing import Optional

from twinpay_tr.api import deps
from twinpay_tr.models.payment import Payment
from twinpay_tr.models.idempotency import IdempotencyKey
from twinpay_tr.schemas.payment import PaymentCreate, PaymentResponse
from twinpay_tr.core.webhook import schedule_webhook

router = APIRouter()

def get_idempotency_response(db: Session, user_id: int, key: str):
    return db.query(IdempotencyKey).filter(
        IdempotencyKey.user_id == user_id,
        IdempotencyKey.key == key
    ).first()

def save_idempotency_response(db: Session, user_id: int, key: str, status_code: int, response_body: dict):
    if key:
        idem = IdempotencyKey(
            user_id=user_id,
            key=key,
            response_status_code=status_code,
            response_body=json.dumps(response_body)
        )
        db.add(idem)
        db.commit()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: PaymentCreate,
    background_tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    if idempotency_key:
        existing = get_idempotency_response(db, user_id, idempotency_key)
        if existing:
            response.status_code = existing.response_status_code
            return json.loads(existing.response_body)
    
    card_mask = f"**** **** **** {payment_in.card_number[-4:]}" if len(payment_in.card_number) >= 4 else "****"
    
    new_payment = Payment(
        user_id=user_id,
        amount=payment_in.amount,
        currency=payment_in.currency,
        status="authorized",
        card_mask=card_mask,
        idempotency_key=idempotency_key
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    resp_data = PaymentResponse.model_validate(new_payment).model_dump()
    resp_data["created_at"] = resp_data["created_at"].isoformat()
    
    if idempotency_key:
        save_idempotency_response(db, user_id, idempotency_key, status.HTTP_201_CREATED, resp_data)
        
    schedule_webhook(db, user_id, "payment.created", resp_data, background_tasks)
    return resp_data

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Ödeme bulunamadı")
    return payment

@router.post("/{payment_id}/capture", response_model=PaymentResponse)
def capture_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Ödeme bulunamadı")
        
    if payment.status != "authorized":
        raise HTTPException(status_code=400, detail="Sadece 'authorized' durumundaki ödemeler capture edilebilir.")
        
    payment.status = "captured"
    db.commit()
    db.refresh(payment)
    
    resp_data = PaymentResponse.model_validate(payment).model_dump()
    resp_data["created_at"] = resp_data["created_at"].isoformat()
    schedule_webhook(db, user_id, "payment.captured", resp_data, background_tasks)
    return payment

@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
def cancel_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Ödeme bulunamadı")
        
    if payment.status != "authorized":
        raise HTTPException(status_code=400, detail="Sadece 'authorized' durumundaki ödemeler iptal edilebilir.")
        
    payment.status = "canceled"
    db.commit()
    db.refresh(payment)
    
    resp_data = PaymentResponse.model_validate(payment).model_dump()
    resp_data["created_at"] = resp_data["created_at"].isoformat()
    schedule_webhook(db, user_id, "payment.canceled", resp_data, background_tasks)
    return payment

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id)
):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Ödeme bulunamadı")
        
    if payment.status != "captured":
        raise HTTPException(status_code=400, detail="Sadece 'captured' durumundaki ödemeler iade edilebilir.")
        
    payment.status = "refunded"
    db.commit()
    db.refresh(payment)
    
    resp_data = PaymentResponse.model_validate(payment).model_dump()
    resp_data["created_at"] = resp_data["created_at"].isoformat()
    schedule_webhook(db, user_id, "payment.refunded", resp_data, background_tasks)
    return payment
