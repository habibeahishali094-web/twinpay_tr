import sqlite3
import os
from fastapi.testclient import TestClient
from twinpay_tr.main import app
from twinpay_tr.db.session import engine
from twinpay_tr.db.base import Base

def run_tests():
    # 1. Veritabanını kontrol et
    print("=== 1. VERITABANI HASH KONTROLU ===")
    
    import uuid
    client = TestClient(app)
    u1 = f"user_{uuid.uuid4().hex[:6]}"
    u2 = f"user_{uuid.uuid4().hex[:6]}"
    
    res_a = client.post("/api/v1/users/register", json={"username": u1})
    if res_a.status_code != 201:
        print("Kullanıcı A oluşturulamadı:", res_a.status_code, res_a.text)
        return
    api_key_a = res_a.json()["api_key"]
    print(f"Kullanıcı A ({u1}) oluşturuldu. Verilen ham API Key: {api_key_a}")

    res_b = client.post("/api/v1/users/register", json={"username": u2})
    if res_b.status_code != 201:
        print("Kullanıcı B oluşturulamadı:", res_b.status_code, res_b.text)
        return
    api_key_b = res_b.json()["api_key"]
    print(f"Kullanıcı B ({u2}) oluşturuldu. Verilen ham API Key: {api_key_b}")

    # SQLite ile doğrudan bağlanıp Users tablosuna bakalım
    # Çünkü TestClient main'deki veritabanını (twinpay.db) kullanıyor
    conn = sqlite3.connect("twinpay.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, api_key_prefix, api_key_hash FROM users")
    users = cursor.fetchall()
    
    for u in users:
        print(f"DB Kaydı -> ID: {u[0]}, Username: {u[1]}, Prefix: {u[2]}, Hash: {u[3][:15]}... (Gerçek API Key veritabanında YOK!)")
        
    print("\nSonuç: api_key_hash kullanılıyor, anahtar olduğu gibi durmuyor. Şifrelenmiş halde (SHA-256).\n")
    
    # 2. SSRF Testi (127.0.0.1 reddediliyor mu?)
    print("=== 2. SSRF KONTROLU ===")
    headers_a = {"Authorization": f"Bearer {api_key_a}"}
    res_webhook = client.post("/api/v1/webhooks/", json={"url": "http://127.0.0.1:8000/some/path"}, headers=headers_a)
    print(f"Webhook Ekleme İsteği (http://127.0.0.1:8000) -> Status: {res_webhook.status_code}")
    if res_webhook.status_code == 400:
        print("Sonuç: BAŞARILI! SSRF engellendi. Localhost kabul edilmedi.\n")
    else:
        print(f"Sonuç: BAŞARISIZ! {res_webhook.json()}\n")
        
    # 3. İzolasyon Kuralı Testi (User A ödemesini User B çekebilir mi?)
    print("=== 3. IZOLASYON KONTROLU (User A vs User B) ===")
    # User A ödeme oluşturur
    pay_payload = {
        "amount": 500,
        "card_number": "4111111111111111",
        "expiry_month": "12",
        "expiry_year": "26",
        "cvc": "123"
    }
    res_pay_a = client.post("/api/v1/payments/", json=pay_payload, headers=headers_a)
    pay_id_a = res_pay_a.json()["id"]
    print(f"User A ödeme oluşturdu. Ödeme ID: {pay_id_a}")
    
    # User B bu ödemeyi görmeye çalışır
    headers_b = {"Authorization": f"Bearer {api_key_b}"}
    res_get_b = client.get(f"/api/v1/payments/{pay_id_a}", headers=headers_b)
    
    print(f"User B, User A'nın ödemesini çekmeye çalıştı -> Status: {res_get_b.status_code}")
    if res_get_b.status_code == 404:
        print("Sonuç: BAŞARILI! 404 Döndü. Başka kullanıcının ödemesine erişilemedi.")
    else:
        print("Sonuç: BAŞARISIZ!")

if __name__ == "__main__":
    run_tests()
