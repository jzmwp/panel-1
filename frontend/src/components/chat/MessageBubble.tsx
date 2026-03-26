import { HardHat, User, Database, Loader2 } from "lucide-react";
import type { ChatMessage } from "@/hooks/useChat";
import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  message: ChatMessage;
}

function formatContent(content: string): string {
  return content
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, '<code class="bg-surface-overlay px-1.5 py-0.5 rounded text-mine-400 text-xs">$1</code>')
    .replace(/\n/g, "<br />");
}

function renderTable(content: string): string {
  const lines = content.split("\n");
  let inTable = false;
  let result: string[] = [];
  let tableRows: string[] = [];

  for (const line of lines) {
    if (line.trim().startsWith("|") && line.trim().endsWith("|")) {
      if (!inTable) {
        inTable = true;
        tableRows = [];
      }
      if (/^\|[\s-:|]+\|$/.test(line.trim())) continue;
      tableRows.push(line.trim());
    } else {
      if (inTable) {
        result.push(buildTable(tableRows));
        inTable = false;
        tableRows = [];
      }
      result.push(line);
    }
  }
  if (inTable) result.push(buildTable(tableRows));

  return result.join("\n");
}

function buildTable(rows: string[]): string {
  if (rows.length === 0) return "";
  const parsed = rows.map((r) =>
    r
      .split("|")
      .filter((c) => c !== "")
      .map((c) => c.trim())
  );

  let html =
    '<div class="overflow-x-auto my-3"><table class="w-full text-sm border-collapse">';
  html +=
    "<thead><tr>" +
    parsed[0]
      .map(
        (h) =>
          `<th class="text-left px-3 py-2 border-b border-border text-text-secondary font-medium">${h}</th>`
      )
      .join("") +
    "</tr></thead>";
  html += "<tbody>";
  for (let i = 1; i < parsed.length; i++) {
    html +=
      "<tr>" +
      parsed[i]
        .map(
          (c) =>
            `<td class="px-3 py-2 border-b border-border/50">${c}</td>`
        )
        .join("") +
      "</tr>";
  }
  html += "</tbody></table></div>";
  return html;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  let processed = message.content;
  if (!isUser) {
    processed = renderTable(processed);
    processed = formatContent(processed);
  }

  // Add blinking cursor while streaming
  const showCursor = !isUser && message.isStreaming && message.content;

  return (
    <div
      className={cn("flex gap-3 py-4", isUser ? "flex-row-reverse" : "flex-row")}
    >
      <div
        className={cn(
          "shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5",
          isUser ? "bg-mine-600/20" : "bg-surface-overlay"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-mine-400" />
        ) : (
          <HardHat className="w-4 h-4 text-mine-500" />
        )}
      </div>
      <div className={cn("max-w-[80%] space-y-2", isUser ? "text-right" : "")}>
        {/* SQL queries executed */}
        {!isUser && message.queries && message.queries.length > 0 && (
          <div className="space-y-1">
            {message.queries.map((q, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs text-text-muted"
              >
                <Database className="w-3 h-3 shrink-0" />
                <code className="bg-surface-overlay px-2 py-1 rounded text-text-secondary truncate max-w-md">
                  {q}
                </code>
              </div>
            ))}
          </div>
        )}

        {/* Message content */}
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed inline-block text-left",
            isUser
              ? "bg-mine-600 text-white"
              : "bg-surface-overlay text-text-primary"
          )}
        >
          {message.isStreaming && !message.content ? (
            <div className="flex items-center gap-2 text-text-secondary">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          ) : (
            <div className="inline">
              <span dangerouslySetInnerHTML={{ __html: processed }} />
              {showCursor && (
                <span className="inline-block w-0.5 h-4 bg-mine-400 ml-0.5 align-middle animate-pulse" />
              )}
            </div>
          )}
        </div>

        {/* Charts */}
        {message.charts &&
          message.charts.map((chart, i) => (
            <div
              key={i}
              className="rounded-xl overflow-hidden border border-border mt-2"
            >
              <img
                src={`data:image/png;base64,${chart}`}
                alt="Chart"
                className="w-full max-w-lg"
              />
            </div>
          ))}
      </div>
    </div>
  );
}
