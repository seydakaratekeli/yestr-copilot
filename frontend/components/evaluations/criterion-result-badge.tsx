import { Badge } from "@/components/ui/badge";

import {
  getCriterionResultLabel,
} from "@/lib/evaluation-utils";

import type {
  CriterionResultStatus,
} from "@/types/evaluation";

interface CriterionResultBadgeProps {
  status: CriterionResultStatus;
}

export function CriterionResultBadge({
  status,
}: CriterionResultBadgeProps) {
  if (status === "satisfied") {
    return (
      <Badge>
        {getCriterionResultLabel(status)}
      </Badge>
    );
  }

  if (
    status === "not_satisfied" ||
    status === "failed"
  ) {
    return (
      <Badge variant="destructive">
        {getCriterionResultLabel(status)}
      </Badge>
    );
  }

  if (
    status === "manual_review" ||
    status === "uncertain"
  ) {
    return (
      <Badge variant="secondary">
        {getCriterionResultLabel(status)}
      </Badge>
    );
  }

  return (
    <Badge variant="outline">
      {getCriterionResultLabel(status)}
    </Badge>
  );
}