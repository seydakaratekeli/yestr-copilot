"use client";

import {
  ChangeEvent,
  FormEvent,
  useMemo,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import {
  FileText,
  LoaderCircle,
  Trash2,
  Upload,
} from "lucide-react";

import { createClient } from "@/lib/supabase/client";
import {
  DOCUMENT_TYPE_OPTIONS,
  formatFileSize,
} from "@/lib/document-utils";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
} from "@/components/ui/card";

import type {
  DocumentType,
  MultipleDocumentUploadResponse,
} from "@/types/document";


interface SelectedDocument {
  id: string;
  file: File;
  documentType: DocumentType;
}


interface DocumentUploadFormProps {
  projectId: string;
}


export function DocumentUploadForm({
  projectId,
}: DocumentUploadFormProps) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  const [documents, setDocuments] = useState<
    SelectedDocument[]
  >([]);

  const [isUploading, setIsUploading] =
    useState(false);

  const [error, setError] = useState<string | null>(
    null,
  );

  const [successMessage, setSuccessMessage] =
    useState<string | null>(null);

  const totalSize = useMemo(
    () =>
      documents.reduce(
        (sum, document) =>
          sum + document.file.size,
        0,
      ),
    [documents],
  );

  function handleFileSelection(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    setError(null);
    setSuccessMessage(null);

    const selectedFiles = Array.from(
      event.target.files ?? [],
    );

    if (!selectedFiles.length) {
      return;
    }

    const pdfFiles = selectedFiles.filter(
      (file) =>
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf"),
    );

    if (pdfFiles.length !== selectedFiles.length) {
      setError(
        "PDF dışındaki dosyalar listeye eklenmedi.",
      );
    }

    const newDocuments: SelectedDocument[] =
      pdfFiles.map((file) => ({
        id: crypto.randomUUID(),
        file,
        documentType: "other",
      }));

    setDocuments((current) => {
      const combined = [...current, ...newDocuments];

      if (combined.length > 10) {
        setError(
          "Tek seferde en fazla 10 PDF yükleyebilirsiniz.",
        );

        return combined.slice(0, 10);
      }

      return combined;
    });

    event.target.value = "";
  }

  function updateDocumentType(
    id: string,
    documentType: DocumentType,
  ) {
    setDocuments((current) =>
      current.map((document) =>
        document.id === id
          ? {
              ...document,
              documentType,
            }
          : document,
      ),
    );
  }

  function removeDocument(id: string) {
    setDocuments((current) =>
      current.filter(
        (document) => document.id !== id,
      ),
    );
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!documents.length) {
      setError("En az bir PDF seçmelisiniz.");
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setIsUploading(true);

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

      const formData = new FormData();

      for (const document of documents) {
        formData.append("files", document.file);
        formData.append(
          "document_types",
          document.documentType,
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
        `${apiUrl}/projects/${projectId}/documents`,
        {
          method: "POST",
          headers: {
            Authorization:
              `Bearer ${session.access_token}`,
          },
          body: formData,
        },
      );

      const responseBody = await response.json();

      if (!response.ok) {
        const detail =
          typeof responseBody.detail === "string"
            ? responseBody.detail
            : "Dosyalar yüklenemedi.";

        throw new Error(detail);
      }

      const result =
        responseBody as MultipleDocumentUploadResponse;

      if (result.successful.length) {
        setSuccessMessage(
          `${result.successful.length} belge başarıyla yüklendi.`,
        );
      }

      if (result.failed.length) {
        const failureMessages = result.failed
          .map(
            (failed) =>
              `${failed.original_filename}: ${failed.message}`,
          )
          .join(" ");

        setError(failureMessages);
      }

      if (result.successful.length) {
        setDocuments([]);
        router.refresh();
      }

    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "Belge yüklenirken hata oluştu.",
      );

    } finally {
      setIsUploading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-5"
    >
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {successMessage && (
        <Alert>
          <AlertDescription>
            {successMessage}
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardContent className="p-6">
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,application/pdf"
            multiple
            className="hidden"
            onChange={handleFileSelection}
          />

          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="group flex min-h-48 w-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-muted-foreground/25 bg-muted/10 p-8 text-center transition-all hover:border-primary/50 hover:bg-primary/5 active:scale-[0.98]"
          >
            <div className="rounded-full bg-primary/10 p-4 mb-4 transition-transform group-hover:scale-110 group-hover:bg-primary/20">
              <Upload className="h-8 w-8 text-primary" />
            </div>

            <span className="text-lg font-semibold text-foreground">
              PDF belgelerini seçin veya sürükleyin
            </span>

            <span className="mt-2 text-sm text-muted-foreground max-w-sm">
              En fazla 10 dosya yükleyebilirsiniz. Dosya başına maksimum boyut 25 MB'dır.
            </span>
          </button>
        </CardContent>
      </Card>

      <div className="space-y-3">
        {documents.length > 0 ? (
          documents.map((document) => (
            <Card key={document.id}>
              <CardContent className="grid items-center gap-4 p-4 md:grid-cols-[1fr_260px_auto]">
                <div className="flex min-w-0 items-center gap-3">
                  <FileText className="h-8 w-8 shrink-0 text-muted-foreground" />

                  <div className="min-w-0">
                    <p className="truncate font-medium">{document.file.name}</p>

                    <p className="text-sm text-muted-foreground">{formatFileSize(document.file.size)}</p>
                  </div>
                </div>

                <select
                  value={document.documentType}
                  onChange={(e) =>
                    updateDocumentType(document.id, e.target.value as DocumentType)
                  }
                  className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                >
                  {DOCUMENT_TYPE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>

                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  disabled={isUploading}
                  onClick={() => removeDocument(document.id)}
                  aria-label="Dosyayı kaldır"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card className="border-dashed border-2 bg-muted/5">
            <CardContent className="flex min-h-[200px] flex-col items-center justify-center text-center p-8">
              <div className="rounded-full bg-muted p-4 mb-4">
                <FileText className="h-8 w-8 text-muted-foreground/50" />
              </div>
              <p className="text-base text-muted-foreground max-w-md">
                PDF seçmek için üstteki alana tıklayın. Dosyaları seçtikten sonra her birine belge türü atayın ve <span className="font-medium text-foreground">Belgeleri kaydet</span> butonuyla yükleyin.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {documents.length > 0 && (
        <div className="flex flex-col justify-between gap-4 rounded-lg border bg-muted/20 p-4 sm:flex-row sm:items-center">
          <div className="text-sm">
            <p className="font-medium">
              {documents.length} belge seçildi
            </p>

            <p className="text-muted-foreground">
              Toplam {formatFileSize(totalSize)}
            </p>
          </div>

          <Button type="submit" size="lg" className="w-full sm:w-auto font-medium shadow-md" disabled={isUploading}>
            {isUploading ? (
              <>
                <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                Belgeler yükleniyor...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-5 w-5" />
                Belgeleri kaydet ve yükle
              </>
            )}
          </Button>
        </div>
      )}
    </form>
  );
}