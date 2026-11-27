"use client";

import { useState, type FormEvent } from "react";

export interface TradeFill {
  ticker: string;
  side: string;
  quantity: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  trades?: TradeFill[];
}

export interface ChatAssistantProps {
  initialMessages?: ChatMessage[];
  onSend?: (message: string) => Promise<string> | string;
}

interface ParsedReply {
  text: string;
  trades: TradeFill[];
}

function isTradeFill(value: unknown): value is TradeFill {
  if (!value || typeof value !== "object") return false;
  const t = value as Record<string, unknown>;
  return (
    typeof t.ticker === "string" &&
    typeof t.side === "string" &&
    typeof t.quantity === "number"
  );
}

// Unwraps a stringified JSON reply into plain text plus executed trades.
// Anything that is not a JSON object is shown verbatim as text.
function parseReply(raw: string): ParsedReply {
  try {
    const data: unknown = JSON.parse(raw);
    if (data && typeof data === "object" && !Array.isArray(data)) {
      const obj = data as Record<string, unknown>;
      const candidate = [obj.message, obj.reply, obj.response, obj.content].find(
        (v) => typeof v === "string" && v.trim() !== ""
      );
      const trades = Array.isArray(obj.trades)
        ? obj.trades.filter(isTradeFill)
        : [];
      return {
        text: typeof candidate === "string" ? candidate : "",
        trades,
      };
    }
  } catch {
    // Not JSON: fall through and render the raw text.
  }
  return { text: raw, trades: [] };
}

const DEFAULT_GREETING: ChatMessage = {
  role: "assistant",
  content: "Hello! I am FinAlly, your AI trading copilot. Ask me about your portfolio, market trends, or to execute a trade.",
};

export default function ChatAssistant({
  initialMessages = [],
  onSend,
}: ChatAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(
    initialMessages.length > 0 ? initialMessages : [DEFAULT_GREETING]
  );
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || pending) return;
    setDraft("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    if (!onSend) return;
    setPending(true);
    try {
      const reply = await onSend(text);
      const parsed = parseReply(reply);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: parsed.text, trades: parsed.trades },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <section aria-label="AI assistant" className="panel p-4 flex flex-col h-[420px] text-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <h3 className="font-semibold text-slate-200">FinAlly Copilot</h3>
        </div>
        <span className="text-xs bg-slate-800 text-blue-400 border border-slate-700 px-2 py-0.5 rounded">
          AI Assistant
        </span>
      </div>

      <ul aria-label="Chat history" className="flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.map((m, i) => (
          <li
            key={i}
            data-role={m.role}
            className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}
          >
            <span className="text-[11px] text-slate-500 mb-0.5 px-1">
              {m.role === "user" ? "You" : "FinAlly"}
            </span>
            <div
              className={`rounded-lg px-3 py-2 max-w-[90%] text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-blue-600/30 border border-blue-500/50 text-blue-100"
                  : "bg-slate-800/90 border border-slate-700/80 text-slate-200"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.trades && m.trades.length > 0 && (
                <div className="mt-2 space-y-1">
                  {m.trades.map((t, j) => (
                    <div
                      key={j}
                      className="inline-block rounded bg-emerald-950/80 border border-emerald-700 px-2 py-0.5 text-xs font-mono text-emerald-300"
                    >
                      {`✓ Trade Fill: ${t.side.toUpperCase()} ${t.quantity} ${t.ticker.toUpperCase()}`}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </li>
        ))}
        {pending && (
          <li role="status" aria-live="polite" className="flex items-center gap-2 text-slate-400 text-xs italic p-1">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-slate-400 animate-ping" />
            Copilot is thinking...
          </li>
        )}
      </ul>

      <form onSubmit={handleSubmit} className="flex gap-2 pt-3 border-t border-slate-800 mt-2">
        <input
          type="text"
          aria-label="Message"
          placeholder="Ask FinAlly..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="flex-1 rounded bg-slate-900 border border-slate-700 px-3 py-1.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={pending}
          className="rounded px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
    </section>
  );
}
