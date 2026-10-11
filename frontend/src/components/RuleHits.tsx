import React from "react";
import EmptyState from "./EmptyState";

interface RuleHitsProps {
  hits?: string[];
  criticalCount?: number;
}

/**
 * Triggered Rule Checks list with clean typographic severity badges.
 * No icons per row, compact rows, hairline borders.
 */
export default function RuleHits({ hits, criticalCount }: RuleHitsProps) {
  if (!hits || hits.length === 0) {
    return (
      <div className="border border-border rounded-[4px] bg-surface p-4 flex flex-col space-y-3">
        <div className="flex items-center justify-between border-b border-border/60 pb-2">
          <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
            TRIGGERED RULE CHECKS
          </span>
          <span className="text-[10px] font-mono text-text-dim">0 VIOLATIONS</span>
        </div>
        <EmptyState
          label="CLEAN PASS"
          description="No deterministic safety or policy violations triggered."
          minHeight="90px"
        />
      </div>
    );
  }

  // Helper for badge severity categorization based on rule names
  const getSeverity = (ruleId: string) => {
    const id = ruleId.toUpperCase();
    if (["R1", "R4", "R8", "SQL", "CREDENTIAL", "MALICIOUS"].some((k) => id.includes(k))) {
      return { label: "CRITICAL", text: "text-block", bg: "bg-block-bg border-block/40" };
    }
    if (["R2", "R3", "R7", "PATH", "TRAVERSAL", "SUSPICIOUS"].some((k) => id.includes(k))) {
      return { label: "HIGH", text: "text-revise", bg: "bg-revise-bg border-revise/40" };
    }
    return { label: "MEDIUM", text: "text-confirm", bg: "bg-confirm-bg border-confirm/40" };
  };

  return (
    <div className="border border-border rounded-[4px] bg-surface p-4 flex flex-col space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/60 pb-2">
        <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
          TRIGGERED RULE CHECKS
        </span>
        <span className="text-[11px] font-mono text-text-muted tabular-nums">
          {hits.length} hit{hits.length > 1 ? "s" : ""}
          {criticalCount ? ` (${criticalCount} critical)` : ""}
        </span>
      </div>

      {/* Rules list */}
      <div className="flex flex-col divide-y divide-border/40">
        {hits.map((hit, idx) => {
          const sev = getSeverity(hit);
          return (
            <div
              key={`${hit}-${idx}`}
              className="py-2 flex items-center justify-between text-[13px]"
            >
              <span className="font-mono text-[12px] text-text">{hit}</span>
              <span
                className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-[2px] border ${sev.bg} ${sev.text} tracking-[0.05em] font-medium`}
              >
                {sev.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
