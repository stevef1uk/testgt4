import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinAlly Trading Dashboard",
  description: "Track your portfolio and live market prices with FinAlly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}