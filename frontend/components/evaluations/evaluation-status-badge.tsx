import { Badge } from "@/components/ui/badge";

import {
  getEvaluationStatusLabel,
} from "@/lib/evaluation-utils";

import type {
  EvaluationStatus,
} from "@/types/evaluation";

interface EvaluationStatusBadgeProps {
  status: EvaluationStatus;
}

export function EvaluationStatusBadge({
  status,
}: EvaluationStatusBadgeProps) {
  if (status === "completed") {
    return (
      <Badge>
        {getEvaluationStatusLabel(status)}
      </Badge>
    );
  }

  if (status === "failed") {
    return (
      <Badge variant="destructive">
        {getEvaluationStatusLabel(status)}
      </Badge>
    );
  }

  return (
    <Badge variant="secondary">
      {getEvaluationStatusLabel(status)}
    </Badge>
  );
}