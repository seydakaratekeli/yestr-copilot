import { createClient } from "@/lib/supabase/client";

import type {
  CriterionSet,
  EvaluationDetail,
  EvaluationSummary,
} from "@/types/evaluation";

async function getToken(): Promise<string> {
  const supabase = createClient();

  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error(
      "Oturum bilgisi alınamadı.",
    );
  }

  return session.access_token;
}

function getApiUrl(): string {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    throw new Error(
      "Backend API adresi tanımlanmamış.",
    );
  }

  return apiUrl;
}

async function parseResponse<T>(
  response: Response,
): Promise<T> {
  const body = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : "İstek gerçekleştirilemedi.",
    );
  }

  return body as T;
}

export async function listCriterionSets():
Promise<CriterionSet[]> {
  const token = await getToken();

  const response = await fetch(
    `${getApiUrl()}/criterion-sets`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return parseResponse(response);
}

export async function startEvaluation(
  projectId: string,
  criterionSetId: string,
): Promise<{
  evaluation_id: string;
  status: string;
}> {
  const token = await getToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/evaluations`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        criterion_set_id: criterionSetId,
      }),
    },
  );

  return parseResponse(response);
}

export async function listEvaluations(
  projectId: string,
): Promise<EvaluationSummary[]> {
  const token = await getToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/evaluations`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return parseResponse(response);
}

export async function getEvaluation(
  projectId: string,
  evaluationId: string,
): Promise<EvaluationDetail> {
  const token = await getToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/evaluations/${evaluationId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return parseResponse(response);
}

export async function rerunEvaluation(
  projectId: string,
  evaluationId: string,
): Promise<{
  evaluation_id: string;
  status: string;
}> {
  const token = await getToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/evaluations/${evaluationId}/rerun`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return parseResponse(response);
}