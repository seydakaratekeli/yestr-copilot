import {
  AlertTriangle,
  CheckCircle2,
  CircleHelp,
  Gauge,
  XCircle,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

import {
  formatPercentage,
  formatScore,
} from "@/lib/evaluation-utils";

import type {
  EvaluationSummary,
} from "@/types/evaluation";

interface EvaluationSummaryCardProps {
  evaluation: EvaluationSummary;
}

export function EvaluationSummaryCard({
  evaluation,
}: EvaluationSummaryCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gauge className="h-5 w-5" />
          Tahmini ön değerlendirme
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <SummaryMetric
            label="Tahmini puan"
            value={`${formatScore(
              evaluation.total_score,
            )} / ${formatScore(
              evaluation.maximum_score,
            )}`}
          />

          <SummaryMetric
            label="Başarı oranı"
            value={formatPercentage(
              evaluation.score_percentage,
            )}
          />

          <SummaryMetric
            label="Sağlanan"
            value={evaluation.satisfied_count}
            icon={
              <CheckCircle2 className="h-4 w-4" />
            }
          />

          <SummaryMetric
            label="Sağlanmayan"
            value={
              evaluation.not_satisfied_count
            }
            icon={
              <XCircle className="h-4 w-4" />
            }
          />

          <SummaryMetric
            label="İnceleme gereken"
            value={
              evaluation.uncertain_count +
              evaluation.manual_review_count
            }
            icon={
              <CircleHelp className="h-4 w-4" />
            }
          />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Toplam puan oranı</span>

            <span className="font-medium">
              {formatPercentage(
                evaluation.score_percentage,
              )}
            </span>
          </div>

          <Progress
            value={Math.min(
              100,
              Math.max(
                0,
                evaluation.score_percentage,
              ),
            )}
          />
        </div>

        <div className="flex gap-3 rounded-lg border bg-muted/20 p-4 text-sm">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />

          <p className="text-muted-foreground">
            Bu sonuç temsili kriter setine göre
            oluşturulmuş otomatik bir ön
            değerlendirmedir. Resmî YeS-TR
            sertifikasyon sonucu değildir.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function SummaryMetric({
  label,
  value,
  icon,
}: {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        {icon}
        <span>{label}</span>
      </div>

      <p className="mt-2 text-2xl font-semibold">
        {value}
      </p>
    </div>
  );
}