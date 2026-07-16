import { notFound, redirect } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { createClient } from "@/lib/supabase/server";
import { DocumentList } from "@/components/documents/document-list";
import { DocumentUploadForm } from "@/components/documents/document-upload-form";
import { Button } from "@/components/ui/button";

import type { ProjectDocument } from "@/types/document";
import { DocumentProcessingRefresh } from "@/components/documents/document-processing-refresh";


interface DocumentsPageProps {
  params: Promise<{
    projectId: string;
  }>;
}


export default async function DocumentsPage({
  params,
}: DocumentsPageProps) {
  const { projectId } = await params;

  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  const [projectResult, documentsResult] =
    await Promise.all([
      supabase
        .from("projects")
        .select("id, name")
        .eq("id", projectId)
        .single(),

      supabase
        .from("project_documents")
        .select("*")
        .eq("project_id", projectId)
        .order("created_at", {
          ascending: false,
        }),
    ]);

  if (
    projectResult.error ||
    !projectResult.data
  ) {
    console.error("Project fetch failed:", projectResult.error);
    notFound();
  }

  if (documentsResult.error) {
    console.error(
      "Documents could not be loaded:",
      documentsResult.error,
    );
  }

  const project = projectResult.data;

  const documents =
    (documentsResult.data as
      | ProjectDocument[]
      | null) ?? [];

  const hasProcessingDocuments = documents.some(
    (document) =>
      document.processing_status === "queued" ||
      document.processing_status === "processing"
  );

  return (
    <main className="min-h-screen bg-muted/30">
      <header className="border-b bg-background">
        <div className="mx-auto max-w-5xl px-6 py-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/projects/${project.id}`}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Projeye dön
            </Link>
          </Button>
        </div>
      </header>

      <div className="mx-auto max-w-5xl space-y-8 px-6 py-8">
        <section>
          <h1 className="text-3xl font-bold tracking-tight">
            Proje belgeleri
          </h1>

          <p className="mt-2 text-muted-foreground">
            {project.name}
          </p>
        </section>

        <section className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold">
              Yeni belge yükle
            </h2>

            <p className="text-sm text-muted-foreground">
              Her PDF için belge türünü seçin.
            </p>
          </div>

          <DocumentUploadForm
            projectId={project.id}
          />
        </section>

        <section className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold">
              Yüklenen belgeler
            </h2>

            <p className="text-sm text-muted-foreground">
              Toplam {documents.length} belge
            </p>
          </div>

          <DocumentList documents={documents} />
        </section>
      </div>

      <DocumentProcessingRefresh enabled={hasProcessingDocuments} />
    </main>
  );
}