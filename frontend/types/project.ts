export type ProjectType = "new_building" | "existing_building";

export type ProjectStatus =
  | "draft"
  | "documents_uploaded"
  | "processing"
  | "analyzed"
  | "archived";

export interface Project {
  id: string;
  organization_id: string | null;
  created_by: string;

  name: string;
  description: string | null;

  city: string | null;
  district: string | null;

  building_type: string | null;
  project_type: ProjectType;

  total_construction_area: number | null;
  parcel_area: number | null;
  floor_count: number | null;
  main_facade_direction: string | null;

  target_certificate_level: string | null;
  estimated_budget: number | null;

  status: ProjectStatus;

  created_at: string;
  updated_at: string;
}