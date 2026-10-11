"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

/**
 * Understated, editorial header matching terminal/threat-intel aesthetic.
 * Height 56px, hairline bottom border, quiet navigation.
 */
export default function Header() {
  const pathname = usePathname();

  const navItems = [
    { label: "Analyze", href: "/" },
    { label: "Metrics", href: "/metrics" },
    { label: "Audit Log", href: "/audit" },
    { label: "API Docs", href: "http://127.0.0.1:8000/docs", external: true },
  ];

  return (
    <header className="h-14 border-b border-border bg-bg px-6 flex items-center justify-between sticky top-0 z-40 select-none">
      {/* Wordmark */}
      <div className="flex items-center space-x-3">
        <Link
          href="/"
          className="text-[13px] font-semibold tracking-[0.1em] uppercase text-text hover:text-white transition-colors flex items-center space-x-2.5"
        >
          <span className="w-2.5 h-2.5 rounded-[2px] bg-brand inline-block shadow-[0_0_8px_rgba(224,169,72,0.4)]" />
          <span>RISK DETECTOR</span>
        </Link>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded-[3px] border border-allow/30 bg-allow-bg text-allow flex items-center space-x-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-allow animate-pulse" />
          <span>v2 ONLINE</span>
        </span>
      </div>

      {/* Nav */}
      <nav className="flex items-center space-x-7">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          if (item.external) {
            return (
              <a
                key={item.label}
                href={item.href}
                target="_blank"
                rel="noreferrer"
                className="text-[13px] text-text-muted hover:text-text transition-colors py-1 inline-flex items-center"
              >
                {item.label}
              </a>
            );
          }
          return (
            <Link
              key={item.label}
              href={item.href}
              className={`text-[13px] py-1 transition-colors relative ${
                isActive
                  ? "text-text font-medium"
                  : "text-text-muted hover:text-text"
              }`}
            >
              {item.label}
              {isActive && (
                <span className="absolute bottom-[-16px] left-0 right-0 h-[1px] bg-text" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Version badge */}
      <div className="flex items-center space-x-2">
        <span className="text-[11px] font-mono text-text-dim">v2.1.0</span>
      </div>
    </header>
  );
}
