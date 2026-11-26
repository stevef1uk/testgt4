// @jest-environment jsdom
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import ChatAssistant from "./ChatAssistant";

describe("ChatAssistant", () => {
  beforeEach(() => {
    global.fetch = jest.fn().mockResolvedValue({
      json: async () => ({ reply: "Bought 5 MSFT." }),
    }) as unknown as typeof fetch;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it("disables send until the input has text", () => {
    render(<ChatAssistant />);
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
    fireEvent.change(screen.getByLabelText("Chat message"), {
      target: { value: "buy 5 MSFT" },
    });
    expect(screen.getByRole("button", { name: "Send" })).toBeEnabled();
  });

  it("posts the message and renders the assistant reply", async () => {
    render(<ChatAssistant />);
    const input = screen.getByLabelText("Chat message");
    fireEvent.change(input, { target: { value: "buy 5 MSFT" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/chat",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ message: "buy 5 MSFT" }),
      }),
    );
    expect(await screen.findByText("Bought 5 MSFT.")).toBeInTheDocument();
    expect(screen.getByText("buy 5 MSFT")).toBeInTheDocument();
    expect(input).toHaveValue("");
  });

  it("shows a failure message when the request throws", async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error("network")) as unknown as typeof fetch;
    render(<ChatAssistant />);
    fireEvent.change(screen.getByLabelText("Chat message"), {
      target: { value: "hi" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() =>
      expect(screen.getByText("Request failed. Please try again.")).toBeInTheDocument(),
    );
  });
});