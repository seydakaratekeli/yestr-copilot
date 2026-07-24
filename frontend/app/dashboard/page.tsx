import Link from "next/link";
import { redirect } from "next/navigation";
import {
  ArrowRight,
  Building2,
  FilePlus2,
  FileText,
  MapPin,
} from "lucide-react";

import { createClient } from "@/lib/supabase/server";
import {
  formatDate,
  getBuildingTypeLabel,
  getProjectStatusLabel,
  getProjectTypeLabel,
} from "@/lib/project-utils";
import { LogoutButton } from "@/components/auth/logout-button";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import type { Project } from "@/types/project";

export default async function DashboardPage() {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  const { data: projects } = await supabase
    .from("projects")
    .select("*")
    .order("created_at", { ascending: false });

  const projectList = (projects ?? []) as Project[];

  return (
    <main className="min-h-screen bg-muted/30">
      <header className="border-b bg-background">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-sm text-muted-foreground">Hoş geldiniz</p>
            <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          </div>

          <div className="flex items-center gap-4">
            <Button asChild variant="outline">
              <Link href="/profile">Profil Ayarları</Link>
            </Button>
            <LogoutButton />
            <Button asChild>
              <Link href="/projects/new">
                <FilePlus2 className="mr-2 h-4 w-4" />
                Yeni proje oluştur
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl space-y-8 px-6 py-8">
        <section className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Toplam proje</CardTitle>
              <CardDescription>Hesabınızdaki proje sayısı</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{projectList.length}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Giriş durumu</CardTitle>
              <CardDescription>Aktif oturum bilgisi</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="font-medium">{user.email ?? "Bilinmiyor"}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Son adım</CardTitle>
              <CardDescription>Belge yükleme akışı</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="font-medium">Projeyi açın, sonra belgeleri yükleyin.</p>
            </CardContent>
          </Card>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold tracking-tight">Projeler</h2>
              <p className="text-sm text-muted-foreground">Son oluşturulan projeler</p>
            </div>
          </div>

          {projectList.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
                <div className="rounded-full bg-muted p-3">
                  <FileText className="h-6 w-6 text-muted-foreground" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-lg font-semibold">Henüz proje yok</h3>
                  <p className="text-sm text-muted-foreground">
                    İlk projenizi oluşturup analiz akışını başlatın.
                  </p>
                </div>
                <Button asChild>
                  <Link href="/projects/new">İlk projeyi oluştur</Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 lg:grid-cols-2">
              {projectList.map((project) => (
                <Card key={project.id}>
                  <CardHeader>
                    <div className="mb-2 flex flex-wrap gap-2">
                      <Badge>{getProjectStatusLabel(project.status)}</Badge>
                      <Badge variant="outline">{getProjectTypeLabel(project.project_type)}</Badge>
                    </div>
                    <CardTitle className="text-lg">{project.name}</CardTitle>
                    <CardDescription>{project.description || "Açıklama girilmemiş."}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-3 text-sm text-muted-foreground sm:grid-cols-2">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        <span>{[project.district, project.city].filter(Boolean).join(", ") || "Belirtilmedi"}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4" />
                        <span>{getBuildingTypeLabel(project.building_type)}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Oluşturulma: {formatDate(project.created_at)}</span>
                      <Button asChild size="sm" variant="ghost">
                        <Link href={`/projects/${project.id}`}>
                          Aç
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
