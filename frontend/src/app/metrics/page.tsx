"use client";

import React, { useEffect, useState } from "react";
import { getMetrics, MetricsResponse } from "@/lib/api";

/**
 * Editorial Model Evaluation Metrics Page.
 * Visual layout matching the terminal workspace with precision cards,
 * tabular numbers, and hairline borders.
 */
export default function MetricsPage() {
  const [data, setData] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMetrics()
      .then((res) => setData(res))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-brand" />
            <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
              OFFLINE BENCHMARKS
            </span>
          </div>
          <h1 className="text-[20px] font-medium tracking-tight text-text mt-0.5">
            Model Evaluation Metrics
          </h1>
          <p className="text-[13px] text-text-muted mt-0.5">
            Test set validation metrics across Decision Tree, Random Forest, XGBoost, and Isolation Forest.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-mono px-2 py-1 rounded-[3px] border border-border-str bg-surface-2 text-text-muted">
            VALIDATION FPR TARGET: 5.0%
          </span>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-text-dim font-mono text-[12px]">
          Reading offline metrics manifest…
        </div>
      ) : !data || !data.available ? (
        <div className="p-6 bg-surface border border-border rounded-[4px] text-text-muted text-[13px]">
          Metrics report currently loading. Retraining and calibration benchmarks will populate here.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top 4 Model Stat Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(data.models).map(([name, m]) => (
              <div
                key={name}
                className="p-4 bg-surface border border-border rounded-[4px] space-y-3"
              >
                <div className="flex items-center justify-between border-b border-border/70 pb-2">
                  <span className="text-[13px] font-medium text-text capitalize">
                    {name.replace("_", " ")}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-surface-2 border border-border rounded-[2px] text-brand font-mono">
                    {m.latency_ms.toFixed(2)} ms
                  </span>
                </div>

                <div className="space-y-2 text-[12px]">
                  <div className="flex justify-between items-baseline py-0.5 border-b border-border/40">
                    <span className="text-text-muted">F1 Score</span>
                    <span className="font-mono font-medium text-allow tabular-nums">
                      {(m.f1 * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-baseline py-0.5 border-b border-border/40">
                    <span className="text-text-muted">Precision</span>
                    <span className="font-mono text-text tabular-nums">
                      {(m.precision * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-baseline py-0.5 border-b border-border/40">
                    <span className="text-text-muted">Recall</span>
                    <span className="font-mono text-text tabular-nums">
                      {(m.recall * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-baseline py-0.5">
                    <span className="text-text-muted">AUROC</span>
                    <span className="font-mono font-medium text-brand tabular-nums">
                      {(m.auroc * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Detailed Table */}
          <div className="border border-border rounded-[4px] bg-surface overflow-hidden">
            <div className="px-5 py-3 border-b border-border bg-surface-2/60">
              <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
                DETAILED METRICS COMPARISON TABLE
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-[12px] text-left">
                <thead className="bg-[#14151B] text-text-dim uppercase tracking-[0.06em] text-[10px] font-medium border-b border-border">
                  <tr>
                    <th className="px-5 py-2.5 font-medium">Model</th>
                    <th className="px-5 py-2.5 font-medium">F1 Score</th>
                    <th className="px-5 py-2.5 font-medium">Precision</th>
                    <th className="px-5 py-2.5 font-medium">Recall</th>
                    <th className="px-5 py-2.5 font-medium">AUROC</th>
                    <th className="px-5 py-2.5 font-medium">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60 font-mono text-text">
                  {Object.entries(data.models).map(([name, m]) => (
                    <tr key={name} className="hover:bg-surface-2/40 transition-colors">
                      <td className="px-5 py-3 font-sans font-medium text-text capitalize">
                        {name.replace("_", " ")}
                      </td>
                      <td className="px-5 py-3 text-allow tabular-nums font-medium">{m.f1.toFixed(4)}</td>
                      <td className="px-5 py-3 text-text-muted tabular-nums">{m.precision.toFixed(4)}</td>
                      <td className="px-5 py-3 text-text-muted tabular-nums">{m.recall.toFixed(4)}</td>
                      <td className="px-5 py-3 text-brand tabular-nums font-medium">{m.auroc.toFixed(4)}</td>
                      <td className="px-5 py-3 text-text-dim tabular-nums">{m.latency_ms.toFixed(3)} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
