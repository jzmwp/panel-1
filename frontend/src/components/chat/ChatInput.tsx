import { useState, useRef, useEffect } from "react";
import { Send, Square } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  onStop: () => void;
}

const SUGGESTIONS = [
  "Show me all deputy reports from the last week",
  "What are the CH4 trends at TG return this month?",
  "Any hazards currently open?",
  "How many shears did we do on day shift last week?",
  "Show me all gas exceedances in the last 30 days",
  "Chart the convergence rates at the face",
];

export default function ChatInput({ onSend, isLoading, onStop }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput("");
    setShowSuggestions(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  };

  return (
    <div className="border-t border-border bg-surface-raised p-4">
      {showSuggestions && (
        <div className="mb-3 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => {
                onSend(s);
                setShowSuggestions(false);
              }}
              className="text-xs px-3 py-1.5 rounded-full border border-border text-text-secondary hover:border-mine-500 hover:text-mine-400 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder="Ask about your mine data..."
          rows={1}
          className="flex-1 resize-none bg-surface-overlay border border-border rounded-xl px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-mine-600 transition-colors"
        />
        {isLoading ? (
          <button
            onClick={onStop}
            className="shrink-0 w-10 h-10 rounded-xl bg-danger/20 text-danger flex items-center justify-center hover:bg-danger/30 transition-colors"
          >
            <Square className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className={cn(
              "shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-colors",
              input.trim()
                ? "bg-mine-600 text-white hover:bg-mine-700"
                : "bg-surface-overlay text-text-muted"
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
