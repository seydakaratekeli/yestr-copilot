// Tarih formatlama (Örn: 14 Temmuz 2026)
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return "Belirtilmedi";
  return new Date(dateString).toLocaleDateString("tr-TR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

// Para birimi formatlama (Örn: ₺1.250.000,00)
export function formatCurrency(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return "Belirtilmedi";
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
  }).format(amount);
}

// Alan formatlama (Örn: 150 m²)
export function formatArea(area: number | null | undefined): string {
  if (!area) return "Belirtilmedi";
  return `${new Intl.NumberFormat("tr-TR").format(area)} m²`;
}

// Proje durum etiketleri (Veritabanındaki İngilizce değerleri Türkçe yapar)
export function getProjectStatusLabel(status: string | null | undefined): string {
  const statuses: Record<string, string> = {
    draft: "Taslak",
    documents_uploaded: "Belgeler yüklendi",
    processing: "İşleniyor",
    analyzed: "Analiz edildi",
    archived: "Arşivlendi",
  };
  return status ? (statuses[status] || status) : "Bilinmiyor";
}

// Proje türü etiketleri
export function getProjectTypeLabel(type: string | null | undefined): string {
  const types: Record<string, string> = {
    new_building: "Yeni bina",
    existing_building: "Mevcut bina / renovasyon",
  };
  return type ? (types[type] || type) : "Bilinmiyor";
}

export function getBuildingTypeLabel(type: string | null | undefined): string {
  const types: Record<string, string> = {
    public: "Kamu binası",
    office: "Ofis",
    education: "Eğitim binası",
    healthcare: "Sağlık yapısı",
    residential: "Konut",
    commercial: "Ticari yapı",
    mixed: "Karma kullanım",
    other: "Diğer",
  };

  return type ? (types[type] || type) : "Belirtilmedi";
}

export function getFacadeDirectionLabel(
  direction: string | null | undefined,
): string {
  const directions: Record<string, string> = {
    north: "Kuzey",
    northeast: "Kuzeydoğu",
    east: "Doğu",
    southeast: "Güneydoğu",
    south: "Güney",
    southwest: "Güneybatı",
    west: "Batı",
    northwest: "Kuzeybatı",
  };

  return direction
    ? (directions[direction] || direction)
    : "Belirtilmedi";
}

export function getCertificateLevelLabel(
  level: string | null | undefined,
): string {
  const levels: Record<string, string> = {
    pass: "Asgari uygunluk",
    good: "İyi",
    very_good: "Çok iyi",
    national_excellence: "Ulusal üstünlük",
  };

  return level ? (levels[level] || level) : "Belirtilmedi";
}
