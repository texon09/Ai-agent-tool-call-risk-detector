import React from "react";
import EmptyState from "./EmptyState";

interface DecisionBannerProps {
  action?: "ALLOW" | "CONFIRM" | "REVISE" | "BLOCK";
  riskScore?: number;
  criticalViolations?: number;
  rationale?: string;
  latencyMs?: number;
}

/**
 * Editorial-grade Decision Banner.
 * Full width of right column, 1px accent border, 2px left border signature,
 * tabular numerals, no gradients.
 */
export default function DecisionBanner({
  action,
  riskScore,
  criticalViolations,
  rationale,
  latencyMs,
}: DecisionBannerProps) {
  if (!action) {
    return (
      <EmptyState
        label="POLICY DECISION"
        description="Run an analysis to inspect safety verdict, calibrated risk, and rule violations."
        minHeight="140px"
      />
    );
  }

  // Accent styling based on decision action
  const accentStyles = {
    ALLOW: {
      border: "border-allow/80",
      leftBorder: "border-l-allow",
      bg: "bg-allow-bg",
      text: "text-allow",
      shadow: "shadow-[0_0_20px_rgba(107,191,89,0.12)]",
    },
    CONFIRM: {
      border: "border-confirm/80",
      leftBorder: "border-l-confirm",
      bg: "bg-confirm-bg",
      text: "text-confirm",
      shadow: "shadow-[0_0_20px_rgba(212,168,75,0.12)]",
    },
    REVISE: {
      border: "border-revise/80",
      leftBorder: "border-l-revise",
      bg: "bg-revise-bg",
      text: "text-revise",
      shadow: "shadow-[0_0_20px_rgba(201,122,61,0.12)]",
    },
    BLOCK: {
      border: "border-block/80",
      leftBorder: "border-l-block",
      bg: "bg-block-bg",
      text: "text-block",
      shadow: "shadow-[0_0_20px_rgba(193,75,61,0.15)]",
    },
  }[action];

  const pctScore = Math.round((riskScore ?? 0) * 100);

  return (
    <div
      className={`border ${accentStyles.border} ${accentStyles.leftBorder} border-l-[3px] rounded-[4px] ${accentStyles.bg} ${accentStyles.shadow} p-4 flex flex-col justify-between animate-decision-pulse transition-all`}
    >
      <div className="flex items-start justify-between">
        {/* Left: Verdict and Rationale */}
        <div className="flex flex-col space-y-1 pr-4">
          <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
            DECISION
          </span>
          <div
            className={`text-[28px] font-mono font-medium tracking-tight ${accentStyles.text}`}
          >
            {action}
          </div>
          <p className="text-[13px] text-text-muted leading-snug pt-1 max-w-[460px]">
            {rationale || "Evaluated by calibrated ML ensemble and deterministic safety rules."}
          </p>
        </div>

        {/* Right: Score and metrics */}
        <div className="flex flex-col items-end space-y-2 text-right shrink-0">
          <div className="flex items-baseline space-x-4">
            {/* Risk score */}
            <div className="flex flex-col items-end">
              <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
                RISK
              </span>
              <div className="text-[28px] font-mono font-medium tabular-nums text-text">
                {pctScore}
                <span className="text-[16px] text-text-dim font-normal">%</span>
              </div>
            </div>

            {/* Critical count */}
            <div className="flex flex-col items-end">
              <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
                CRITICAL
              </span>
              <div className="text-[28px] font-mono font-medium tabular-nums text-text">
                {criticalViolations ?? 0}
              </div>
            </div>
          </div>

          {/* Latency */}
          {latencyMs !== undefined && (
            <div className="text-[11px] font-mono text-text-dim tabular-nums">
              latency: {latencyMs.toFixed(1)}ms
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
