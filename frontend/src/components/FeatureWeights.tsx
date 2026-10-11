import React from "react";
import EmptyState from "./EmptyState";

interface FeatureWeightsProps {
  contributions?: Record<string, number>;
}

/**
 * Feature contributions card ("Why this score") displaying
 * normalized feature importances with relative thin indicator bars.
 */
export default function FeatureWeights({
  contributions,
}: FeatureWeightsProps) {
  const entries = Object.entries(contributions || {}).sort(
    (a, b) => Math.abs(b[1]) - Math.abs(a[1])
  );

  if (entries.length === 0) {
    return (
      <div className="border border-border rounded-[4px] bg-surface p-4 flex flex-col space-y-3">
        <div className="flex items-center justify-between border-b border-border/60 pb-2">
          <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
            WHY THIS SCORE
          </span>
        </div>
        <EmptyState
          label="FEATURE WEIGHTS"
          description="Feature weights will appear after the first analysis."
          minHeight="140px"
        />
      </div>
    );
  }

  const maxVal = Math.max(...entries.map(([, val]) => Math.abs(val)), 0.001);

  return (
    <div className="border border-border rounded-[4px] bg-surface p-4 flex flex-col space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/60 pb-2">
        <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
          WHY THIS SCORE
        </span>
        <span className="text-[10px] font-mono text-text-dim">TOP CONTRIBUTORS</span>
      </div>

      {/* Feature rows */}
      <div className="flex flex-col space-y-3 pt-1">
        {entries.slice(0, 6).map(([feat, val], idx) => {
          const ratio = Math.min(100, Math.max(0, (Math.abs(val) / maxVal) * 100));
          const isTop = idx === 0;
          return (
            <div key={feat} className="flex flex-col space-y-1">
              <div className="flex items-center justify-between text-[12px]">
                <div className="flex items-center space-x-1.5 truncate pr-2">
                  <span className="text-[10px] font-mono text-text-dim">#{idx + 1}</span>
                  <span className={`font-mono truncate ${isTop ? "text-text font-medium" : "text-text-muted"}`}>
                    {feat}
                  </span>
                </div>
                <span className={`font-mono tabular-nums text-right shrink-0 ${isTop ? "text-brand font-semibold" : "text-text"}`}>
                  {val.toFixed(4)}
                </span>
              </div>
              {/* Thin relative bar */}
              <div className="h-[2px] bg-border-str/60 w-full overflow-hidden rounded-full">
                <div
                  style={{ width: `${ratio}%` }}
                  className={`h-full ${isTop ? "bg-brand" : "bg-text-dim"} transition-all duration-300`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
