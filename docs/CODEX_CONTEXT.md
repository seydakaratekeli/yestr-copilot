Bu repository üzerinde YeS-TR Copilot adlı bir B2B SaaS MVP geliştiriyoruz.

Mevcut teknoloji yığını:

* Frontend: Next.js, TypeScript, Tailwind CSS, shadcn/ui
* Backend: FastAPI, Python
* Kimlik doğrulama: Supabase Auth
* Veritabanı: Supabase PostgreSQL
* Dosya depolama: Private Supabase Storage
* PDF işleme: PyMuPDF
* OCR: PyMuPDF + Tesseract
* Embedding: intfloat/multilingual-e5-small, 384 boyut
* Vektör arama: PostgreSQL pgvector

Şu ana kadar çalışan özellikler:

* Kullanıcı kayıt, giriş ve çıkış
* Korumalı dashboard
* Proje oluşturma ve listeleme
* Çoklu PDF yükleme
* PDF doğrulama ve sayfa sayısı çıkarma
* PDF metnini sayfa bazında çıkarma
* Metni chunk’lara ayırma
* OCR denemesi
* Metin kalite filtresi
* Chunk embedding üretimi
* Proje bazlı semantik arama

Çalışan semantik arama örneği:
Sorgu: “Düşük debili armatür kullanılıyor mu?”
Sonuç olarak “Lavabo bataryalarının maksimum debisi 5 litre/dakika olacaktır.” metnini içeren chunk yaklaşık 0.81 similarity ile bulunuyor.

Mimari kurallar:

* Service Role Key yalnızca backend tarafında kullanılmalı.
* Kullanıcı erişimi ve proje izolasyonu her endpoint’te doğrulanmalı.
* Bir projenin belgeleri başka projedeki aramada görünmemeli.
* Düşük kaliteli OCR chunk’ları embedding’e alınmamalı.
* LLM puan hesaplamamalı; ileride puanı deterministik kural motoru hesaplayacak.
* Her RAG sonucu dosya adı, sayfa numarası ve benzerlik değeri içermeli.
* Mevcut çalışan yapıyı gereksiz yere yeniden yazma.
* Değişikliklerden önce ilgili dosyaları incele.
* Her değişiklikten sonra lint, type-check ve ilgili testleri çalıştır.
* Hata varsa geçici olarak gizlemek yerine temel nedenini çöz.

Şimdi repository’yi incele. Önce mevcut yapıyı, eksikleri ve muhtemel hataları raporla. Ardından bir sonraki özellik olarak semantik arama sonuçlarını kaynak göstererek yanıtlayan RAG soru-cevap endpoint’ini geliştir.

Beklenen endpoint:
POST /api/projects/{project_id}/ask

Beklenen davranış:

1. Kullanıcının projeye erişimini doğrula.
2. Sorgu embedding’i üret.
3. Projeye ait en ilgili chunk’ları getir.
4. Yeterli kaynak yoksa cevap uydurma.
5. Kaynaklardan kısa ve temkinli Türkçe cevap üret.
6. Cevapla birlikte kullanılan dosya adı, sayfa, içerik alıntısı ve similarity değerlerini döndür.
7. LLM sağlayıcısını arayüz üzerinden değiştirilebilir tasarla.
8. API anahtarlarını environment variable olarak kullan.
9. Pydantic response modelleri ve hata yönetimi ekle.
10. En az birim testleri ve örnek curl isteği ekle.

Önce kod yazmadan repository analizini ve uygulama planını göster.
