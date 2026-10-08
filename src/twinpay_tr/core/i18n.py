MESSAGES = {
    "tr": {
        "payment_not_found": "Ödeme bulunamadı.",
        "invalid_status_capture": "Sadece 'authorized' durumundaki ödemeler onaylanabilir.",
        "invalid_status_cancel": "Sadece 'authorized' durumundaki ödemeler iptal edilebilir.",
        "invalid_status_refund": "Sadece 'captured' durumundaki ödemeler iade edilebilir.",
        "invalid_installments": "Geçersiz taksit sayısı. Sadece 1, 2, 3, 6, 9, 12 taksit yapılabilir.",
        
        "error_insufficient_funds": "Yetersiz bakiye. Lütfen bakiyenizi kontrol edip tekrar deneyin.",
        "error_limit_exceeded": "Kart limiti aşıldı. Lütfen limitinizi kontrol edin.",
        "error_card_blocked": "Kartınız banka tarafından bloke edilmiş veya kullanıma kapalı.",
        "error_3d_failed": "3D Secure doğrulama işlemi başarısız oldu.",
        "error_bank_declined": "Kartınız banka tarafından reddedildi, lütfen başka bir kart deneyin."
    },
    "en": {
        "payment_not_found": "Payment not found.",
        "invalid_status_capture": "Only 'authorized' payments can be captured.",
        "invalid_status_cancel": "Only 'authorized' payments can be canceled.",
        "invalid_status_refund": "Only 'captured' payments can be refunded.",
        "invalid_installments": "Invalid installments. Only 1, 2, 3, 6, 9, 12 are supported.",
        
        "error_insufficient_funds": "Insufficient funds. Please check your balance.",
        "error_limit_exceeded": "Card limit exceeded.",
        "error_card_blocked": "Your card is blocked or closed for usage.",
        "error_3d_failed": "3D Secure verification failed.",
        "error_bank_declined": "Your card was declined by the bank, please try another card."
    }
}

def get_language(accept_language: str, user_lang: str = None) -> str:
    if user_lang in ["tr", "en"]:
        return user_lang
    if accept_language and "tr" in accept_language.lower():
        return "tr"
    return "en"

def t(key: str, lang: str = "tr") -> str:
    return MESSAGES.get(lang, MESSAGES["en"]).get(key, key)

def format_currency(amount: float, currency: str = "TRY") -> str:
    """1250.50 -> '1.250,50'"""
    s = f"{amount:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    if currency == "TRY":
        return f"{s} ₺"
    return f"{s} {currency}"

def format_date(dt) -> str:
    """08.10.2026"""
    if not dt:
        return ""
    return dt.strftime("%d.%m.%Y")
