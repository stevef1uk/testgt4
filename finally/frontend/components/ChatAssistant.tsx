"use client";

import { FormEvent, useState, useRef, useEffect } from "react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  trade?: {
    side: string;
    ticker: string;
    quantity: number;
  };
}

export interface ChatAssistantProps {
  endpoint?: string;
  onTrade?: () => void;
}

export default function ChatAssistant({
  endpoint = "/api/chat",
  onTrade,
}: ChatAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, pending]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = input.trim();
    if (!text || pending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setPending(true);

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = (await res.json()) as {
        reply?: string;
        response?: string;
        message?: string;
        error?: string;
        detail?: string;
        trade?: { side: string; ticker: string; quantity: number };
      };
      let reply =
        data.reply ??
        data.response ??
        data.message ??
        data.error ??
        data.detail ??
        (res.ok ? "No response received" : `Error (${res.status})`);

      if (
        typeof reply === "string" &&
        reply.trim().startsWith("{") &&
        reply.trim().endsWith("}")
      ) {
        try {
          const parsed = JSON.parse(reply.trim());
          if (parsed.reply) reply = parsed.reply;
          else if (parsed.response) reply = parsed.response;
          else if (parsed.message) reply = parsed.message;
          else if (parsed.error) reply = parsed.error;
        } catch {
          // Keep raw reply if parsing fails
        }
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: reply, trade: data.trade },
      ]);
      if (data.trade) {
        onTrade?.();
      }
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : "Request failed";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errMsg}. Please try again.` },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <section
      aria-label="Chat assistant"
      className="flex flex-col h-[400px] text-sm"
    >
      {/* Scrollable conversation history */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-3 mb-3 custom-scrollbar">
        <ul className="space-y-3">
          {messages.map((m, i) => {
            const isUser = m.role === "user";
            return (
              <li
                key={i}
                data-role={m.role}
                className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
              >
                <span className="text-[10px] text-gray-400 mb-1 px-1">
                  {isUser ? "You" : "FinAlly AI"}
                </span>
                <div
                  className={`px-3 py-2 rounded-lg max-w-[90%] leading-relaxed ${
                    isUser
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-[#1f242c] text-gray-200 border border-gray-700/80 rounded-bl-none shadow-sm"
                  }`}
                >
                  <p>{m.content}</p>
                  {m.trade && (
                    <div className="mt-2 pt-1 border-t border-gray-700 text-xs text-emerald-400 font-mono">
                      ✓ Trade Fill: {m.trade.side.toUpperCase()}{" "}
                      {m.trade.quantity} {m.trade.ticker}
                    </div>
                  )}
                </div>
              </li>
            );
          })}
          {pending && (
            <li data-role="assistant" className="flex flex-col items-start">
              <span className="text-[10px] text-gray-400 mb-1 px-1">FinAlly AI</span>
              <div className="px-3 py-2 rounded-lg bg-[#1f242c] border border-gray-700 text-gray-400 italic text-xs flex items-center gap-2">
                <span className="inline-block h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
                Copilot is thinking...
              </div>
            </li>
          )}
        </ul>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2 pt-2 border-t border-gray-800">
        <input
          aria-label="Chat message"
          placeholder="Ask AI (e.g. 'Buy 5 AAPL')..."
          className="flex-1 bg-gray-950 border border-gray-700 rounded px-3 py-1.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={pending}
        />
        <button
          type="submit"
          disabled={pending || !input.trim()}
          className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:opacity-40 text-white font-medium rounded text-sm transition-colors shrink-0"
        >
          Send
        </button>
      </form>
    </section>
  );
}
