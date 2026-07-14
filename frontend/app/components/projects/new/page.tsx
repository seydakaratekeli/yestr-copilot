import { redirect } from "next/navigation";

export default function LegacyNewProjectRoute() {
  redirect("/projects/new");
}