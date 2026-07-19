Projeyi ayağa kaldırmak için frontend ve backend olmak üzere iki ayrı terminalde işlem yapmanız gerekiyor.

İşte adım adım çalıştırmanız gereken komutlar:

1. Backend'i Ayağa Kaldırmak İçin (FastAPI)
Yeni bir terminal açın ve sırasıyla şu komutları çalıştırın:

# Backend klasörüne gidin
cd backend

# Sanal ortamı (virtual environment) aktif edin


# Gerekli kütüphanelerin yüklü olduğundan emin olmak için (ilk kurulumda veya güncellemelerde)
pip install -r requirements.txt

# FastAPI uygulamasını geliştirme modunda başlatın
uvicorn app.main:app --reload

2. Frontend'i Ayağa Kaldırmak İçin (Next.js)
İkinci bir terminal açın ve şu komutları çalıştırın:

# Frontend klasörüne gidin
cd frontend

# Gerekli kütüphanelerin yüklü olduğundan emin olmak için (ilk kurulumda veya güncellemelerde)
npm install

# Next.js uygulamasını geliştirme modunda başlatın
npm run dev

Bu işlemleri tamamladıktan sonra; frontend http://localhost:3000 adresinden, backend ise http://localhost:8000 adresinden ayağa kalkmış olacaktır.

## RAG soru-cevap örneği

Backend tarafında LLM sağlayıcısı etkinse:

```bash
curl -X POST "http://localhost:8000/api/projects/PROJECT_ID/ask" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Düşük debili armatür kullanılıyor mu?",
    "limit": 5,
    "minimum_similarity": 0.45
  }'
```

Yanıt, yalnızca projeye ait aranabilir ve embedding'i tamamlanmış
chunk'lardan üretilen kaynakları kullanır. Yeterli kanıt bulunamazsa LLM
çağrılmadan temkinli bir `insufficient_evidence` yanıtı döner.
