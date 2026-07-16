"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

interface DocumentProcessingRefreshProps {
  enabled: boolean;
}

export function DocumentProcessingRefresh({
  enabled,
}: DocumentProcessingRefreshProps) {
  const router = useRouter();

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const intervalId = window.setInterval(
      () => {
        router.refresh();
      },
      3000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [enabled, router]);

  return null;
}