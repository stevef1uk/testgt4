"use client";

import { FormEvent, useState } from "react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatAssistantProps {
  endpoint?: string;
}

export default function ChatAssistant({ endpoint = "/api/chat" }: ChatAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);

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
      const data = (await res.json()) as { reply?: string; error?: string };
      const reply = data.reply ?? data.error ?? "No response";
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Request failed. Please try again." },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <section aria-label="Chat assistant">
      <ul>
        {messages.map((m, i) => (
          <li key={i} data-role={m.role}>
            {m.content}
          </li>
        ))}
      </ul>
      <form onSubmit={handleSubmit}>
        <input
          aria-label="Chat message"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={pending}
        />
        <button type="submit" disabled={pending || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}