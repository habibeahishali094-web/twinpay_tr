# TwinPay TR

TwinPay TR, Türkiye'ye yerelleştirilmiş sahte bir ödeme servisi (sandbox) projesidir. Geliştiricilerin gerçek bir ödeme/banka entegrasyonu kurmadan, kendi sistemlerini test edebilmeleri için tasarlanmıştır.

## İzolasyon Kuralı
Sistemdeki her kullanıcının kendine ait, izole bir sandbox verisi vardır. 
Veritabanı tablolarındaki her kayıt `user_id` sütunu içermelidir (User tablosu hariç). 
Tüm veritabanı sorguları giriş yapan kullanıcının `user_id`'sine göre filtrelenmelidir. Bu kuralı uygulamak için API bağımlılıklarında (dependencies) sağlanan ortak yardımcı fonksiyonlar (`deps.py` içindeki oturum ve kullanıcı kimliği filtreleri) kullanılmalıdır. Hiçbir kullanıcı başkasının test verisine erişemez!
