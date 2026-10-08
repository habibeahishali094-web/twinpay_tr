import time
import random
from twinpay_tr.models.settings import Settings

REJECTION_REASONS = [
    "insufficient_funds",
    "limit_exceeded",
    "card_blocked",
    "bank_declined"
]

def get_random(settings: Settings) -> random.Random:
    if settings.seed:
        return random.Random(settings.seed)
    return random.Random()

def apply_delay(settings: Settings):
    if settings.chaos_mode_enabled and settings.delay_ms > 0:
        time.sleep(settings.delay_ms / 1000.0)

def should_fail_payment(settings: Settings) -> str | None:
    if not settings.chaos_mode_enabled or settings.error_rate <= 0:
        return None
    
    rnd = get_random(settings)
    if rnd.randint(1, 100) <= settings.error_rate:
        return rnd.choice(REJECTION_REASONS)
    return None

def get_webhook_chaos(settings: Settings) -> tuple[float, bool]:
    """Returns (delay_seconds, should_duplicate)"""
    if not settings.chaos_mode_enabled or settings.error_rate <= 0:
        return 0.0, False
        
    rnd = get_random(settings)
    
    if rnd.randint(1, 100) <= settings.error_rate:
        is_duplicate = rnd.choice([True, False])
        delay_s = rnd.uniform(2.0, 10.0) if rnd.choice([True, False]) else 0.0
        return delay_s, is_duplicate
    return 0.0, False
