import { notFound, redirect } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, FileUp } from "lucide-react";

import { createClient } from "@/lib/supabase/server";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

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

  const { data: project, error } = await supabase
    .from("projects")
    .select("id, name")
    .eq("id", projectId)
    .single();

  if (error || !project) {
    notFound();
  }

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

      <div className="mx-auto max-w-5xl space-y-6 px-6 py-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Proje belgeleri
          </h1>

          <p className="mt-2 text-muted-foreground">
            {project.name}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>PDF belgeleri</CardTitle>
          </CardHeader>

          <CardContent className="flex min-h-64 flex-col items-center justify-center text-center">
            <FileUp className="mb-4 h-12 w-12 text-muted-foreground" />

            <h2 className="font-semibold">
              Belge yükleme alanı
            </h2>

            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              Sonraki adımda çoklu PDF yükleme,
              Supabase Storage ve FastAPI PDF kontrol
              servisini bu ekrana bağlayacağız.
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}