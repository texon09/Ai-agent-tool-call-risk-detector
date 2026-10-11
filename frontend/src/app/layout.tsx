import "./globals.css";
import { Inter, JetBrains_Mono } from "next/font/google";
import React from "react";
import Header from "../components/Header";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata = {
  title: "Risk Detector · AI Agent Tool-Call Security Guardrail",
  description:
    "Real-time proxy guardrail inspecting AI agent tool calls with calibrated ensemble scoring and SHA-256 audit trails.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-bg text-text antialiased flex flex-col font-sans selection:bg-border-str selection:text-text">
        <Header />
        <main className="flex-1 w-full max-w-[1560px] mx-auto px-4 sm:px-6 py-4 flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
