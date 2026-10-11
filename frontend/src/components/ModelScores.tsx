import React from "react";
import EmptyState from "./EmptyState";
import { ModelScores, ModelVotes } from "../lib/types";

interface ModelScoresProps {
  scores?: ModelScores;
  votes?: ModelVotes;
  ensembleScore?: number;
}

/**
 * Clean side-by-side model score comparison card.
 * Monospace probabilities, thin 2px progress indicators, tabular alignment.
 */
export default function ModelScoresCard({
  scores,
  votes,
  ensembleScore,
}: ModelScoresProps) {
  if (!scores && !votes) {
    return (
      <div className="border border-border rounded-[4px] bg-surface p-4 flex flex-col space-y-3">
        <div className="flex items-center justify-between border-b border-border/60 pb-2">
          <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
            ENSEMBLE MODEL VOTES
          </span>
        </div>
        <EmptyState
          label="AWAITING ANALYSIS"
          description="Model breakdown for Decision Tree, Random Forest, XGBoost, and Isolation Forest will appear here."
          minHeight="140px"
        />
      </div>
    );
  }

  // Normalize scores from either model_scores or model_votes
  const dt = scores?.decision_tree ?? votes?.dt_prob ?? 0;
  const rf = scores?.random_forest ?? votes?.rf_prob ?? 0;
  const xgb = scores?.xgboost ?? votes?.xgb_prob ?? 0;
  const iso =
    scores?.isolation_forest ??
    (typeof votes?.iso_flag === "number" ? votes.iso_flag : votes?.iso_flag ? 1 : 0);
  const ens = scores?.ensemble ?? ensembleScore ?? 0;

  const rows = [
    { name: "Decision Tree", score: dt, weight: "10%" },
    { name: "Random Forest", score: rf, weight: "40%" },
    { name: "XGBoost", score: xgb, weight: "40%" },
    { name: "Isolation Forest", score: iso, weight: "10%" },
  ];

  return (
    <div className="border border-border rounded-[4px] bg-surface p-4 flex flex-col space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/60 pb-2">
        <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
          ENSEMBLE MODEL VOTES
        </span>
        <span className="text-[10px] font-mono text-text-dim">4-MODEL CONSENSUS</span>
      </div>

      {/* Model rows */}
      <div className="flex flex-col space-y-2 pt-1">
        {rows.map((row) => {
          const pct = Math.round(row.score * 100);
          const barColor =
            row.score >= 0.75
              ? "bg-block"
              : row.score >= 0.40
              ? "bg-confirm"
              : "bg-allow";
          return (
            <div
              key={row.name}
              className="grid grid-cols-[140px_1fr_60px] items-center gap-3 text-[13px]"
            >
              <div className="flex items-baseline space-x-1.5 truncate">
                <span className="text-text-muted truncate">{row.name}</span>
                <span className="text-[10px] font-mono text-text-dim">
                  ({row.weight})
                </span>
              </div>

              {/* Progress track */}
              <div className="h-[3px] bg-border-str/70 rounded-full overflow-hidden w-full">
                <div
                  style={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
                  className={`h-full ${barColor} transition-all duration-300`}
                />
              </div>

              {/* Score */}
              <span className="font-mono text-[13px] text-right text-text tabular-nums font-medium">
                {pct}%
              </span>
            </div>
          );
        })}

        {/* Ensemble row (separated by 1px hairline) */}
        <div className="pt-2 mt-2 border-t border-border grid grid-cols-[140px_1fr_60px] items-center gap-3">
          <div className="flex items-center space-x-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-brand" />
            <span className="text-[13px] font-medium text-text">
              Weighted Ensemble
            </span>
          </div>

          <div className="h-[4px] bg-border-str/90 rounded-full overflow-hidden w-full">
            <div
              style={{
                width: `${Math.min(100, Math.max(0, Math.round(ens * 100)))}%`,
              }}
              className={`h-full ${
                ens >= 0.75
                  ? "bg-block"
                  : ens >= 0.40
                  ? "bg-confirm"
                  : "bg-allow"
              } transition-all duration-300`}
            />
          </div>

          <span className="font-mono text-[14px] text-right text-brand tabular-nums font-semibold">
            {Math.round(ens * 100)}%
          </span>
        </div>
      </div>
    </div>
  );
}
