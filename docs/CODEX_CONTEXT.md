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
* OCR denemesi ve Metin kalite filtresi
* Chunk embedding üretimi
* Proje bazlı semantik arama (RAG)
* **Kriter ve Kural Motoru (Rule Engine):** Belirli standartlar (kriterler) ve onlara bağlı kurallar (eşikler, mantıksal şartlar).
* **Proje Değerlendirme Sistemi (Evaluations):** Projeleri mevcut kural setlerine (criterion sets) göre analiz eden arka plan (background) görevi.
* **Kanıt ve Alıntı Yönetimi (Citations):** Değerlendirme sonucunda RAG sisteminden alınan alıntıların, kanıtların (evidence_summary), varsa eksik bilgilerin (missing_information) ve uyarıların (warnings) raporlanması.
* **Kural Konfigürasyonu Anlık Görüntüleri (Rule Snapshots):** Her bir değerlendirme sonucunun, işlem anındaki kural konfigürasyonunu (eşikler vb.) saklamasıyla geçmişe dönük veri bütünlüğü sağlanması.

Mimari kurallar:

* Service Role Key yalnızca backend tarafında kullanılmalı.
* Kullanıcı erişimi ve proje izolasyonu her endpoint’te doğrulanmalı.
* Bir projenin belgeleri başka projedeki aramada veya değerlendirmede kullanılmamalı.
* LLM (OpenAI vs.) doğrudan puan hesaplamamalı; puan hesaplaması, LLM'in çıkardığı sayısal ya da kategorik verilere dayalı olarak deterministik kural motoru tarafından yapılmalı.
* Her RAG / Değerlendirme sonucu dosya adı, sayfa numarası ve metin alıntısı içermeli (Citations).
* Mevcut çalışan yapıyı gereksiz yere yeniden yazma.
* Değişikliklerden önce ilgili dosyaları (schemas, services, vb.) incele.
* Her değişiklikten sonra lint, type-check ve ilgili testleri çalıştır.
* Hata varsa geçici olarak gizlemek yerine temel nedenini çöz.

Şimdi repository’yi incele. Önce mevcut yapıyı, eksikleri ve muhtemel hataları raporla ve istenen görevi yerine getirmek üzere plan yap.
