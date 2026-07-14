"use client";

import { useFormStatus } from "react-dom";
import { LoaderCircle, Save } from "lucide-react";

import { Button } from "@/components/ui/button";

export function CreateProjectSubmit() {
  const { pending } = useFormStatus();

  return (
    <Button type="submit" disabled={pending}>
      {pending ? (
        <>
          <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
          Proje oluşturuluyor...
        </>
      ) : (
        <>
          <Save className="mr-2 h-4 w-4" />
          Projeyi oluştur
        </>
      )}
    </Button>
  );
}