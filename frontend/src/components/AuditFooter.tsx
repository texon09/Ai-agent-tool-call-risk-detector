"use client";

import React, { useState } from "react";
import Link from "next/link";

interface AuditFooterProps {
  auditId?: string;
}

/**
 * Clean audit ID footer with copy interaction and link to audit ledger.
 */
export default function AuditFooter({ auditId }: AuditFooterProps) {
  const [copied, setCopied] = useState(false);

  if (!auditId) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(auditId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="pt-2 border-t border-border/70 flex items-center justify-between text-[11px] text-text-dim">
      <div className="flex items-center space-x-2 truncate pr-2">
        <span className="uppercase tracking-[0.08em] font-medium shrink-0 text-text-muted">
          AUDIT ID:
        </span>
        <span className="font-mono text-text-muted truncate select-all px-1.5 py-0.5 rounded-[2px] bg-surface-2 border border-border">
          {auditId}
        </span>
      </div>

      <div className="flex items-center space-x-2 shrink-0">
        <button
          onClick={handleCopy}
          className={`px-2.5 py-1 rounded-[3px] border transition-all focus:outline-none ${
            copied
              ? "border-allow/50 bg-allow-bg text-allow font-medium"
              : "border-border-str bg-surface-2 text-text-muted hover:text-text hover:border-text-dim"
          }`}
        >
          {copied ? "Copied ✓" : "Copy ID"}
        </button>
        <Link
          href="/audit"
          className="px-2.5 py-1 rounded-[3px] border border-border-str bg-surface-2 text-brand hover:text-brand-hover hover:border-brand/40 transition-all font-medium"
        >
          Audit Ledger →
        </Link>
      </div>
    </div>
  );
}
