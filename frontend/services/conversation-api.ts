import { createClient } from "@/lib/supabase/client";

import type {
  ConversationDetail,
  ConversationQuestionResponse,
  ConversationSummary,
} from "@/types/conversation";

async function getAccessToken(): Promise<string> {
  const supabase = createClient();

  const {
    data: { session },
    error,
  } = await supabase.auth.getSession();

  if (error || !session?.access_token) {
    throw new Error(
      "Oturum bilgisi alınamadı."
    );
  }

  return session.access_token;
}

function getApiUrl(): string {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    throw new Error(
      "Backend API adresi tanımlanmamış."
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

export async function listConversations(
  projectId: string,
): Promise<ConversationSummary[]> {
  const token = await getAccessToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/conversations`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return parseResponse(response);
}

export async function createConversation(
  projectId: string,
): Promise<ConversationSummary> {
  const token = await getAccessToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/conversations`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: null,
      }),
    },
  );

  return parseResponse(response);
}

export async function getConversation(
  projectId: string,
  conversationId: string,
): Promise<ConversationDetail> {
  const token = await getAccessToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/conversations/${conversationId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return parseResponse(response);
}

export async function sendConversationMessage(
  projectId: string,
  conversationId: string,
  question: string,
): Promise<ConversationQuestionResponse> {
  const token = await getAccessToken();

  const response = await fetch(
    `${getApiUrl()}/projects/${projectId}/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        question,
        search_limit: 6,
        minimum_similarity: 0.3,
      }),
    },
  );

  return parseResponse(response);
}