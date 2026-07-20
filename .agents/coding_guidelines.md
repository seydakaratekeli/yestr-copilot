# Kodlama Standartları ve Prensipleri

Bu doküman, projede kod yazılırken dikkat edilmesi gereken temel kuralları ve prensipleri içermektedir. Hem geliştiriciler hem de yapay zeka asistanları (örneğin Antigravity) kod üretirken bu kurallara harfiyen uymalıdır.

## 1. Clean Code (Temiz Kod) Kuralları
*   **Anlamlı İsimlendirmeler:** Değişken, fonksiyon ve sınıf isimleri ne iş yaptıklarını açıkça belirtmelidir (örneğin `x` yerine `user_age`, `calc()` yerine `calculate_total_price()`).
*   **Kısa ve Odaklı Fonksiyonlar:** Her fonksiyon sadece tek bir işi yapmalı (Single Responsibility) ve mümkün olduğunca kısa olmalıdır.
*   **Yorum Satırları:** Kötü yazılmış kodu açıklamak için değil, kodun neden (why) o şekilde yazıldığını açıklamak için yorum kullanılmalıdır. Kodun kendisi ne (what) yaptığını anlatabilmelidir.
*   **Tekrarı Önle (DRY - Don't Repeat Yourself):** Aynı kod blokları birden fazla kez yazılmamalı, ortak fonksiyonlar veya sınıflar halinde soyutlanmalıdır.
*   **Okunabilirlik:** Kod, bilgisayarın anlaması için değil, diğer insanların okuyup anlaması için yazılır.

## 2. SOLID Prensipleri
*   **S - Single Responsibility Principle (Tek Sorumluluk Prensibi):** Bir sınıfın veya modülün değişmek için yalnızca bir nedeni olmalıdır.
*   **O - Open/Closed Principle (Açık/Kapalı Prensibi):** Yazılım varlıkları (sınıflar, modüller, fonksiyonlar vb.) genişletilmeye açık, ancak değiştirilmeye kapalı olmalıdır.
*   **L - Liskov Substitution Principle (Liskov Yerine Geçme Prensibi):** Alt sınıflar, üst sınıflarının yerine kullanılabilir olmalı ve sistemin beklenen davranışını bozmamalıdır.
*   **I - Interface Segregation Principle (Arayüz Ayrımı Prensibi):** İstemciler, kullanmadıkları arayüzlere bağımlı olmaya zorlanmamalıdır. Büyük arayüzler yerine daha küçük, özelleşmiş arayüzler tercih edilmelidir.
*   **D - Dependency Inversion Principle (Bağımlılığın Tersine Çevrilmesi Prensibi):** Yüksek seviyeli modüller düşük seviyeli modüllere bağlı olmamalıdır; her ikisi de soyutlamalara bağlı olmalıdır.

## 3. Temel Yazılım İlkeleri (Evrensel Kurallar)
*   **KISS (Keep It Simple, Stupid):** Sistemler basit tutulduklarında en iyi şekilde çalışır. Gereksiz karmaşıklıktan kaçınılmalıdır.
*   **YAGNI (You Aren't Gonna Need It):** Sadece şu an ihtiyaç duyulan özellikleri geliştirin; gelecekte "belki lazım olur" diyerek kod yazmayın.
*   **Separation of Concerns (İlgi Alanlarının Ayrımı):** Uygulamanın farklı işlevleri farklı modüller veya katmanlar halinde ayrılmalıdır (örneğin veritabanı işlemleri, iş mantığı ve arayüz birbirinden bağımsız olmalıdır).

## 4. Hata Yönetimi ve Güvenlik (Exception & Security)
*   **Hata Yakalama (Exception Handling):** Hatalar uygun try-catch/except blokları ile yakalanmalı, uygulamayı çökertecek "sessiz" hatalara izin verilmemelidir. Hatalar mutlaka loglanmalıdır.
*   **Giriş Doğrulama (Input Validation):** Kullanıcıdan veya dış sistemlerden gelen tüm veriler mutlaka doğrulanmalı (validate) ve temizlenmelidir (sanitize). (SQL Injection, XSS gibi saldırıları önlemek için).
*   **Güvenli Konfigürasyon:** Şifreler, API anahtarları ve gizli bilgiler kod içinde (hardcoded) tutulmamalı, `.env` dosyaları veya güvenli yapılandırma yöneticileri kullanılmalıdır.
*   **En Az Ayrıcalık (Least Privilege):** Fonksiyonlar ve servisler, sadece görevlerini yerine getirebilecekleri en az yetkiyle çalıştırılmalıdır.

## 5. Kod Standartları ve Kalite Kontrolü
*   **Formatlama ve Linting:** Projenin diline uygun linter ve formatlayıcılar (Örn: Python için Black/Ruff, TS için ESLint/Prettier) kullanılmalı, kod stili standartlaştırılmalıdır.
*   **Tip Güvenliği (Type Safety):** Python'da type hints (örneğin `def foo(x: int) -> str:`), TypeScript'te ise sıkı tip denetimleri (`strict: true`) aktif olarak kullanılmalıdır.
*   **Test Edilebilirlik:** Kod parçaları birbirinden bağımsız ve kolayca birim test (unit test) yazılabilecek şekilde tasarlanmalıdır.
*   **Modülerlik:** Klasör ve dosya yapısı mantıklı ve sürdürülebilir olmalıdır (Örn: `services/`, `controllers/`, `models/`, `utils/` gibi ayrımlar).

---
> **Not (Yapay Zeka İçin Talimat):** Antigravity veya diğer asistanlar, bu projede kod oluştururken, güncellerken veya yeniden yapılandırırken yukarıda belirtilen tüm kuralları varsayılan davranış olarak kabul edip uygulayacaktır.
