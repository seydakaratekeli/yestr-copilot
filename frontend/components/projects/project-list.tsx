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
    planning: "Planlama Aşamasında",
    in_progress: "Devam Ediyor",
    completed: "Tamamlandı",
    suspended: "Askıya Alındı",
  };
  return status ? (statuses[status] || status) : "Bilinmiyor";
}

// Proje türü etiketleri
export function getProjectTypeLabel(type: string | null | undefined): string {
  const types: Record<string, string> = {
    residential: "Konut",
    commercial: "Ticari",
    industrial: "Endüstriyel",
    mixed_use: "Karma Kullanım",
  };
  return type ? (types[type] || type) : "Bilinmiyor";
}
