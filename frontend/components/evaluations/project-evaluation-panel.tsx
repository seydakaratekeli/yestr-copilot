"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  ClipboardCheck,
  LoaderCircle,
  Play,
  RefreshCw,
} from "lucide-react";

import {
  getEvaluation,
  listCriterionSets,
  listEvaluations,
  rerunEvaluation,
  startEvaluation,
} from "@/services/evaluation-api";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { EvaluationStatusBadge } from "./evaluation-status-badge";
import { EvaluationSummaryCard } from "./evaluation-summary-card";
import { EvaluationResultsList } from "./evaluation-results-list";

import type {
  CriterionSet,
  EvaluationDetail,
  EvaluationSummary,
} from "@/types/evaluation";
import {
  getEvaluationStatusLabel,
} from "@/lib/evaluation-utils";

interface ProjectEvaluationPanelProps {
  projectId: string;
  documentCount: number;
}

function formatEvaluationLabel(
  evaluation: EvaluationSummary,
) {
  const createdAt = new Date(
    evaluation.created_at,
  ).toLocaleString("tr-TR");

  const status = getEvaluationStatusLabel(
    evaluation.status,
  );

  if (evaluation.status !== "completed") {
    return `${createdAt} · ${status}`;
  }

  const percentage = Math.round(
    evaluation.score_percentage,
  );

  return `${createdAt} · ${status} · %${percentage}`;
}

