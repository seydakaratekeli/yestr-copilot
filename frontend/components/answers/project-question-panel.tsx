"use client";

import {
  FormEvent,
  useState,
} from "react";
import {
  AlertTriangle,
  BookOpen,
  Bot,
  FileText,
  LoaderCircle,
  MessageCircleQuestion,
  Search,
} from "lucide-react";

import { createClient } from "@/lib/supabase/client";
import {
  formatConfidence,
  getAnswerStatusLabel,
  getConfidenceLabel,
} from "@/lib/answer-utils";
import {
  getDocumentTypeLabel,
} from "@/lib/document-utils";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";

import type {
  AnswerCitation,
  ProjectQuestionResponse,
} from "@/types/answer";
import type { DocumentType } from "@/types/document";

interface ProjectQuestionPanelProps {
  projectId: string;
  documentCount: number;
}

const EXAMPLE_QUESTIONS = [
  "Projede güneş enerjisi sistemi bulunuyor mu?",
  "Lavabo bataryalarının maksimum debisi nedir?",
  "Yağmur suyu depolama kapasitesi ne kadar?",
  "Dış cephe ısı yalıtımı hakkında hangi bilgiler var?",
];

export function ProjectQuestionPanel({
  projectId,
  documentCount,
}: ProjectQuestionPanelProps) {
  const [question, setQuestion] = useState("");
  const [result, setResult] =
    useState<ProjectQuestionResponse | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [isLoading, setIsLoading] =
    useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const normalizedQuestion = question.trim();

    if (normalizedQuestion.length < 3) {
      setError(
        "Lütfen en az 3 karakterden oluşan bir soru yazın.",
      );
      return;
    }

    setError(null);
    setResult(null);
    setIsLoading(true);

    try {
      const supabase = createClient();

      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession();

      if (
        sessionError ||
        !session?.access_token
      ) {
        throw new Error(
          "Oturum bilgisi alınamadı. Lütfen tekrar giriş yapın.",
        );
      }

      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL;

      if (!apiUrl) {
        throw new Error(
          "Backend API adresi tanımlanmamış.",
        );
      }

      const response = await fetch(
        `${apiUrl}/projects/${projectId}/answer`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization:
              `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({
            question: normalizedQuestion,
            search_limit: 6,
            minimum_similarity: 0.3,
          }),
        },
      );

      const responseBody = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof responseBody.detail === "string"
            ? responseBody.detail
            : "Soru yanıtlanamadı.",
        );
      }

      setResult(
        responseBody as ProjectQuestionResponse,
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Soru yanıtlanırken beklenmeyen bir hata oluştu.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function selectExampleQuestion(
    exampleQuestion: string,
  ) {
    setQuestion(exampleQuestion);
    setError(null);
  }

  if (documentCount === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircleQuestion className="h-5 w-5" />
            Belgelere Sor
          </CardTitle>

          <CardDescription>
            Proje belgeleri üzerinde kaynaklı soru-cevap
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Alert>
            <FileText className="h-4 w-4" />

            <AlertDescription>
              Soru sorabilmek için önce projeye en az bir
              belge yüklemelisiniz.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircleQuestion className="h-5 w-5" />
            Belgelere Sor
          </CardTitle>

          <CardDescription>
            Yanıtlar yalnızca bu projeye yüklenen ve işlenen
            belgelerden üretilir.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label htmlFor="project-question">
                Sorunuz
              </Label>

              <Textarea
                id="project-question"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                rows={4}
                maxLength={1000}
                disabled={isLoading}
                placeholder={
                  "Örneğin: Yağmur suyu depolama kapasitesi nedir?"
                }
              />

              <div className="flex justify-between gap-4 text-xs text-muted-foreground">
                <span>
                  Belgede bulunmayan bilgiler tahmin edilmez.
                </span>

                <span>
                  {question.length}/1000
                </span>
              </div>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={
                  isLoading ||
                  question.trim().length < 3
                }
              >
                {isLoading ? (
                  <>
                    <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                    Belgeler inceleniyor...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Soruyu yanıtla
                  </>
                )}
              </Button>
            </div>
          </form>

          <div className="mt-6 space-y-3">
            <p className="text-sm font-medium">
              Örnek sorular
            </p>

            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUESTIONS.map(
                (exampleQuestion) => (
                  <Button
                    key={exampleQuestion}
                    type="button"
                    variant="secondary"
                    className="rounded-full text-xs font-medium hover:bg-primary/10 hover:text-primary transition-colors border shadow-sm"
                    disabled={isLoading}
                    onClick={() =>
                      selectExampleQuestion(
                        exampleQuestion,
                      )
                    }
                  >
                    {exampleQuestion}
                  </Button>
                ),
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {result && (
        <AnswerResult result={result} />
      )}
    </div>
  );
}

function AnswerResult({
  result,
}: {
  result: ProjectQuestionResponse;
}) {
  const confidencePercentage =
    Math.round(result.confidence * 100);

  return (
    <div className="space-y-5">
      <Card>
        <CardHeader>
          <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Belge analizi
              </CardTitle>

              <CardDescription className="mt-1">
                {result.question}
              </CardDescription>
            </div>

            <AnswerStatusBadge
              status={result.status}
            />
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="rounded-lg border bg-muted/20 p-4">
            <p className="whitespace-pre-wrap leading-7">
              {result.answer}
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">
                Cevap güven düzeyi
              </span>

              <span>
                {getConfidenceLabel(
                  result.confidence,
                )}{" "}
                ·{" "}
                {formatConfidence(
                  result.confidence,
                )}
              </span>
            </div>

            <Progress
              value={confidencePercentage}
            />
          </div>

          <p className="text-xs text-muted-foreground">
            {result.retrieved_source_count} belge parçası
            incelendi. Bu çıktı ön değerlendirme niteliğindedir
            ve resmî sertifikasyon kararı değildir.
          </p>
        </CardContent>
      </Card>

      <CitationSection
        citations={result.citations}
      />

      {result.missing_information.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Eksik bilgiler
            </CardTitle>

            <CardDescription>
              Daha güçlü bir değerlendirme için gerekli bilgiler
            </CardDescription>
          </CardHeader>

          <CardContent>
            <ul className="space-y-2">
              {result.missing_information.map(
                (information, index) => (
                  <li
                    key={`${information}-${index}`}
                    className="flex gap-3 text-sm"
                  >
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-muted-foreground" />

                    <span>{information}</span>
                  </li>
                ),
              )}
            </ul>
          </CardContent>
        </Card>
      )}

      {result.warnings.length > 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />

          <AlertDescription>
            <div className="space-y-2">
              <p className="font-medium">
                Değerlendirme uyarıları
              </p>

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
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

function AnswerStatusBadge({
  status,
}: {
  status: ProjectQuestionResponse["status"];
}) {
  if (status === "answered") {
    return (
      <Badge>
        {getAnswerStatusLabel(status)}
      </Badge>
    );
  }

  if (status === "conflicting_evidence") {
    return (
      <Badge variant="destructive">
        {getAnswerStatusLabel(status)}
      </Badge>
    );
  }

  return (
    <Badge variant="secondary">
      {getAnswerStatusLabel(status)}
    </Badge>
  );
}

function CitationSection({
  citations,
}: {
  citations: AnswerCitation[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <BookOpen className="h-5 w-5" />
          Kullanılan kanıtlar
        </CardTitle>

        <CardDescription>
          Cevabın dayandığı dosya ve sayfa parçaları
        </CardDescription>
      </CardHeader>

      <CardContent>
        {citations.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Cevabı destekleyen yeterli kaynak bulunamadı.
          </p>
        ) : (
          <div className="space-y-4">
            {citations.map((citation) => (
              <CitationCard
                key={citation.source_id}
                citation={citation}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function CitationCard({
  citation,
}: {
  citation: AnswerCitation;
}) {
  const documentTypeLabel =
    citation.document_type
      ? getDocumentTypeLabel(
          citation.document_type as DocumentType,
        )
      : "Belge";

  return (
    <div className="rounded-lg border p-4">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
        <div className="flex min-w-0 gap-3">
          <FileText className="mt-1 h-5 w-5 shrink-0 text-muted-foreground" />

          <div className="min-w-0">
            <p className="break-words font-medium">
              {citation.original_filename}
            </p>

            <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-sm text-muted-foreground">
              <span>{documentTypeLabel}</span>
              <span>Sayfa {citation.page_number}</span>
              <span>
                Benzerlik %
                {Math.round(
                  citation.similarity * 100,
                )}
              </span>
            </div>
          </div>
        </div>

        <Badge variant="outline">
          {citation.source_id}
        </Badge>
      </div>

      <blockquote className="mt-4 border-l-2 pl-4 text-sm leading-6 text-muted-foreground">
        {citation.excerpt}
      </blockquote>
    </div>
  );
}