"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  LoaderCircle,
  RefreshCw,
} from "lucide-react";

import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";


interface ReprocessDocumentButtonProps {
  documentId: string;
}


export function ReprocessDocumentButton({
  documentId,
}: ReprocessDocumentButtonProps) {
  const router = useRouter();

  const [isLoading, setIsLoading] =
    useState(false);

  async function handleReprocess() {
    setIsLoading(true);

    try {
      const supabase = createClient();

      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session?.access_token) {
        throw new Error(
          "Oturum bilgisi alınamadı."
        );
      }

      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL;

      const response = await fetch(
        `${apiUrl}/documents/${documentId}/process`,
        {
          method: "POST",
          headers: {
            Authorization:
              `Bearer ${session.access_token}`,
          },
        },
      );

      const body = await response.json();

      if (!response.ok) {
        throw new Error(
          body.detail ??
          "Belge yeniden işlenemedi."
        );
      }

      router.refresh();

    } catch (error) {
      console.error(error);

    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      disabled={isLoading}
      onClick={handleReprocess}
    >
      {isLoading ? (
        <>
          <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
          Sıraya alınıyor
        </>
      ) : (
        <>
          <RefreshCw className="mr-2 h-4 w-4" />
          Yeniden işle
        </>
      )}
    </Button>
  );
}