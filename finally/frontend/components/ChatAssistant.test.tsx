// @jest-environment jsdom
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import ChatAssistant from "./ChatAssistant";

function sendMessage(text: string) {
  const input = screen.getByRole("textbox", { name: /message/i });
  fireEvent.change(input, { target: { value: text } });
  fireEvent.click(screen.getByRole("button", { name: /send/i }));
}

describe("ChatAssistant", () => {
  it("renders a message input and a send button", () => {
    render(<ChatAssistant />);
    expect(screen.getByRole("textbox")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });

  it("renders the chat panel without throwing on an empty history", () => {
    const { container } = render(<ChatAssistant />);
    expect(container.firstChild).not.toBeNull();
  });

  it("unwraps a stringified JSON reply to plain text with no braces", async () => {
    const onSend = jest.fn().mockResolvedValue(
      JSON.stringify({ message: "Hello there, trader." })
    );
    render(<ChatAssistant onSend={onSend} />);
    sendMessage("hi");
    const bubble = await screen.findByText("Hello there, trader.");
    expect(bubble.textContent).toBe("Hello there, trader.");
    expect(bubble.textContent).not.toMatch(/[{}]/);
    expect(screen.queryByText(/"message"/)).toBeNull();
  });

  it("shows the thinking indicator while the request is pending", async () => {
    let resolveReply: (value: string) => void = () => {};
    const onSend = jest.fn(
      () => new Promise<string>((resolve) => { resolveReply = resolve; })
    );
    render(<ChatAssistant onSend={onSend} />);
    sendMessage("what is my cash?");
    expect(await screen.findByText(/Copilot is thinking/i)).toBeInTheDocument();
    await act(async () => {
      resolveReply(JSON.stringify({ message: "You have $10,000." }));
    });
    await waitFor(() =>
      expect(screen.queryByText(/Copilot is thinking/i)).toBeNull()
    );
  });

  it("renders a trade fill badge for an executed trade", async () => {
    const onSend = jest.fn().mockResolvedValue(
      JSON.stringify({
        message: "Bought AAPL for you.",
        trades: [{ ticker: "AAPL", side: "buy", quantity: 2 }],
      })
    );
    render(<ChatAssistant onSend={onSend} />);
    sendMessage("buy 2 AAPL");
    expect(
      await screen.findByText("✓ Trade Fill: BUY 2 AAPL")
    ).toBeInTheDocument();
  });
});