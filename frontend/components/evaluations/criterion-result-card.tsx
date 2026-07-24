import {
  AlertTriangle,
  BookOpen,
  FileText,
  SearchCheck,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

import { CriterionResultBadge } from
  "@/components/evaluations/criterion-result-badge";

import {
  formatScore,
} from "@/lib/evaluation-utils";

import type {
  CriterionResult,
} from "@/types/evaluation";

interface CriterionResultCardProps {
  result: CriterionResult;
}

export function CriterionResultCard({
  result,
}: CriterionResultCardProps) {
  const confidencePercentage =
    Math.round(result.confidence * 100);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
          <div>
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <Badge variant="outline">
                {result.criteria.code}
              </Badge>

              {result.criteria.category_name && (
                <Badge variant="secondary">
                  {result.criteria.category_name}
                </Badge>
              )}
            </div>

            <CardTitle className="text-lg">
              {result.criteria.title}
            </CardTitle>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <CriterionResultBadge
              status={result.result_status}
            />

            <Badge variant="outline">
              {formatScore(
                result.awarded_score,
              )}
              {" / "}
              {formatScore(
                result.maximum_score,
              )}
              {" puan"}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {result.evidence_summary && (
          <div className="rounded-lg border bg-muted/20 p-4">
            <div className="mb-2 flex items-center gap-2 text-sm font-medium">
              <SearchCheck className="h-4 w-4" />
              Kanıt özeti
            </div>

            <p className="text-sm leading-6 text-muted-foreground">
              {result.evidence_summary}
            </p>
          </div>
        )}

        <ExtractedValues
          values={result.extracted_values}
        />

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Kanıt güven düzeyi</span>

            <span>
              %{confidencePercentage}
            </span>
          </div>

          <Progress
            value={confidencePercentage}
          />
        </div>

        <CriterionCitations
          citations={result.citations}
        />

        {result.missing_information.length >
          0 && (
          <div className="rounded-lg border p-4">
            <p className="mb-2 text-sm font-medium">
              Eksik bilgiler
            </p>

            <ul className="space-y-1 text-sm text-muted-foreground">
              {result.missing_information.map(
                (item, index) => (
                  <li
                    key={`${item}-${index}`}
                  >
                    • {item}
                  </li>
                ),
              )}
            </ul>
          </div>
        )}

        {result.warnings.length > 0 && (
          <Alert>
            <AlertTriangle className="h-4 w-4" />

            <AlertDescription>
              <ul className="space-y-1">
                {result.warnings.map(
                  (warning, index) => (
                    <li
                      key={`${warning}-${index}`}
                    >
                      • {warning}
                    </li>
                  ),
                )}
              </ul>
            </AlertDescription>
          </Alert>
        )}

        {result.requires_manual_review && (
          <Alert>
            <BookOpen className="h-4 w-4" />

            <AlertDescription>
              Bu kriter otomatik sonuçtan önce uzman
              tarafından incelenmelidir.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}

function ExtractedValues({
  values,
}: {
  values: Record<string, unknown>;
}) {
  const entries = Object.entries(values).filter(
    ([, value]) =>
      value !== null &&
      value !== undefined &&
      value !== "",
  );

  if (!entries.length) {
    return null;
  }

  return (
    <div>
      <p className="mb-3 text-sm font-medium">
        Belgelerden çıkarılan değerler
      </p>

      <div className="grid gap-3 sm:grid-cols-2">
        {entries.map(([key, value]) => (
          <div
            key={key}
            className="rounded-lg border p-3"
          >
            <p className="text-xs text-muted-foreground">
              {formatFieldName(key)}
            </p>

            <p className="mt-1 font-medium">
              {formatValue(value)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function CriterionCitations({
  citations,
}: {
  citations: CriterionResult["citations"];
}) {
  if (!citations.length) {
    return (
      <div className="rounded-lg border p-4 text-sm text-muted-foreground">
        Bu kriter için doğrulanabilir belge kaynağı
        bulunamadı.
      </div>
    );
  }

  return (
    <div>
      <p className="mb-3 flex items-center gap-2 text-sm font-medium">
        <FileText className="h-4 w-4" />
        Kullanılan kaynaklar
      </p>

      <div className="space-y-3">
        {citations.map((citation) => (
          <div
            key={`${citation.source_id}-${citation.document_id}`}
            className="rounded-lg border p-4"
          >
            <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
              <div>
                <p className="break-words text-sm font-medium">
                  {citation.original_filename}
                </p>

                <p className="mt-1 text-xs text-muted-foreground">
                  Sayfa {citation.page_number}
                  {" · "}
                  Benzerlik %
                  {Math.round(
                    citation.similarity * 100,
                  )}
                </p>
              </div>

              <Badge variant="outline">
                {citation.source_id}
              </Badge>
            </div>

            <blockquote className="mt-3 border-l-2 pl-3 text-sm leading-6 text-muted-foreground">
              {citation.excerpt}
            </blockquote>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatFieldName(
  value: string,
): string {
  const labels: Record<string, string> = {
    maximum_flow_rate_l_min:
      "Maksimum debi",
    maximum_flow_rate_unit:
      "Debi birimi",
    photovoltaic_system_present:
      "Fotovoltaik sistem",
    rainwater_system_present:
      "Yağmur suyu depolama sistemi",
    facade_insulation_evidence:
      "Dış cephe ısı yalıtımı kanıtı",
  };

  if (labels[value]) {
    return labels[value];
  }

  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}

function formatValue(
  value: unknown,
): string {
  if (typeof value === "boolean") {
    return value ? "Evet" : "Hayır";
  }

  if (
    typeof value === "object" &&
    value !== null
  ) {
    return JSON.stringify(
      value,
      null,
      2,
    );
  }

  return String(value);
}
