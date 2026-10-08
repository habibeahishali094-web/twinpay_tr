import json
from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks, status, Response
from sqlalchemy.orm import Session
from typing import Optional

from twinpay_tr.api import deps
from twinpay_tr.models.payment import Payment
from twinpay_tr.models.idempotency import IdempotencyKey
from twinpay_tr.schemas.payment import PaymentCreate, PaymentResponse, Complete3DSecure
from twinpay_tr.core.webhook import schedule_webhook
from twinpay_tr.core.i18n import t, format_currency, format_date
from twinpay_tr.api.v1.settings import get_or_create_settings
from twinpay_tr.core.chaos import apply_delay, should_fail_payment

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

def _prepare_response(payment: Payment, lang: str):
    data = PaymentResponse.model_validate(payment).model_dump()
    data["formatted_amount"] = format_currency(payment.amount, payment.currency)
    data["formatted_date"] = format_date(payment.created_at)
    
    if payment.status == "pending_3d":
        data["three_d_secure_url"] = f"http://localhost:8000/sandbox/3d-secure/{payment.id}"
        
    if payment.error_code:
        data["error_message"] = t(f"error_{payment.error_code}", lang)
        
    data["created_at"] = data["created_at"].isoformat()
    return data

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: PaymentCreate,
    background_tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id),
    lang: str = Depends(deps.get_lang),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    settings = get_or_create_settings(db, user_id)
    apply_delay(settings)

    if idempotency_key:
        existing = get_idempotency_response(db, user_id, idempotency_key)
        if existing:
            response.status_code = existing.response_status_code
            return json.loads(existing.response_body)
            
    if payment_in.installments not in [1, 2, 3, 6, 9, 12]:
        raise HTTPException(status_code=400, detail=t("invalid_installments", lang))
    
    chaos_error = should_fail_payment(settings)
    
    card_mask = f"**** **** **** {payment_in.card_number[-4:]}" if len(payment_in.card_number) >= 4 else "****"
    
    if chaos_error:
        payment_status = "failed"
    else:
        payment_status = "pending_3d" if payment_in.require_3d_secure else "authorized"
    
    new_payment = Payment(
        user_id=user_id,
        amount=payment_in.amount,
        currency=payment_in.currency,
        status=payment_status,
        card_mask=card_mask,
        installments=payment_in.installments,
        error_code=chaos_error,
        idempotency_key=idempotency_key
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    resp_data = _prepare_response(new_payment, lang)
    
    if idempotency_key:
        save_idempotency_response(db, user_id, idempotency_key, status.HTTP_201_CREATED, resp_data)
        
    if payment_status == "authorized" or payment_status == "failed":
        # we can trigger webhook for failures too
        event_type = "payment.created" if payment_status == "authorized" else "payment.failed"
        schedule_webhook(db, user_id, event_type, resp_data, background_tasks, settings)
        
    return resp_data

@router.post("/{payment_id}/complete_3d", response_model=PaymentResponse)
def complete_3d_secure(
    payment_id: int,
    payload: Complete3DSecure,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id),
    lang: str = Depends(deps.get_lang)
):
    settings = get_or_create_settings(db, user_id)
    apply_delay(settings)
    
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail=t("payment_not_found", lang))
        
    if payment.status != "pending_3d":
        raise HTTPException(status_code=400, detail="Ödeme 3D doğrulama bekleyen bir durumda değil.")
        
    if payload.success:
        payment.status = "authorized"
    else:
        payment.status = "failed"
        payment.error_code = payload.error_code or "3d_failed"
        
    db.commit()
    db.refresh(payment)
    
    resp_data = _prepare_response(payment, lang)
    event_type = "payment.created" if payload.success else "payment.failed"
    schedule_webhook(db, user_id, event_type, resp_data, background_tasks, settings)
    return resp_data

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id),
    lang: str = Depends(deps.get_lang)
):
    settings = get_or_create_settings(db, user_id)
    apply_delay(settings)
    
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail=t("payment_not_found", lang))
    return _prepare_response(payment, lang)

@router.post("/{payment_id}/capture", response_model=PaymentResponse)
def capture_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id),
    lang: str = Depends(deps.get_lang)
):
    settings = get_or_create_settings(db, user_id)
    apply_delay(settings)
    
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail=t("payment_not_found", lang))
        
    if payment.status != "authorized":
        raise HTTPException(status_code=400, detail=t("invalid_status_capture", lang))
        
    payment.status = "captured"
    db.commit()
    db.refresh(payment)
    
    resp_data = _prepare_response(payment, lang)
    schedule_webhook(db, user_id, "payment.captured", resp_data, background_tasks, settings)
    return resp_data

@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
def cancel_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id),
    lang: str = Depends(deps.get_lang)
):
    settings = get_or_create_settings(db, user_id)
    apply_delay(settings)
    
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail=t("payment_not_found", lang))
        
    if payment.status != "authorized":
        raise HTTPException(status_code=400, detail=t("invalid_status_cancel", lang))
        
    payment.status = "canceled"
    db.commit()
    db.refresh(payment)
    
    resp_data = _prepare_response(payment, lang)
    schedule_webhook(db, user_id, "payment.canceled", resp_data, background_tasks, settings)
    return resp_data

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user_id: int = Depends(deps.get_user_id),
    lang: str = Depends(deps.get_lang)
):
    settings = get_or_create_settings(db, user_id)
    apply_delay(settings)
    
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail=t("payment_not_found", lang))
        
    if payment.status != "captured":
        raise HTTPException(status_code=400, detail=t("invalid_status_refund", lang))
        
    payment.status = "refunded"
    db.commit()
    db.refresh(payment)
    
    resp_data = _prepare_response(payment, lang)
    schedule_webhook(db, user_id, "payment.refunded", resp_data, background_tasks, settings)
    return resp_data
