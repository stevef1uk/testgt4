// @jest-environment jsdom
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import ChatAssistant from "./ChatAssistant";

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
});