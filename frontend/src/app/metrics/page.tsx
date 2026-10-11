"use client";

import React, { useEffect, useState } from "react";
import { getMetrics, MetricsResponse } from "@/lib/api";

export default function MetricsPage() {
  const [data, setData] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMetrics()
      .then((res) => setData(res))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Model Evaluation Metrics
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Offline test benchmark metrics across decision trees, random forests,
          XGBoost, and isolation forest models.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">
          Loading metrics report from /api/metrics...
        </div>
      ) : !data || !data.available ? (
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 text-sm">
          Metrics report currently unavailable. Run the offline evaluation
          pipeline to refresh metrics.
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(data.models).map(([name, m]) => (
              <div
                key={name}
                className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-4"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white capitalize">
                    {name.replace("_", " ")}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 bg-slate-800 rounded text-cyan-400 font-mono">
                    {m.latency_ms} ms
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-800/80">
                    <span className="text-slate-400">F1 Score</span>
                    <span className="font-mono font-medium text-emerald-400">
                      {(m.f1 * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/80">
                    <span className="text-slate-400">Precision</span>
                    <span className="font-mono text-slate-300">
                      {(m.precision * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800/80">
                    <span className="text-slate-400">Recall</span>
                    <span className="font-mono text-slate-300">
                      {(m.recall * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">AUROC</span>
                    <span className="font-mono font-medium text-cyan-400">
                      {(m.auroc * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Model Summary Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-800">
              <h2 className="text-sm font-semibold text-slate-200">
                Detailed Metrics Comparison Table
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="px-6 py-3">Model</th>
                    <th className="px-6 py-3">F1 Score</th>
                    <th className="px-6 py-3">Precision</th>
                    <th className="px-6 py-3">Recall</th>
                    <th className="px-6 py-3">AUROC</th>
                    <th className="px-6 py-3">Per-Call Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 font-mono">
                  {Object.entries(data.models).map(([name, m]) => (
                    <tr key={name} className="hover:bg-slate-800/40">
                      <td className="px-6 py-3.5 font-sans font-medium text-slate-200 capitalize">
                        {name.replace("_", " ")}
                      </td>
                      <td className="px-6 py-3.5 text-emerald-400">{m.f1.toFixed(4)}</td>
                      <td className="px-6 py-3.5 text-slate-300">{m.precision.toFixed(4)}</td>
                      <td className="px-6 py-3.5 text-slate-300">{m.recall.toFixed(4)}</td>
                      <td className="px-6 py-3.5 text-cyan-400">{m.auroc.toFixed(4)}</td>
                      <td className="px-6 py-3.5 text-slate-400">{m.latency_ms.toFixed(3)} ms</td>
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
