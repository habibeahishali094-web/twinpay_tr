import httpx
import logging
import asyncio
from sqlalchemy.orm import Session
from twinpay_tr.models.webhook import WebhookEndpoint
from twinpay_tr.core.chaos import get_webhook_chaos

logger = logging.getLogger(__name__)

async def send_webhook_task(url: str, payload: dict, delay_s: float = 0.0, duplicate: bool = False):
    """Arka planda asenkron olarak webhook gönderir."""
    if delay_s > 0:
        await asyncio.sleep(delay_s)
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=5.0)
            logger.info(f"Webhook sent to {url}, status: {response.status_code}")
            
            if duplicate:
                # Same webhook again for chaos mode
                response2 = await client.post(url, json=payload, timeout=5.0)
                logger.info(f"Duplicate webhook sent to {url}, status: {response2.status_code}")
        except Exception as e:
            logger.error(f"Failed to send webhook to {url}: {str(e)}")

def schedule_webhook(db: Session, user_id: int, event_type: str, data: dict, background_tasks, settings=None):
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
    
    delay_s = 0.0
    duplicate = False
    if settings:
        delay_s, duplicate = get_webhook_chaos(settings)
    
    for endpoint in endpoints:
        background_tasks.add_task(send_webhook_task, endpoint.url, payload, delay_s, duplicate)
