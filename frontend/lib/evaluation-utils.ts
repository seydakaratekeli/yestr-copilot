import type {
  CriterionResultStatus,
  EvaluationStatus,
} from "@/types/evaluation";

export function getEvaluationStatusLabel(
  status: EvaluationStatus,
): string {
  const labels: Record<EvaluationStatus, string> = {
    queued: "Sırada",
    processing: "Değerlendiriliyor",
    completed: "Tamamlandı",
    failed: "Başarısız",
  };

  return labels[status];
}

export function getCriterionResultLabel(
  status: CriterionResultStatus,
): string {
  const labels: Record<
    CriterionResultStatus,
    string
  > = {
    satisfied: "Sağlandı",
    not_satisfied: "Sağlanmadı",
    uncertain: "Belirsiz",
    not_applicable: "Uygulanamaz",
    manual_review: "Manuel inceleme",
    not_evaluated: "Değerlendirilmedi",
    failed: "İşlem başarısız",
  };

  return labels[status];
}

export function formatScore(
  value: number,
): string {
  return Number.isInteger(value)
    ? value.toString()
    : value.toFixed(2);
}

export function formatPercentage(
  value: number,
): string {
  return `%${Math.round(value)}`;
}