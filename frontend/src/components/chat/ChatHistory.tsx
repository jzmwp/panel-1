import { MessageSquare, Trash2, Loader2 } from "lucide-react";
import type { ChatSessionSummary } from "@/hooks/useChat";
import { cn } from "@/lib/utils";

interface ChatHistoryProps {
  sessions: ChatSessionSummary[];
  loading: boolean;
  activeSessionId: number | null;
  onSelect: (id: number) => void;
  onDelete: (id: number) => void;
}

function groupByDate(sessions: ChatSessionSummary[]) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);
  const weekAgo = new Date(today.getTime() - 7 * 86400000);

  const groups: { label: string; items: ChatSessionSummary[] }[] = [
    { label: "Today", items: [] },
    { label: "Yesterday", items: [] },
    { label: "This Week", items: [] },
    { label: "Older", items: [] },
  ];

  for (const s of sessions) {
    const d = new Date(s.created_at);
    if (d >= today) groups[0].items.push(s);
    else if (d >= yesterday) groups[1].items.push(s);
    else if (d >= weekAgo) groups[2].items.push(s);
    else groups[3].items.push(s);
  }

  return groups.filter((g) => g.items.length > 0);
}

export default function ChatHistory({
  sessions,
  loading,
  activeSessionId,
  onSelect,
  onDelete,
}: ChatHistoryProps) {
  if (loading && sessions.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-text-muted">
        <Loader2 className="w-5 h-5 animate-spin" />
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="px-4 py-12 text-center text-sm text-text-muted">
        No past conversations yet.
      </div>
    );
  }

  const groups = groupByDate(sessions);

  return (
    <div className="flex flex-col gap-1 py-2">
      {groups.map((group) => (
        <div key={group.label}>
          <div className="px-4 py-2 text-xs font-medium text-text-muted uppercase tracking-wider">
            {group.label}
          </div>
          {group.items.map((s) => (
            <button
              key={s.id}
              onClick={() => onSelect(s.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors group",
                s.id === activeSessionId
                  ? "bg-mine-600/15 text-mine-400"
                  : "text-text-secondary hover:bg-surface-overlay hover:text-text-primary"
              )}
            >
              <MessageSquare className="w-4 h-4 shrink-0 opacity-50" />
              <div className="flex-1 min-w-0">
                <div className="truncate">
                  {s.title || "Untitled chat"}
                </div>
                <div className="text-xs text-text-muted mt-0.5">
                  {s.message_count} message{s.message_count !== 1 ? "s" : ""}
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(s.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-danger/20 hover:text-danger transition-all shrink-0"
                title="Delete conversation"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}
