# Yestr Copilot - Frontend Geliştirme Dokümantasyonu

Bu doküman, Yestr Copilot projesinin frontend mimarisi, kullanılan teknolojiler ve geliştirme standartları hakkında temel teknik detayları içermektedir.

## 🛠 Kullanılan Teknolojiler (Tech Stack)

### Core
- **Framework:** [Next.js 16](https://nextjs.org/) (App Router Mimarisi)
- **Kütüphane:** React 19
- **Dil:** TypeScript

### Stil & UI Bileşenleri
- **CSS Framework:** [Tailwind CSS v4](https://tailwindcss.com/)
- **UI Kütüphanesi:** [shadcn/ui](https://ui.shadcn.com/) & Base UI (`@base-ui/react`)
- **İkonlar:** Lucide React (`lucide-react`)
- **Grafikler:** Recharts (`recharts`)
- **Animasyonlar:** `tw-animate-css`
- **Bildirimler:** Sonner (`sonner`)

### State Yönetimi & Veri Çekme (Data Fetching)
- **Global State:** Projede genel olarak harici bir state yönetim kütüphanesi (Zustand, Redux vb.) kullanılmamaktadır. Next.js'in App Router yapısı gereği **React Server Components (RSC)** ve **Server Actions** mimarisi kullanılarak state yönetimi sunucu tarafında (Server-side) veya Hook'lar aracılığıyla istemci tarafında (Client-side) yönetilmektedir.
- **HTTP İstemcisi:** Axios (`axios`) üzerinden backend (FastAPI) ile haberleşilmektedir.

### Form Yönetimi & Doğrulama (Validation)
- **Form Kütüphanesi:** React Hook Form (`react-hook-form`)
- **Şema Doğrulaması:** Zod (`zod` & `@hookform/resolvers`)

### Kimlik Doğrulama & Veritabanı Servisleri (BaaS)
- **Platform:** [Supabase](https://supabase.com/)
- **Kütüphaneler:** `@supabase/supabase-js`, `@supabase/ssr` (Next.js Server-Side Rendering entegrasyonu için)

---

## 📁 Klasör Yapısı (Folder Structure)

Projenin `frontend/` klasörü aşağıdaki standart modern Next.js yapısını takip etmektedir:

- `app/`: Next.js App Router sayfaları (`page.tsx`), layout yapıları (`layout.tsx`) ve Server Actions.
- `components/`: Tekrar kullanılabilir UI bileşenleri. Genellikle `shadcn/ui` bileşenleri `components/ui/` altında yer alır.
- `lib/`: Yardımcı (utility) fonksiyonlar, Supabase istemci/sunucu konfigürasyonları ve ortak ayarlar.
- `services/`: Backend API'ları ile haberleşen fonksiyonların ve servis çağrılarının bulunduğu dizin.
- `types/`: Projede kullanılan ortak TypeScript tipleri (interfaces, types).

---

## 🚀 Geliştirme Komutları

Geliştirme ortamını başlatmak için ana README dosyasındaki adımları izleyebilirsiniz. Frontend özelinde kullanılan bazı temel npm scriptleri:

- `npm run dev` : Geliştirme (development) ortamını başlatır (http://localhost:3000).
- `npm run build` : Projeyi production ortamı için derler.
- `npm run start` : Derlenmiş production uygulamasını başlatır.
- `npm run lint` : ESLint kullanarak kod kalitesini ve standartlarını denetler.
