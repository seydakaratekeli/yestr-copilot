"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { createClient } from "@/lib/supabase/server";
import { projectSchema } from "@/lib/validations/project";

export interface ProjectActionState {
  success: boolean;
  message: string | null;
  fieldErrors?: Record<string, string[] | undefined>;
}

export async function createProject(
  _previousState: ProjectActionState,
  formData: FormData,
): Promise<ProjectActionState> {
  const parsed = projectSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description") || undefined,
    city: formData.get("city") || undefined,
    district: formData.get("district") || undefined,
    buildingType: formData.get("buildingType") || undefined,
    projectType: formData.get("projectType"),
    totalConstructionArea:
      formData.get("totalConstructionArea") || undefined,
    parcelArea: formData.get("parcelArea") || undefined,
    floorCount: formData.get("floorCount") || undefined,
    mainFacadeDirection:
      formData.get("mainFacadeDirection") || undefined,
    targetCertificateLevel:
      formData.get("targetCertificateLevel") || undefined,
    estimatedBudget:
      formData.get("estimatedBudget") || undefined,
  });

  if (!parsed.success) {
    return {
      success: false,
      message: "Lütfen formdaki hataları düzeltin.",
      fieldErrors: parsed.error.flatten().fieldErrors,
    };
  }

  const supabase = await createClient();

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser();

  if (userError || !user) {
    return {
      success: false,
      message: "Oturumunuz bulunamadı. Lütfen tekrar giriş yapın.",
    };
  }

  const values = parsed.data;

  const { data: project, error: insertError } = await supabase
    .from("projects")
    .insert({
      organization_id: null,
      created_by: user.id,

      name: values.name,
      description: values.description || null,

      city: values.city || null,
      district: values.district || null,

      building_type: values.buildingType || null,
      project_type: values.projectType,

      total_construction_area:
        values.totalConstructionArea ?? null,

      parcel_area: values.parcelArea ?? null,
      floor_count: values.floorCount ?? null,

      main_facade_direction:
        values.mainFacadeDirection || null,

      target_certificate_level:
        values.targetCertificateLevel || null,

      estimated_budget:
        values.estimatedBudget ?? null,

      status: "draft",
    })
    .select("id")
    .single();

  if (insertError || !project) {
    console.error("Project insert error:", insertError);

    return {
      success: false,
      message:
        insertError?.message ??
        "Proje oluşturulurken beklenmeyen bir hata oluştu.",
    };
  }

  revalidatePath("/dashboard");
  revalidatePath("/projects");

  redirect(`/projects/${project.id}`);
}