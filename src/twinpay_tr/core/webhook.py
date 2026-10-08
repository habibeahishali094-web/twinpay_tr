import httpx
import logging
from sqlalchemy.orm import Session
from twinpay_tr.models.webhook import WebhookEndpoint

logger = logging.getLogger(__name__)

async def send_webhook_task(url: str, payload: dict):
    """Arka planda asenkron olarak webhook gönderir."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=5.0)
            logger.info(f"Webhook sent to {url}, status: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send webhook to {url}: {str(e)}")

def schedule_webhook(db: Session, user_id: int, event_type: str, data: dict, background_tasks):
    """
    Belirtilen olayı kullanıcının tanımlı tüm webhook'larına göndermeyi planlar.
    """
    endpoints = db.query(WebhookEndpoint).filter(WebhookEndpoint.user_id == user_id).all()
    if not endpoints:
        return
        
    payload = {
        "event": event_type,
        "data": data
    }
    
    for endpoint in endpoints:
        background_tasks.add_task(send_webhook_task, endpoint.url, payload)
