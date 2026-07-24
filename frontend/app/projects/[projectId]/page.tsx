import { notFound, redirect } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Building2,
  FileUp,
  MapPin,
  Ruler,
} from "lucide-react";

import { createClient } from "@/lib/supabase/server";
import {
  formatArea,
  formatCurrency,
  formatDate,
  getBuildingTypeLabel,
  getCertificateLevelLabel,
  getFacadeDirectionLabel,
  getProjectStatusLabel,
  getProjectTypeLabel,
} from "@/lib/project-utils";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { ProjectEvaluationPanel } from
  "@/components/evaluations/project-evaluation-panel";

import type { Project } from "@/types/project";

import { ProjectChatPanel } from
  "@/components/answers/project-chat-panel";

interface ProjectDetailPageProps {
  params: Promise<{
    projectId: string;
  }>;
}

export default async function ProjectDetailPage({
  params,
}: ProjectDetailPageProps) {
  const { projectId } = await params;

  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  const [projectResult, documentCountResult] =
    await Promise.all([
      supabase
        .from("projects")
        .select("*")
        .eq("id", projectId)
        .single(),

      // TODO: İleride daha doğru kontrol için chunk_count > 0 koşulu eklenebilir
      // (Kısmi OCR sonucu olup chunk içeren belgeleri dahil etmek için)
      supabase
        .from("project_documents")
        .select("*", {
          count: "exact",
          head: true,
        })
        .eq("project_id", projectId)
        .eq("processing_status", "completed"),
    ]);

  const data = projectResult.data;
  const error = projectResult.error;

  if (error || !data) {
    notFound();
  }

  const documentCount =
    documentCountResult.count ?? 0;

  if (error || !data) {
    notFound();
  }

  const project = data as Project;

  return (
    <main className="min-h-screen bg-muted/30">
      <header className="border-b bg-background">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/dashboard">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Dashboard
            </Link>
          </Button>

          <Button asChild>
            <Link href={`/projects/${project.id}/documents`}>
              <FileUp className="mr-2 h-4 w-4" />
              Belge yükle
            </Link>
          </Button>
        </div>
      </header>

      <div className="mx-auto max-w-7xl space-y-8 px-6 py-8">
        <section className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
          <div>
            <div className="mb-3 flex flex-wrap gap-2">
              <Badge>{getProjectStatusLabel(project.status)}</Badge>
              <Badge variant="outline">{getProjectTypeLabel(project.project_type)}</Badge>
            </div>

            <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>

            <p className="mt-2 max-w-3xl text-muted-foreground">
              {project.description || "Bu proje için açıklama girilmemiş."}
            </p>
          </div>

          <p className="text-sm text-muted-foreground">
            Oluşturulma: {formatDate(project.created_at)}
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Konum</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>

            <CardContent>
              <p className="font-semibold">
                {[project.district, project.city].filter(Boolean).join(", ") || "Belirtilmedi"}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Bina türü</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>

            <CardContent>
              <p className="font-semibold">{getBuildingTypeLabel(project.building_type)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">İnşaat alanı</CardTitle>
              <Ruler className="h-4 w-4 text-muted-foreground" />
            </CardHeader>

            <CardContent>
              <p className="font-semibold">{formatArea(project.total_construction_area)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Kat sayısı</CardTitle>
            </CardHeader>

            <CardContent>
              <p className="font-semibold">{project.floor_count ?? "Belirtilmedi"}</p>
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Proje bilgileri</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <DetailRow label="Parsel alanı" value={formatArea(project.parcel_area)} />
              <DetailRow
                label="Ana cephe yönü"
                value={getFacadeDirectionLabel(project.main_facade_direction)}
              />
              <DetailRow
                label="Hedef sertifika seviyesi"
                value={getCertificateLevelLabel(project.target_certificate_level)}
              />
              <DetailRow label="Tahmini bütçe" value={formatCurrency(project.estimated_budget)} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Belge analizi</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Analize başlamak için mimari proje, teknik şartname veya enerji raporu gibi PDF belgelerini yükleyin.
              </p>

              <Button asChild className="w-full sm:w-auto shadow-sm">
                <Link href={`/projects/${project.id}/documents`}>
                  <FileUp className="mr-2 h-4 w-4" />
                  İlk belgeyi yükle
                </Link>
              </Button>
            </CardContent>
          </Card>
        </section>

        <section className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold">
              Otomatik ön değerlendirme
            </h2>

            <p className="text-sm text-muted-foreground">
              Proje belgelerini temsili kriter setine
              göre analiz edin.
            </p>
          </div>

          <ProjectEvaluationPanel
            projectId={project.id}
            documentCount={documentCount}
          />
        </section>

        <section className="space-y-4">
          <div>
            <h2 className="text-xl font-semibold">
              Proje belge asistanı
            </h2>

            <p className="text-sm text-muted-foreground">
              İşlenmiş proje belgeleri üzerinde kaynaklı
              sorular sorun.
            </p>
          </div>
          <ProjectChatPanel
            projectId={project.id}
            documentCount={documentCount}
          />
        </section>
      </div>
    </main>
  );
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b pb-3 last:border-b-0 last:pb-0">
      <span className="text-sm text-muted-foreground">{label}</span>

      <span className="text-right text-sm font-medium">{value}</span>
    </div>
  );
}
