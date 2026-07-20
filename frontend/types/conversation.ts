import type {
  AnswerCitation,
  AnswerStatus,
} from "@/types/answer";

export interface ConversationSummary {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  project_id: string;

  role: "user" | "assistant";
  content: string;

  answer_status:
    | AnswerStatus
    | "failed"
    | null;

  confidence: number | null;

  citations: AnswerCitation[];
  missing_information: string[];
  warnings: string[];

  retrieved_source_count: number;
  error_message: string | null;

  created_at: string;
}

export interface ConversationDetail {
  conversation: ConversationSummary;
  messages: ConversationMessage[];
}

export interface ConversationQuestionResponse {
  conversation_id: string;
  user_message: ConversationMessage;
  assistant_message: ConversationMessage;
}