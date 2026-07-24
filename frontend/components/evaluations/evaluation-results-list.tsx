import { ClipboardCheck } from "lucide-react";

import {
  Card,
  CardContent,
} from "@/components/ui/card";

import { CriterionResultCard } from
  "@/components/evaluations/criterion-result-card";

import type {
  CriterionResult,
} from "@/types/evaluation";

interface EvaluationResultsListProps {
  results: CriterionResult[];
}

export function EvaluationResultsList({
  results,
}: EvaluationResultsListProps) {
  if (!results.length) {
    return (
      <Card>
        <CardContent className="flex min-h-48 flex-col items-center justify-center text-center">
          <ClipboardCheck className="mb-4 h-10 w-10 text-muted-foreground" />

          <h3 className="font-semibold">
            Henüz kriter sonucu yok
          </h3>

          <p className="mt-2 max-w-md text-sm text-muted-foreground">
            Değerlendirme tamamlandığında kriter
            sonuçları burada görüntülenecek.
          </p>
        </CardContent>
      </Card>
    );
  }

  const groupedResults = groupByCategory(
    results,
  );

  return (
    <div className="space-y-8">
      {Object.entries(groupedResults).map(
        ([category, categoryResults]) => (
          <section
            key={category}
            className="space-y-4"
          >
            <div>
              <h3 className="text-lg font-semibold">
                {category}
              </h3>

              <p className="text-sm text-muted-foreground">
                {categoryResults.length} kriter
              </p>
            </div>

            <div className="space-y-4">
              {categoryResults.map((result) => (
                <CriterionResultCard
                  key={result.id}
                  result={result}
                />
              ))}
            </div>
          </section>
        ),
      )}
    </div>
  );
}

function groupByCategory(
  results: CriterionResult[],
): Record<string, CriterionResult[]> {
  return results.reduce<
    Record<string, CriterionResult[]>
  >((groups, result) => {
    const category =
      result.criteria.category_name ??
      "Diğer kriterler";

    groups[category] ??= [];
    groups[category].push(result);

    return groups;
  }, {});
}