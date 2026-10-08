
# TwinPay TR

TwinPay TR, geliştiriciler için Türkiye'ye yerelleştirilmiş bir sahte ödeme (sandbox) servisidir. Gerçek para veya gerçek banka altyapısına dokunmadan entegrasyonlarınızı 3D Secure, taksit ve Türkiye'ye özgü banka hatalarıyla güvenle test etmenizi sağlar.

## Bu Proje Neden?

- **İlham:** Arga Labs (YC Spring 2026), gerçek servislerin "ikizlerini" yaparak geliştiricilere stabil bir test ortamı sunma fikriyle yola çıkmıştır.
- **Neden önemli:** Arga, lansmanından kısa süre sonra yaklaşık 40 bin dolar aylık gelire ulaşmış ve 10 milyon dolar tohum (seed) yatırımı alarak bu modelin (sandbox-as-a-service) ne kadar talep gördüğünü kanıtlamıştır.
- **Bu projenin kapsamı:** 
  - (a) **Clone kısmı:** Ödeme oluşturma, onaylama, iptal, iade, webhook gönderimi ve idempotency gibi temel ödeme yetenekleri.
  - (b) **Yerelleştirme:** Türkçe hata mesajları, TRY formatı, taksit seçenekleri (1, 2, 3, 6, 9, 12), 3D Secure akışları, Türkiye'ye özgü ret nedenleri (Yetersiz bakiye vb.) ve kullanıcıya özel ayarlar.
  - (c) **Yenilik:** Seed (tohum) tabanlı, tekrar üretilebilir kaos modu (hata ve gecikme simülasyonu).

## Özellikler
- Taksit ve 3D Secure destekli ödeme senaryoları.
- Idempotency-Key ile mükerrer ödeme koruması.
- Tekrar üretilebilir hatalar için Seed destekli Kaos Mühendisliği.
- API kayıtlarının ve ödemelerin izlenebildiği Geliştirici Paneli.
- Her geliştiricinin kendi alanında tam izole (sandbox) çalışabilmesi.

## Mimari
Projenin temel klasör yapısı:
- `api/`: API endpoint'leri ve bağımlılık enjeksiyonları (deps.py).
- `core/`: Yapılandırma, güvenlik, kaos modu ve dil ayarları.
- `db/`: Veritabanı bağlantısı ve SQLAlchemy oturum yönetimi.
- `models/`: Veritabanı tablolarının tanımları (SQLAlchemy).
- `schemas/`: Pydantic doğrulama şemaları.
- `web/` ve `templates/`: Geliştirici paneline ait Jinja2 şablonları ve router.
- `tests/`: Kapsamlı API testleri (Pytest).

**İzolasyon Kuralı:** Veritabanındaki her tablo (ödemeler, ayarlar, webhook'lar, loglar vb.) mutlaka `user_id` alanı taşır. `deps.py` üzerinden gelen her istekte veriler yalnızca o anki giriş yapmış kullanıcıya göre filtrelenir, geliştiriciler arası veri sızıntısı kesinlikle yaşanmaz.

## Kurulum

Proje Python 3.11+ gerektirir.

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Uygulamayı Çalıştırma
```bash
uvicorn twinpay_tr.main:app --app-dir src --reload
```
Uygulama `http://127.0.0.1:8000` adresinde çalışacaktır. Geliştirici Paneli `http://127.0.0.1:8000/`, API Dokümantasyonu ise `http://127.0.0.1:8000/docs` adresinden erişilebilir.

## Hızlı Başlangıç

Aşağıdaki örneklerde yer alan `<API_ANAHTARI>` kısmına, ilk adımda alacağınız kendi anahtarınızı yazmalısınız.

**a) Kullanıcı Kaydı:**
Sisteme kayıt olup API anahtarınızı alın. *Anahtar sadece bir kez gösterilir, mutlaka not edin.*
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/users/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"username": "demo"}'
```

**b) Ödeme Oluşturma:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <API_ANAHTARI>' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 250.0,
  "card_number": "4111111111111111",
  "expiry_month": "12",
  "expiry_year": "28",
  "cvc": "123",
  "installments": 1,
  "require_3d_secure": false
}'
```

**c) 3D Secure ile Ödeme Tamamlama (pending_3d için):**
Ödemeyi oluştururken `require_3d_secure: true` verdiyseniz, dönen `payment_id` ile bu adımı çalıştırarak işlemi doğrulayabilirsiniz.
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/1/complete_3d' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <API_ANAHTARI>' \
  -H 'Content-Type: application/json' \
  -d '{"success": true}'
