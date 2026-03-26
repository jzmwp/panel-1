import { useRef, useEffect, useState } from "react";
import { Plus, HardHat, History, X } from "lucide-react";
import { useChat } from "@/hooks/useChat";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";
import ChatHistory from "./ChatHistory";
import { cn } from "@/lib/utils";

export default function ChatPanel() {
  const {
    messages,
    isLoading,
    sendMessage,
    newSession,
    stopStreaming,
    sessionId,
    sessions,
    sessionsLoading,
    loadSession,
    deleteSession,
  } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSelectSession = (id: number) => {
    loadSession(id);
    setShowHistory(false);
  };

  return (
    <div className="flex h-full">
      {/* History sidebar */}
      <div
        className={cn(
          "border-r border-border bg-surface-raised flex flex-col shrink-0 transition-all duration-200 overflow-hidden",
          showHistory ? "w-72" : "w-0 border-r-0"
        )}
      >
        <div className="h-14 border-b border-border flex items-center justify-between px-4 shrink-0">
          <span className="text-sm font-semibold whitespace-nowrap">Chat History</span>
          <button
            onClick={() => setShowHistory(false)}
            className="p-1 rounded hover:bg-surface-overlay text-text-secondary hover:text-text-primary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ChatHistory
            sessions={sessions}
            loading={sessionsLoading}
            activeSessionId={sessionId}
            onSelect={handleSelectSession}
            onDelete={deleteSession}
          />
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="h-14 border-b border-border flex items-center justify-between px-4 bg-surface-raised shrink-0">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className={cn(
                "p-1.5 rounded-lg transition-colors",
                showHistory
                  ? "bg-mine-600/15 text-mine-400"
                  : "text-text-secondary hover:bg-surface-overlay hover:text-text-primary"
              )}
              title="Chat history"
            >
              <History className="w-4 h-4" />
            </button>
            <h1 className="text-sm font-semibold">Mine Data Chat</h1>
            <span className="text-xs text-text-muted bg-surface-overlay px-2 py-0.5 rounded-full">
              AI-Powered
            </span>
          </div>
          <button
            onClick={newSession}
            className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary px-3 py-1.5 rounded-lg hover:bg-surface-overlay transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            New Chat
          </button>
        </header>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-2xl bg-mine-600/10 flex items-center justify-center mb-4">
                <HardHat className="w-8 h-8 text-mine-500" />
              </div>
              <h2 className="text-lg font-semibold mb-2">
                Chat with your mine data
              </h2>
              <p className="text-sm text-text-secondary max-w-md">
                Ask questions about deputy reports, gas readings, production,
                hazards, strata conditions — anything in the database. The AI will
                query the data and give you answers with charts.
              </p>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto py-4">
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
            </div>
          )}
        </div>

        {/* Input */}
        <ChatInput
          onSend={sendMessage}
          isLoading={isLoading}
          onStop={stopStreaming}
        />
      </div>
    </div>
  );
}
