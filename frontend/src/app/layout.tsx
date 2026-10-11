import "./globals.css";
import Link from "next/link";
import React from "react";

export const metadata = {
  title: "AI Agent Tool-Call Risk Detector",
  description: "Proxy guardrail inspecting tool calls and evaluating risk in real time.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
        {/* Navigation Bar */}
        <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🛡️</span>
              <span className="font-bold text-lg bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Agent Risk Guardrail
              </span>
            </div>
            <nav className="flex space-x-6 text-sm font-medium">
              <Link
                href="/"
                className="hover:text-cyan-400 transition-colors text-slate-300"
              >
                Live Monitor
              </Link>
              <Link
                href="/metrics"
                className="hover:text-cyan-400 transition-colors text-slate-300"
              >
                Model Metrics
              </Link>
              <Link
                href="/audit"
                className="hover:text-cyan-400 transition-colors text-slate-300"
              >
                Audit Chain
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-6">{children}</main>

        {/* Footer */}
        <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
          AI Agent Risk Detector • FastAPI Proxy • SHA-256 Audit Chain
        </footer>
      </body>
    </html>
  );
}