```

**d) Onaylama, İptal ve İade:**
İlgili işleme göre aşağıdaki endpoint'lerden birini kullanabilirsiniz:
```bash
curl -X 'POST' 'http://127.0.0.1:8000/api/v1/payments/1/capture' -H 'Authorization: Bearer <API_ANAHTARI>'
curl -X 'POST' 'http://127.0.0.1:8000/api/v1/payments/1/cancel' -H 'Authorization: Bearer <API_ANAHTARI>'
curl -X 'POST' 'http://127.0.0.1:8000/api/v1/payments/1/refund' -H 'Authorization: Bearer <API_ANAHTARI>'
```

**e) Webhook URL Belirleme:**
Gelen olayları (payment.created, payment.failed vb.) dinlemek için bir webhook ekleyin. (Örn: https://webhook.site adresinden aldığınız geçici URL'yi kullanabilirsiniz.)
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/webhooks/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <API_ANAHTARI>' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://webhook.site/YOUR_UUID_HERE", "event_types": ["payment.created", "payment.failed"]}'
```

**f) Kaos Ayarları ve Tekrar Üretilebilirlik (Seed):**
Sistemi `%50` hata verecek ve sabit bir `seed` (örneğin "test_seed") ile çalışacak şekilde güncelleyin. Bu sayede hatalar rastgele değil, tahmin edilebilir ve tekrarlanabilir olur.
```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/api/v1/settings/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <API_ANAHTARI>' \
  -H 'Content-Type: application/json' \
  -d '{
  "chaos_mode_enabled": true,
  "error_rate": 50,
  "seed": "test_seed"
}'
```

**g) Sandbox Sıfırlama:**
Tüm test verilerinizi (ödemeler, ayarlar, webhook'lar) silip temiz bir duruma dönmek için:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/sandbox/reset' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <API_ANAHTARI>'
```

## Test Kartları

| Kart Numarası | Özellik | Beklenen Durum |
|---|---|---|
| Bütün 16 Haneli Rakamlar | Standart Kredi/Banka Kartı | Ayarlardaki Kaos Modu (error_rate) kapalıysa her zaman başarılı (`authorized` veya 3D seçildiyse `pending_3d`) olur. |

*Bunlar sahte test kartlarıdır, gerçek kart değildir. Sistemimizde gerçek banka entegrasyonu bulunmamaktadır, tamamen izole bir test ortamıdır. Kart limit veya red senaryolarını test etmek için lütfen Geliştirici Paneli veya API üzerinden Kaos Modu'nu aktif ediniz.*

## Güvenlik
- API anahtarları veritabanında Bcrypt hashing algoritması ile şifreli olarak saklanır (düz metin olarak bulunmaz).
- Webhook kayıtlarında Sunucu Taraflı İstek Sahteciliği (SSRF) koruması vardır; localhost veya iç ağ IP adresleri reddedilir.
- Geliştirici panelinde XSS ve Session Hijacking açıklarına karşı çerezlerde (cookie) `HttpOnly`, `SameSite` ve `Secure` (ortama bağlı) bayrakları aktiftir.
- Sistemin güvenliğini doğrulamak için `verify_security.py` isimli test betiğini çalıştırabilirsiniz: `python verify_security.py`. Bu betik, API izolasyonunun, hashing'in ve SSRF engellemesinin doğru çalıştığını test eder.

## Bilinen Sınırlamalar
- Geliştirici panelinde oturum (login) işlemi yapılırken API anahtarı `cookie`'de tutulmaktadır. Üretim ortamında sunucu tarafı oturum kimliği (session ID) kullanılmalıdır.
- Login formunda CSRF token koruması bulunmamaktadır (riski düşüktür).
- HTTPS kullanılıyorsa, çerez güvenliği için `COOKIE_SECURE=True` ortam değişkeniyle çalıştırılmalıdır (yerel geliştirmede varsayılan olarak `False`'dur).

## Kaynaklar
- [Arga Labs - YC Spring 2026](https://www.ycombinator.com/companies/arga-labs)
```

Github'da işinizi hallettikten sonra dilerseniz komut satırından `git pull --rebase origin master` ile de kodunuzun senkronize olmasını sağlayabilirsiniz. Başka yardımcı olabileceğim bir konu var mı?
