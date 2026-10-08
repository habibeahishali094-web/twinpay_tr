# TwinPay TR 🚀 (Aşama 6)
Türkiye'ye özgü yerelleştirilmiş, geliştiriciler için premium bir sahte ödeme (sandbox) servisidir. 
Gerçek ödemelere dokunmadan entegrasyonlarınızı 3D Secure, taksit ve Türkiye'ye özgü banka hatalarıyla test edin.

## Özellikler
- **Türkiye Odaklı:** TRY (₺), 1.250,50 ₺ formatı, taksit seçenekleri (1,2,3,6,9,12).
- **Gelişmiş 3D Secure:** `require_3d_secure` ile ödemelerinizi `pending_3d` statüsünde bekleterek doğrulama akışlarını test edin.
- **Kaos Modu (Chaos Engineering):** İsteğe bağlı hata oranları belirleyin; zaman aşımı, rastgele limit aşımı (`limit_exceeded`) veya çifte webhook gönderimi gibi senaryoları simüle edin.
- **Tekrar Üretilebilirlik (Seed):** Ayarlarınıza bir "seed" (tohum) vererek karmaşık hataların hep aynı şekilde oluşmasını sağlayın.
- **Geliştirici Paneli:** Web arayüzü sayesinde işlemlerinizi, API kayıtlarınızı ve kaos ayarlarınızı göz alıcı bir arayüzden takip edin.
- **İzolasyon Kuralı:** Sistem, her bir geliştiriciyi kendi API anahtarıyla (sandbox'ı ile) tam olarak izole eder.
- **Idempotency (Tekrar Önleme):** `Idempotency-Key` başlığı sayesinde ağ problemlerinde bile ödemenin çift çekilmesini önleyin.

## Bilinen Sınırlamalar
- Geliştirici panelinde oturum (login) işlemi yapılırken API anahtarı `cookie`'de tutulmaktadır. Üretim ortamında sunucu tarafı oturum kimliği (session ID) kullanılmalıdır.
- Login formunda CSRF token koruması bulunmamaktadır (riski düşüktür).
- HTTPS kullanılıyorsa, çerez güvenliği için `COOKIE_SECURE=True` ortam değişkeniyle çalıştırılmalıdır (yerel geliştirmede varsayılan olarak `False`'dur).

## Kurulum ve Çalıştırma
Proje Python 3.11+ gerektirir. Bağımlılık yönetimi için `requirements.txt` kullanılır.
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Çalıştırmak için:
```bash
uvicorn twinpay_tr.main:app --reload
```
Panel ve API `http://127.0.0.1:8000` adresinde çalışacaktır.

## Geliştirici Paneline Giriş
1. Uygulamayı çalıştırdıktan sonra `http://localhost:8000/docs` üzerinden `/api/v1/users/register` endpoint'ini kullanarak bir kullanıcı oluşturun. (Response içerisinde size `TwinPay_...` ile başlayan bir `api_key` verilecektir.)
2. `http://localhost:8000/` adresini tarayıcınızda açın ve bu `api_key` ile giriş yapın.
3. Yönetim paneli üzerinden ödemelerinizi, kayıtlarınızı görüntüleyin ve ayarlarınızı (Kaos modu vs.) yapılandırın.

## Örnek API Kullanımı (Ödeme Oluşturma)
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TwinPay_...api_key_buraya...' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 250.0,
  "card_number": "4111111111111111",
  "expiry_month": "12",
  "expiry_year": "28",
  "cvc": "123",
  "installments": 3,
  "require_3d_secure": false
}'
```

Test etmek için `pytest` çalıştırabilirsiniz:
```bash
pytest
```
