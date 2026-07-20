# Yestr Copilot - Backend Geliştirme Dokümantasyonu

Bu doküman, Yestr Copilot projesinin backend mimarisi, kullanılan teknolojiler ve servis yapıları hakkında temel teknik detayları içermektedir.

## 🛠 Kullanılan Teknolojiler (Tech Stack)

### Core Framework & Sunucu
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Yüksek performanslı, asenkron Python web framework)
- **Sunucu (ASGI):** Uvicorn (`uvicorn`)
- **Veri Doğrulama:** Pydantic (`pydantic`, `pydantic-settings`)

### Yapay Zeka & NLP (RAG Mimari)
Projenin temel amacı olan yapay zeka asistanı ve doküman yönetimi (RAG) için aşağıdaki araçlar kullanılmaktadır:
- **LLM Entegrasyonu:** OpenAI API (`openai`)
- **Vektör & Gömme (Embeddings):** Sentence Transformers (`sentence-transformers`), HuggingFace Hub (`huggingface_hub`), PyTorch (`torch`)
- **Veri & Vektör İşleme:** NumPy (`numpy`), Scikit-learn (`scikit-learn`), SciPy (`scipy`)
- **Doküman (PDF) İşleme:** PyMuPDF (`pymupdf`)

### Veritabanı & ORM
- **Veritabanı Servisi:** [Supabase](https://supabase.com/) (`supabase`, `postgrest`, `realtime`)
- **ORM:** SQLAlchemy (`SQLAlchemy`)

### Güvenlik & Kimlik Doğrulama
- **Kriptografi & Token Yönetimi:** `python-jose`, `PyJWT`, `passlib`, `cryptography`
- **Dosya Yüklemeleri:** `python-multipart` (API üzerinden dosya yükleme işlemleri için)

### Test Ortamı
- **Test Framework'ü:** Pytest (`pytest`, `pytest-asyncio`)

---

## 📁 Klasör Yapısı (Folder Structure)

Projenin `backend/app/` klasörü modüler bir FastAPI yapısını takip etmektedir:

- `api/`: Tüm REST API endpoint'lerinin (route'ların) tanımlandığı dizin (Örn: `/answers`, `/documents`, `/projects`).
- `core/`: Uygulamanın çekirdek konfigürasyonları, güvenlik ayarları ve veritabanı/Supabase bağlantı nesnelerinin bulunduğu yer.
- `models/`: Veritabanı tablolarına karşılık gelen SQLAlchemy model sınıfları.
- `schemas/`: Pydantic kullanılarak oluşturulmuş, API'ye giren ve çıkan verilerin doğrulama şemaları (Request/Response modelleri).
- `services/`: İş mantığının (business logic) yer aldığı katman. AI işlemleri (RAG), doküman parçalama (chunking), OCR, arama (semantic search) ve veritabanı işlemleri servis sınıfları üzerinden yönetilir.
- `prompts/`: Yapay zeka modellerine gönderilen sistem ve kullanıcı prompt'larının şablonlandığı dizin.
- `main.py`: FastAPI uygulamasının başlatıldığı ve yapılandırıldığı kök giriş dosyası.

---

## 🚀 Geliştirme Komutları

Geliştirme ortamını başlatmak için ana README dosyasındaki adımları izleyebilirsiniz. Backend özelinde sık kullanılan işlemler:

```bash
# Sanal ortamı aktif etme (Windows)
.\.venv\Scripts\activate

# Bağımlılıkları yükleme
pip install -r requirements.txt

# Uygulamayı geliştirme modunda çalıştırma
uvicorn app.main:app --reload

# Testleri çalıştırma
pytest
```
