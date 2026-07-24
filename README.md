# Yestr Copilot

Yestr Copilot, yapay zeka destekli bir asistan ve RAG (Retrieval-Augmented Generation) tabanlı doküman yönetim platformudur. Sistem, FastAPI tabanlı güçlü bir backend ve modern bir Next.js frontend mimarisinden oluşmaktadır.

## Kurulum ve Çalıştırma

Projeyi ayağa kaldırmak için frontend ve backend olmak üzere iki ayrı terminalde işlem yapmanız gerekiyor.

İşte adım adım çalıştırmanız gereken komutlar:

1. Backend'i Ayağa Kaldırmak İçin (FastAPI)
Yeni bir terminal açın ve sırasıyla şu komutları çalıştırın:

# Backend klasörüne gidin
cd backend

# Sanal ortamı (virtual environment) aktif edin
.\.venv\Scripts\activate

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


