import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Polecat",
  description: "A focused project workspace.",
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