// Polyfill for EventSource in jsdom
if (typeof global.EventSource === 'undefined') {
  global.EventSource = class EventSource {
    constructor(url) { this.url = url; }
    close() {}
    onmessage: ((ev: MessageEvent) => void) | null = null;
    url: string;
  };
}
import "@testing-library/jest-dom";