export function ProjectEvaluationPanel({
  projectId,
  documentCount,
}: ProjectEvaluationPanelProps) {
  const [criterionSets, setCriterionSets] =
    useState<CriterionSet[]>([]);

  const [
    selectedCriterionSetId,
    setSelectedCriterionSetId,
  ] = useState("");

  const [evaluations, setEvaluations] =
    useState<EvaluationSummary[]>([]);

  const [
    selectedEvaluationId,
    setSelectedEvaluationId,
  ] = useState<string | null>(null);

  const [detail, setDetail] =
    useState<EvaluationDetail | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [isStarting, setIsStarting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const selectedCriterionSet =
    criterionSets.find(
      (item) =>
        item.id === selectedCriterionSetId,
    );

  const selectedEvaluation =
    evaluations.find(
      (item) =>
        item.id === selectedEvaluationId,
    ) ??
    (
      detail?.evaluation.id ===
      selectedEvaluationId
        ? detail.evaluation
        : undefined
    );

  const loadEvaluationDetail =
    useCallback(
      async (
        evaluationId: string,
      ) => {
        const evaluationDetail =
          await getEvaluation(
            projectId,
            evaluationId,
          );

        setDetail(evaluationDetail);

        return evaluationDetail;
      },
      [projectId],
    );

  const initialize = useCallback(
    async () => {
      setIsLoading(true);
      setError(null);

      try {
        const [
          criterionSetItems,
          evaluationItems,
        ] = await Promise.all([
          listCriterionSets(),
          listEvaluations(projectId),
        ]);

        setCriterionSets(
          criterionSetItems,
        );

        setEvaluations(
          evaluationItems,
        );

        setSelectedCriterionSetId("");
        setSelectedEvaluationId(null);
        setDetail(null);
      } catch (initializationError) {
        setError(
          initializationError
            instanceof Error
            ? initializationError.message
            : "Değerlendirme bilgileri yüklenemedi.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [projectId],
  );

  useEffect(() => {
    void initialize();
  }, [initialize]);

  const activeStatus =
    detail?.evaluation.status;

  useEffect(() => {
    if (
      activeStatus !== "queued" &&
      activeStatus !== "processing"
    ) {
      return;
    }

    const intervalId =
      window.setInterval(() => {
        if (selectedEvaluationId) {
          void refreshSelectedEvaluation(
            selectedEvaluationId,
          );
        }
      }, 3000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [
    activeStatus,
    selectedEvaluationId,
  ]);

  async function refreshSelectedEvaluation(
    evaluationId: string,
  ) {
    try {
      const evaluationDetail =
        await loadEvaluationDetail(
          evaluationId,
        );

      const items =
        await listEvaluations(projectId);

      setEvaluations(items);

      if (
        evaluationDetail.evaluation.status ===
          "completed" ||
        evaluationDetail.evaluation.status ===
          "failed"
      ) {
        setIsStarting(false);
      }
    } catch (refreshError) {
      setError(
        refreshError instanceof Error
          ? refreshError.message
          : "Değerlendirme güncellenemedi.",
      );
    }
  }

  async function handleStartEvaluation() {
    if (!selectedCriterionSetId) {
      setError(
        "Lütfen bir kriter seti seçin.",
      );
      return;
    }

    setIsStarting(true);
    setError(null);

    try {
      const response =
        await startEvaluation(
          projectId,
          selectedCriterionSetId,
        );

      await refreshSelectedEvaluation(
        response.evaluation_id,
      );

      setSelectedEvaluationId(
        response.evaluation_id,
      );
    } catch (startError) {
      setError(
        startError instanceof Error
          ? startError.message
          : "Değerlendirme başlatılamadı.",
      );

      setIsStarting(false);
    }
  }

  async function handleRerun() {
    if (!selectedEvaluationId) {
      return;
    }

    setIsStarting(true);
    setError(null);

    try {
      await rerunEvaluation(
        projectId,
        selectedEvaluationId,
      );

      await refreshSelectedEvaluation(
        selectedEvaluationId,
      );
    } catch (rerunError) {
      setError(
        rerunError instanceof Error
          ? rerunError.message
          : "Değerlendirme yeniden başlatılamadı.",
      );

      setIsStarting(false);
    }
  }

  async function handleEvaluationSelection(
    evaluationId: string,
  ) {
    setSelectedEvaluationId(
      evaluationId,
    );

    setError(null);

    try {
      await loadEvaluationDetail(
        evaluationId,
      );
    } catch (selectionError) {
      setError(
        selectionError instanceof Error
          ? selectionError.message
          : "Değerlendirme açılamadı.",
      );
    }
  }

  if (documentCount === 0) {
    return (
      <Alert>
        <ClipboardCheck className="h-4 w-4" />

        <AlertDescription>
          Ön değerlendirme başlatmak için önce
          projeye en az bir işlenmiş belge
          yüklemelisiniz.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardCheck className="h-5 w-5" />
            YeS-TR ön değerlendirme
          </CardTitle>

          <CardDescription>
            Proje belgelerini seçilen kriter setine
            göre otomatik olarak inceleyin.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-5">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>
                {error}
              </AlertDescription>
            </Alert>
          )}

          <div className="grid gap-4 lg:grid-cols-[1fr_auto]">
            <div className="space-y-2">
              <p className="text-sm font-medium">
                Kriter seti
              </p>

              <Select
                value={selectedCriterionSetId}
                onValueChange={(value) => {
                  setSelectedCriterionSetId(
                    value ?? "",
                  );
                }}
                disabled={isLoading || isStarting}
              >
                <SelectTrigger className="min-h-10 w-full">
                  <SelectValue placeholder="Kriter seti seçin">
                    {selectedCriterionSet
                      ? `${selectedCriterionSet.name} · v${selectedCriterionSet.version}`
                      : null}
                  </SelectValue>
                </SelectTrigger>

                <SelectContent
                  alignItemWithTrigger={false}
                  className="max-w-[calc(100vw-2rem)]"
                >
                  {criterionSets.map(
                    (criterionSet) => (
                      <SelectItem
                        key={criterionSet.id}
                        value={criterionSet.id}
                      >
                        {criterionSet.name}
                        {" · "}
                        v{criterionSet.version}
                      </SelectItem>
                    ),
                  )}
                </SelectContent>
              </Select>

              {selectedCriterionSet?.description && (
                <p className="text-xs text-muted-foreground">
                  {selectedCriterionSet.description}
                </p>
              )}
            </div>

            <div className="flex items-end">
              <Button
                onClick={
                  handleStartEvaluation
                }
                disabled={
                  isLoading ||
                  isStarting ||
                  !selectedCriterionSetId
                }
              >
                {isStarting ? (
                  <>
                    <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                    Değerlendiriliyor
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Ön değerlendirmeyi başlat
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {evaluations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Değerlendirme geçmişi
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-3">
            <Select
              value={selectedEvaluationId ?? ""}
              onValueChange={(value) => {
                if (value) {
                  void handleEvaluationSelection(
                    value,
                  );
                }
              }}
            >
              <SelectTrigger className="min-h-10 w-full">
                <SelectValue placeholder="Değerlendirme seçin">
                  {selectedEvaluation
                    ? formatEvaluationLabel(
                        selectedEvaluation,
                      )
                    : null}
                </SelectValue>
              </SelectTrigger>

              <SelectContent
                alignItemWithTrigger={false}
                className="max-w-[calc(100vw-2rem)]"
              >
                {evaluations.map(
                  (evaluation) => (
                    <SelectItem
                      key={evaluation.id}
                      value={evaluation.id}
                    >
                      {formatEvaluationLabel(
                        evaluation,
                      )}
                    </SelectItem>
                  ),
                )}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      )}

      {detail && (
        <>
          <Card>
            <CardContent className="flex flex-col justify-between gap-4 p-5 sm:flex-row sm:items-center">
              <div>
                <p className="text-sm text-muted-foreground">
                  Değerlendirme durumu
                </p>

                <div className="mt-2">
                  <EvaluationStatusBadge
                    status={
                      detail.evaluation.status
                    }
                  />
                </div>
              </div>

              <Button
                variant="outline"
                onClick={handleRerun}
                disabled={
                  isStarting ||
                  detail.evaluation.status ===
                    "queued" ||
                  detail.evaluation.status ===
                    "processing"
                }
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Yeniden değerlendir
              </Button>
            </CardContent>
          </Card>

          {(
            detail.evaluation.status ===
              "queued" ||
            detail.evaluation.status ===
              "processing"
          ) && (
            <Card>
              <CardContent className="flex min-h-40 items-center justify-center">
                <div className="text-center">
                  <LoaderCircle className="mx-auto h-8 w-8 animate-spin" />

                  <p className="mt-4 font-medium">
                    Proje belgeleri kriterlere göre
                    inceleniyor
                  </p>

                  <p className="mt-1 text-sm text-muted-foreground">
                    Sonuçlar otomatik olarak
                    yenilenecek.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {detail.evaluation.status ===
            "failed" && (
            <Alert variant="destructive">
              <AlertDescription>
                {detail.evaluation.error_message ??
                  "Değerlendirme tamamlanamadı."}
              </AlertDescription>
            </Alert>
          )}

          {detail.evaluation.status ===
            "completed" && (
            <>
              <EvaluationSummaryCard
                evaluation={
                  detail.evaluation
                }
              />

              <section className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold">
                    Kriter sonuçları
                  </h3>

                  <p className="text-sm text-muted-foreground">
                    Her kriter için çıkarılan
                    değerler, puan ve belge
                    kanıtları
                  </p>
                </div>

                <EvaluationResultsList
                  results={detail.results}
                />
              </section>
            </>
          )}
        </>
      )}
    </div>
  );
}
