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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
            className="flex min-h-48 w-full flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 text-center transition hover:border-primary hover:bg-muted/40"
          >
            <Upload className="mb-4 h-10 w-10 text-muted-foreground" />

            <span className="font-semibold">
              PDF belgelerini seçin
            </span>

            <span className="mt-2 text-sm text-muted-foreground">
              En fazla 10 dosya, dosya başına 25 MB
            </span>
          </button>
        </CardContent>
      </Card>

      <div className="flex flex-col justify-between gap-4 rounded-lg border bg-muted/20 p-4 sm:flex-row sm:items-center">
        <div className="text-sm">
          <p className="font-medium">
            {documents.length > 0 ? `${documents.length} belge seçildi` : "Henüz belge seçilmedi"}
          </p>

          <p className="text-muted-foreground">
            {documents.length > 0 ? `Toplam ${formatFileSize(totalSize)}` : "PDF seçmek için üstteki alanı kullanın"}
          </p>
        </div>

        <Button type="submit" disabled={isUploading || documents.length === 0}>
          {isUploading ? (
            <>
              <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
              Belgeler yükleniyor...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Belgeleri kaydet ve yükle
            </>
          )}
        </Button>
      </div>

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

                <Select
                  value={document.documentType}
                  onValueChange={(value) =>
                    updateDocumentType(document.id, value as DocumentType)
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>

                  <SelectContent>
                    {DOCUMENT_TYPE_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

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
          <Card>
            <CardContent className="flex min-h-32 items-center justify-center text-center">
              <p className="text-sm text-muted-foreground">
                Yükleme butonu, PDF seçince aktif olur. Seçilen dosyalar önce Supabase Storage'a gider, ardından <span className="font-medium text-foreground">project_documents</span> tablosuna kaydedilir.
              </p>
            </CardContent>
          </Card>
        )}

      </div>
    </form>
  );
}