"use client";

import {
  FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Bot,
  FileText,
  LoaderCircle,
  MessageCircleQuestion,
  Plus,
  Send,
  User,
} from "lucide-react";

import {
  createConversation,
  getConversation,
  listConversations,
  sendConversationMessage,
} from "@/services/conversation-api";

import { formatDate } from "@/lib/project-utils";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

import type {
  ConversationMessage,
  ConversationSummary,
} from "@/types/conversation";

interface ProjectChatPanelProps {
  projectId: string;
  documentCount: number;
}

export function ProjectChatPanel({
  projectId,
  documentCount,
}: ProjectChatPanelProps) {
  const [conversations, setConversations] =
    useState<ConversationSummary[]>([]);

  const [
    selectedConversationId,
    setSelectedConversationId,
  ] = useState<string | null>(null);

  const [messages, setMessages] = useState<
    ConversationMessage[]
  >([]);

  const [messageCache, setMessageCache] = useState<
    Record<string, ConversationMessage[]>
  >({});

  const [question, setQuestion] = useState("");

  const [isLoading, setIsLoading] =
    useState(true);

  const [isSending, setIsSending] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const messagesEndRef =
    useRef<HTMLDivElement>(null);

  useEffect(() => {
    void initialize();
  }, [projectId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  async function initialize() {
    setIsLoading(true);
    setError(null);

    try {
      const items =
        await listConversations(projectId);

      setConversations(items);

      if (items.length > 0) {
        await selectConversation(
          items[0].id,
        );
      }
    } catch (initializationError) {
      setError(
        initializationError instanceof Error
          ? initializationError.message
          : "Konuşmalar yüklenemedi.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function selectConversation(
    conversationId: string,
  ) {
    setSelectedConversationId(
      conversationId,
    );

    if (messageCache[conversationId]) {
      setMessages(messageCache[conversationId]);
      setError(null);
      return;
    }

    setMessages([]);
    setError(null);

    try {
      const detail = await getConversation(
        projectId,
        conversationId,
      );

      setMessages(detail.messages);
      setMessageCache((prev) => ({
        ...prev,
        [conversationId]: detail.messages,
      }));
    } catch (conversationError) {
      setError(
        conversationError instanceof Error
          ? conversationError.message
          : "Konuşma yüklenemedi.",
      );
    }
  }

  async function handleNewConversation() {
    setError(null);

    try {
      const conversation =
        await createConversation(projectId);

      setConversations((current) => [
        conversation,
        ...current,
      ]);

      setSelectedConversationId(
        conversation.id,
      );

      setMessages([]);
      setMessageCache((prev) => ({
        ...prev,
        [conversation.id]: [],
      }));
    } catch (creationError) {
      setError(
        creationError instanceof Error
          ? creationError.message
          : "Yeni konuşma oluşturulamadı.",
      );
    }
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const normalizedQuestion =
      question.trim();

    if (normalizedQuestion.length < 3) {
      return;
    }

    setIsSending(true);
    setError(null);

    try {
      let conversationId =
        selectedConversationId;

      if (!conversationId) {
        const newConversation =
          await createConversation(projectId);

        conversationId =
          newConversation.id;

        setSelectedConversationId(
          conversationId,
        );

        setConversations((current) => [
          newConversation,
          ...current,
        ]);
      }

      const temporaryMessage:
        ConversationMessage = {
          id: crypto.randomUUID(),
          conversation_id:
            conversationId,
          project_id: projectId,
          role: "user",
          content: normalizedQuestion,
          answer_status: null,
          confidence: null,
          citations: [],
          missing_information: [],
          warnings: [],
          retrieved_source_count: 0,
          error_message: null,
          created_at:
            new Date().toISOString(),
          resolved_query: null,
          context_message_ids: [],
          is_follow_up: false,
        };

      setMessages((current) => [
        ...current,
        temporaryMessage,
      ]);

      setQuestion("");

      const response =
        await sendConversationMessage(
          projectId,
          conversationId,
          normalizedQuestion,
        );

      setMessages((current) => {
        const newMessages = [
          ...current.filter(
            (message) =>
              message.id !==
              temporaryMessage.id,
          ),
          response.user_message,
          response.assistant_message,
        ];

        setMessageCache((prev) => ({
          ...prev,
          [conversationId as string]: newMessages,
        }));

        return newMessages;
      });

      const updatedConversations =
        await listConversations(projectId);

      setConversations(
        updatedConversations,
      );
    } catch (sendError) {
      setError(
        sendError instanceof Error
          ? sendError.message
          : "Mesaj gönderilemedi.",
      );
    } finally {
      setIsSending(false);
    }
  }

  if (documentCount === 0) {
    return (
      <Alert>
        <FileText className="h-4 w-4" />

        <AlertDescription>
          Belge asistanını kullanmak için
          önce en az bir işlenmiş PDF yükleyin.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className="overflow-hidden">
      <div className="grid min-h-[650px] lg:grid-cols-[260px_1fr]">
        <aside className="border-b bg-muted/20 lg:border-b-0 lg:border-r">
          <div className="border-b p-4">
            <Button
              className="w-full bg-primary/90 hover:bg-primary shadow-sm transition-all"
              onClick={
                handleNewConversation
              }
            >
              <Plus className="mr-2 h-4 w-4" />
              Yeni konuşma oluştur
            </Button>
          </div>

          <div className="max-h-[590px] space-y-1 overflow-y-auto p-2">
            {conversations.map(
              (conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  onClick={() =>
                    selectConversation(
                      conversation.id,
                    )
                  }
                  className={[
                    "w-full rounded-md p-3 text-left transition",
                    selectedConversationId ===
                    conversation.id
                      ? "bg-background shadow-sm"
                      : "hover:bg-background/70",
                  ].join(" ")}
                >
                  <p className="line-clamp-2 text-sm font-medium">
                    {conversation.title}
                  </p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    {formatDate(
                      conversation.updated_at,
                    )}
                  </p>
                </button>
              ),
            )}
          </div>
        </aside>

        <section className="flex min-w-0 flex-col">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2">
              <MessageCircleQuestion className="h-5 w-5" />
              Belgelere Sor
            </CardTitle>
          </CardHeader>

          <CardContent className="flex flex-1 flex-col p-0">
            <div className="flex-1 space-y-6 overflow-y-auto p-5">
              {isLoading && (
                <div className="flex justify-center py-16">
                  <LoaderCircle className="h-6 w-6 animate-spin" />
                </div>
              )}

              {!isLoading &&
                messages.length === 0 && (
                  <div className="flex min-h-72 flex-col items-center justify-center text-center">
                    <Bot className="mb-4 h-10 w-10 text-muted-foreground" />

                    <h3 className="font-semibold">
                      Proje belgeleri hazır
                    </h3>

                    <p className="mt-2 max-w-md text-sm text-muted-foreground">
                      Teknik şartname, enerji
                      raporu ve diğer belgeler
                      hakkında kaynaklı sorular
                      sorabilirsiniz.
                    </p>
                  </div>
                )}

              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                />
              ))}

              {isSending && (
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                  </div>

                  <div className="rounded-lg border bg-muted/30 px-4 py-3 text-sm">
                    <LoaderCircle className="mr-2 inline h-4 w-4 animate-spin" />
                    Belgeler inceleniyor...
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="border-t p-4">
              {error && (
                <Alert
                  variant="destructive"
                  className="mb-4"
                >
                  <AlertDescription>
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <form
                onSubmit={handleSubmit}
                className="flex items-end gap-3"
              >
                <Textarea
                  value={question}
                  onChange={(event) =>
                    setQuestion(
                      event.target.value,
                    )
                  }
                  rows={2}
                  disabled={isSending}
                  placeholder="Proje belgeleri hakkında soru sorun..."
                  className="min-h-20 resize-none"
                />

                <Button
                  type="submit"
                  size="icon"
                  disabled={
                    isSending ||
                    question.trim().length < 3
                  }
                  className="h-11 w-11 shrink-0"
                >
                  {isSending ? (
                    <LoaderCircle className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </form>

              <p className="mt-2 text-xs text-muted-foreground">
                Cevaplar yalnızca yüklenen
                belgelerden üretilir ve resmî
                sertifikasyon kararı değildir.
              </p>
            </div>
          </CardContent>
        </section>
      </div>
    </Card>
  );
}

function ChatMessage({
  message,
}: {
  message: ConversationMessage;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={[
        "flex gap-3",
        isUser
          ? "justify-end"
          : "justify-start",
      ].join(" ")}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <Bot className="h-4 w-4" />
        </div>
      )}

      <div
        className={[
          "max-w-[85%] space-y-4 rounded-xl px-4 py-3",
          isUser
            ? "bg-primary text-primary-foreground"
            : "border bg-background",
        ].join(" ")}
      >
        <p className="whitespace-pre-wrap text-sm leading-6">
          {message.content}
        </p>

        {isUser && message.is_follow_up && (
          <Badge
            variant="secondary"
            className="mt-2"
          >
            Takip sorusu
          </Badge>
        )}

        {isUser &&
          message.is_follow_up &&
          message.resolved_query && (
            <details className="mt-3 text-xs">
              <summary className="cursor-pointer opacity-80">
                Arama sorgusunu göster
              </summary>

              <p className="mt-2 rounded bg-background/20 p-2">
                {message.resolved_query}
              </p>
            </details>
          )}

        {!isUser &&
          message.answer_status && (
            <AssistantMessageDetails
              message={message}
            />
          )}
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}

function AssistantMessageDetails({
  message,
}: {
  message: ConversationMessage;
}) {
  return (
    <div className="space-y-3 border-t pt-3">
      <div className="flex flex-wrap gap-2">
        {message.answer_status ===
          "answered" && (
          <Badge>Yanıtlandı</Badge>
        )}

        {message.answer_status ===
          "insufficient_evidence" && (
          <Badge variant="secondary">
            Yetersiz kanıt
          </Badge>
        )}

        {message.answer_status ===
          "conflicting_evidence" && (
          <Badge variant="destructive">
            Çelişkili kanıt
          </Badge>
        )}

        {message.answer_status ===
          "failed" && (
          <Badge variant="destructive">
            İşlem başarısız
          </Badge>
        )}

        {message.confidence !== null && (
          <Badge variant="outline">
            Güven %
            {Math.round(
              message.confidence * 100,
            )}
          </Badge>
        )}
      </div>

      {message.citations.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold">
            Kaynaklar
          </p>

          {message.citations.map(
            (citation) => (
              <div
                key={citation.source_id}
                className="rounded-md bg-muted/40 p-3 text-xs"
              >
                <p className="font-medium">
                  {citation.original_filename}
                  {" · "}
                  Sayfa {citation.page_number}
                </p>

                <p className="mt-2 text-muted-foreground">
                  {citation.excerpt}
                </p>
              </div>
            ),
          )}
        </div>
      )}

      {message.missing_information.length >
        0 && (
        <div className="text-xs">
          <p className="font-semibold">
            Eksik bilgiler
          </p>

          <ul className="mt-1 space-y-1 text-muted-foreground">
            {message.missing_information.map(
              (item, index) => (
                <li key={`${item}-${index}`}>
                  • {item}
                </li>
              ),
            )}
          </ul>
        </div>
      )}

      {message.warnings.length > 0 && (
        <div className="text-xs">
          <p className="font-semibold">
            Uyarılar
          </p>

          <ul className="mt-1 space-y-1 text-muted-foreground">
            {message.warnings.map(
              (item, index) => (
                <li key={`${item}-${index}`}>
                  • {item}
                </li>
              ),
            )}
          </ul>
        </div>
      )}
    </div>
  );
}