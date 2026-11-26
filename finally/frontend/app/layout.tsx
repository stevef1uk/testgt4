import type { ReactNode } from "react";
import "./globals.css";
import "./polish.css";

export const metadata = {
  title: "FinAlly",
  description: "FinAlly trading workstation",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}