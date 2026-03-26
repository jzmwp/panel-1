import { useState, useCallback, useRef, useEffect } from "react";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  charts?: string[]; // base64 chart images
  queries?: string[];
  isStreaming?: boolean;
}

export interface ChatSessionSummary {
  id: number;
  title: string | null;
  created_at: string;
  message_count: number;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [sessions, setSessions] = useState<ChatSessionSummary[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const fetchSessions = useCallback(async () => {
    setSessionsLoading(true);
    try {
      const res = await fetch("/api/chat/sessions");
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch {
      // ignore
    } finally {
      setSessionsLoading(false);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // Add user message
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      // Create placeholder assistant message
      const assistantId = crypto.randomUUID();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: "assistant",
          content: "",
          charts: [],
          queries: [],
          isStreaming: true,
        },
      ]);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const res = await fetch("/api/chat/message", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: content, session_id: sessionId }),
          signal: controller.signal,
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const reader = res.body?.getReader();
        if (!reader) throw new Error("No response body");

        const decoder = new TextDecoder();
        let buffer = "";
        let currentEvent = "text";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE messages (separated by double newlines)
          while (true) {
            const msgEnd = buffer.indexOf("\n\n");
            if (msgEnd === -1) break;

            const rawMsg = buffer.slice(0, msgEnd);
            buffer = buffer.slice(msgEnd + 2);

            // Parse SSE fields from the message block
            let eventType = "text";
            let data = "";

            for (const line of rawMsg.split("\n")) {
              if (line.startsWith("event:")) {
                eventType = line.slice(6).trim();
              } else if (line.startsWith("data:")) {
                data = line.slice(5).trim();
              }
            }

            if (!data) continue;

            try {
              const parsed = JSON.parse(data);

              if (eventType === "session" && parsed.session_id) {
                setSessionId(parsed.session_id);
                continue;
              }

              if (eventType === "done") {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId
                      ? { ...m, isStreaming: false }
                      : m
                  )
                );
                continue;
              }

              setMessages((prev) =>
                prev.map((m) => {
                  if (m.id !== assistantId) return m;

                  if (eventType === "text" && parsed.content) {
                    return { ...m, content: m.content + parsed.content };
                  }
                  if (eventType === "chart" && parsed.image) {
                    return {
                      ...m,
                      charts: [...(m.charts || []), parsed.image],
                    };
                  }
                  if (eventType === "tool" && parsed.query) {
                    return {
                      ...m,
                      queries: [...(m.queries || []), parsed.query],
                    };
                  }
                  if (eventType === "error") {
                    return {
                      ...m,
                      content:
                        m.content +
                        "\n\n**Error:** " +
                        (parsed.error || "Unknown error"),
                    };
                  }
                  return m;
                })
              );
            } catch {
              // ignore parse errors
            }
          }
        }

        // Mark streaming complete
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, isStreaming: false } : m
          )
        );
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    content: "Sorry, something went wrong. Please try again.",
                    isStreaming: false,
                  }
                : m
            )
          );
        }
      } finally {
        setIsLoading(false);
        abortRef.current = null;
        fetchSessions();
      }
    },
    [isLoading, sessionId, fetchSessions]
  );

  const loadSession = useCallback(async (id: number) => {
    try {
      const res = await fetch(`/api/chat/sessions/${id}`);
      if (!res.ok) return;
      const data = await res.json();
      setSessionId(data.id);
      setMessages(
        (data.messages || []).map((m: any) => ({
          id: String(m.id),
          role: m.role,
          content: m.content,
          queries: m.queries_executed ? JSON.parse(m.queries_executed) : undefined,
          charts: [],
          isStreaming: false,
        }))
      );
    } catch {
      // ignore
    }
  }, []);

  const deleteSession = useCallback(async (id: number) => {
    try {
      await fetch(`/api/chat/sessions/${id}`, { method: "DELETE" });
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (sessionId === id) {
        setMessages([]);
        setSessionId(null);
      }
    } catch {
      // ignore
    }
  }, [sessionId]);

  const newSession = useCallback(() => {
    setMessages([]);
    setSessionId(null);
  }, []);

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  // Fetch sessions on mount
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    messages,
    isLoading,
    sendMessage,
    newSession,
    stopStreaming,
    sessionId,
    sessions,
    sessionsLoading,
    fetchSessions,
    loadSession,
    deleteSession,
  };
}
