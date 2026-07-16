import {
  FileText,
  ScanText,
} from "lucide-react";

import {
  formatFileSize,
  getDocumentTypeLabel,
} from "@/lib/document-utils";
import { formatDate } from "@/lib/project-utils";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
} from "@/components/ui/card";

import type { ProjectDocument } from "@/types/document";


interface DocumentListProps {
  documents: ProjectDocument[];
}


export function DocumentList({
  documents,
}: DocumentListProps) {
  if (!documents.length) {
    return (
      <Card>
        <CardContent className="flex min-h-48 flex-col items-center justify-center text-center">
          <FileText className="mb-4 h-10 w-10 text-muted-foreground" />

          <h3 className="font-semibold">
            Henüz belge yüklenmedi
          </h3>

          <p className="mt-1 max-w-md text-sm text-muted-foreground">
            Yüklediğiniz mimari ve teknik belgeler
            burada görüntülenecek.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((document) => (
        <Card key={document.id}>
          <CardContent className="flex flex-col justify-between gap-4 p-4 sm:flex-row sm:items-center">
            <div className="flex min-w-0 items-start gap-3">
              <FileText className="mt-1 h-8 w-8 shrink-0 text-muted-foreground" />

              <div className="min-w-0">
                <p className="truncate font-medium">
                  {document.original_filename}
                </p>

                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
                  <span>
                    {getDocumentTypeLabel(
                      document.document_type,
                    )}
                  </span>

                  <span>
                    {formatFileSize(
                      document.file_size_bytes,
                    )}
                  </span>

                  <span>
                    {document.page_count ?? "?"} sayfa
                  </span>

                  <span>
                    {formatDate(document.created_at)}
                  </span>

                  {document.processing_status === "completed" && (
                    <>
                      <span>
                        {document.extracted_word_count} kelime
                      </span>

                      <span>
                        {document.chunk_count} metin parçası
                      </span>
                    </>
                  )}
                </div>

                {document.error_message && (
                  <p className="mt-2 text-sm text-destructive">
                    {document.error_message}
                  </p>
                )}
              </div>
            </div>

            <div className="flex shrink-0 flex-wrap gap-2">
              <Badge
                variant={
                  document.processing_status === "completed"
                    ? "default"
                    : document.processing_status === "failed"
                      ? "destructive"
                      : "secondary"
                }
              >
                {document.processing_status === "queued" &&
                  "Sırada"}

                {document.processing_status === "processing" &&
                  "Metin çıkarılıyor"}

                {document.processing_status === "completed" &&
                  "İşlendi"}

                {document.processing_status === "failed" &&
                  "İşleme başarısız"}

                {document.processing_status === "uploaded" &&
                  "Yüklendi"}
              </Badge>

              {document.extraction_status ===
                "pending" && (
                <Badge variant="outline">
                  <ScanText className="mr-1 h-3 w-3" />
                  OCR gerekli
                </Badge>
              )}

              {document.extraction_status ===
                "completed" && (
                <Badge variant="outline">
                  Metin içeriyor
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}