import type { AnswerStatus } from "@/types/answer";

export function getAnswerStatusLabel(
  status: AnswerStatus,
): string {
  const labels: Record<AnswerStatus, string> = {
    answered: "Yanıtlandı",
    insufficient_evidence: "Yetersiz kanıt",
    conflicting_evidence: "Çelişkili kanıt",
  };

  return labels[status];
}

export function getConfidenceLabel(
  confidence: number,
): string {
  if (confidence >= 0.8) {
    return "Yüksek";
  }

  if (confidence >= 0.55) {
    return "Orta";
  }

  return "Düşük";
}

export function formatConfidence(
  confidence: number,
): string {
  return `%${Math.round(confidence * 100)}`;
}