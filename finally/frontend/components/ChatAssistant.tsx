"use client";

import { useState, type FormEvent } from "react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatAssistantProps {
  initialMessages?: ChatMessage[];
  onSend?: (message: string) => Promise<string> | string;
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
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
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
            {m.content}
          </li>
        ))}
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