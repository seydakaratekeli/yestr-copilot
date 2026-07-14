import type { DocumentType } from "@/types/document";

export const DOCUMENT_TYPE_OPTIONS: Array<{
  value: DocumentType;
  label: string;
}> = [
  {
    value: "site_plan",
    label: "Vaziyet planı",
  },
  {
    value: "floor_plan",
    label: "Kat planı",
  },
  {
    value: "section",
    label: "Kesit",
  },
  {
    value: "facade",
    label: "Cephe",
  },
  {
    value: "energy_report",
    label: "Enerji performans raporu",
  },
  {
    value: "technical_specification",
    label: "Teknik şartname",
  },
  {
    value: "product_datasheet",
    label: "Ürün teknik föyü",
  },
  {
    value: "mechanical_report",
    label: "Mekanik proje raporu",
  },
  {
    value: "electrical_report",
    label: "Elektrik proje raporu",
  },
  {
    value: "other",
    label: "Diğer",
  },
];

export function getDocumentTypeLabel(
  type: DocumentType,
): string {
  return (
    DOCUMENT_TYPE_OPTIONS.find(
      (option) => option.value === type,
    )?.label ?? type
  );
}

export function formatFileSize(
  bytes: number,
): string {
  if (bytes === 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const unitIndex = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1,
  );

  const value = bytes / 1024 ** unitIndex;

  return `${value.toFixed(
    unitIndex === 0 ? 0 : 1,
  )} ${units[unitIndex]}`;
}