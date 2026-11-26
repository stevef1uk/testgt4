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

export default function ChatAssistant({
  initialMessages = [],
  onSend,
}: ChatAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
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
    <section aria-label="AI assistant" className="flex h-full flex-col">
      <ul aria-label="Chat history" className="flex-1 space-y-2 overflow-y-auto p-2">
        {messages.map((m, i) => (
          <li key={i} data-role={m.role}>
            <span className="font-semibold">
              {m.role === "user" ? "You" : "FinAlly"}:
            </span>{" "}
            <span>{m.content}</span>
            {m.trades?.map((t, j) => (
              <span
                key={j}
                className="ml-2 rounded border px-1 text-xs font-semibold"
              >
                {`✓ Trade Fill: ${t.side.toUpperCase()} ${t.quantity} ${t.ticker.toUpperCase()}`}
              </span>
            ))}
          </li>
        ))}
        {pending && (
          <li role="status" aria-live="polite" className="italic">
            Copilot is thinking...
          </li>
        )}
      </ul>
      <form onSubmit={handleSubmit} className="flex gap-2 p-2">
        <input
          type="text"
          aria-label="Message"
          placeholder="Ask FinAlly..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="flex-1 rounded border px-2 py-1"
        />
        <button
          type="submit"
          disabled={pending}
          className="rounded px-3 py-1"
        >
          Send
        </button>
      </form>
    </section>
  );
}