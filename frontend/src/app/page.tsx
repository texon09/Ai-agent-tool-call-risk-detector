"use client";

import React, { useState, useEffect } from "react";
import {
  analyzePlan,
  getScenarios,
  AnalyzeResponse,
  Scenario,
} from "@/lib/api";

export default function LiveMonitorPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenarioName, setSelectedScenarioName] = useState("");
  const [planJson, setPlanJson] = useState(
    JSON.stringify(
      {
        steps: [
          {
            tool_name: "database_query",
            arguments: { query: "SELECT id, title FROM projects WHERE id = 7" },
            permissions_required: ["database:read"],
            side_effect_class: "read",
            destination: "internal",
            data_sensitivity: "public",
            reversible: true,
            estimated_cost: 0.05,
          },
        ],
      },
      null,
      2
    )
  );

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    getScenarios().then((list) => setScenarios(list));
  }, []);

  const handleSelectScenario = (name: string) => {
    setSelectedScenarioName(name);
    const found = scenarios.find((s) => s.name === name);
    if (found) {
      setPlanJson(JSON.stringify(found.plan, null, 2));
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      const parsed = JSON.parse(planJson);
      const res = await analyzePlan(parsed);
      setResult(res);
    } catch (e: any) {
      setErrorMsg(`Invalid JSON plan: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getActionStyles = (action: string) => {
    switch (action) {
      case "ALLOW":
        return "bg-emerald-950/80 border-emerald-500 text-emerald-300";
      case "CONFIRM":
        return "bg-sky-950/80 border-sky-500 text-sky-300";
      case "REVISE":
        return "bg-amber-950/80 border-amber-500 text-amber-300";
      case "BLOCK":
      default:
        return "bg-rose-950/80 border-rose-500 text-rose-300";
    }
  };

  const parsedSteps = (() => {
    try {
      const p = JSON.parse(planJson);
      return Array.isArray(p.steps) ? p.steps : [p];
    } catch {
      return [];
    }
  })();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          AI Agent Plan Risk Monitor
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Inspect and intercept tool-call execution sequences before execution.
        </p>
      </div>

      {/* Editor & Scenario Selection */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-slate-300">
              Tool-Call Execution Plan (JSON)
            </label>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400">Load Scenario:</span>
              <select
                className="bg-slate-900 border border-slate-700 text-xs rounded px-2 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
                value={selectedScenarioName}
                onChange={(e) => handleSelectScenario(e.target.value)}
              >
                <option value="">(Custom Plan)</option>
                {scenarios.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name} ({s.expected_decision})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <textarea
            value={planJson}
            onChange={(e) => setPlanJson(e.target.value)}
            rows={12}
            className="w-full bg-slate-900/90 font-mono text-xs text-slate-200 border border-slate-700 rounded-lg p-4 focus:ring-1 focus:ring-cyan-500 focus:outline-none"
          />

          {errorMsg && (
            <div className="p-3 bg-rose-950/80 border border-rose-600 text-rose-300 text-xs rounded">
              {errorMsg}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-2.5 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-sm rounded-lg shadow transition disabled:opacity-50"
          >
            {loading ? "Analyzing Plan Security..." : "Analyze Tool-Call Plan"}
          </button>
        </div>

        {/* Trajectory Flow Preview */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-300">
            Trajectory Flow ({parsedSteps.length} Steps)
          </h2>
          <div className="space-y-3 max-h-[380px] overflow-y-auto pr-2">
            {parsedSteps.map((step: any, idx: number) => (
              <div
                key={idx}
                className="p-3 bg-slate-900 border border-slate-800 rounded-lg space-y-1.5 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-cyan-400">
                    Step {idx + 1}: {step.tool_name || "Unknown Tool"}
                  </span>
                  <span className="px-1.5 py-0.5 bg-slate-800 text-[10px] rounded text-slate-300 uppercase">
                    {step.side_effect_class || "read"}
                  </span>
                </div>
                <div className="text-slate-400 font-mono truncate">
                  {JSON.stringify(step.arguments || {})}
                </div>
                <div className="flex space-x-2 text-[10px] text-slate-500">
                  <span>Dest: {step.destination || "internal"}</span>
                  <span>Sens: {step.data_sensitivity || "internal"}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Analysis Results View */}
      {result && (
        <div className="space-y-6 pt-4 border-t border-slate-800">
          {/* Decision Banner */}
          <div
            className={`p-6 border-2 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 ${getActionStyles(
              result.action
            )}`}
          >
            <div>
              <div className="flex items-center space-x-3">
                <span className="text-xl font-bold tracking-wide">
                  DECISION: {result.action}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-black/40 font-mono">
                  {result.latency_ms} ms
                </span>
              </div>
              <p className="text-sm mt-1 opacity-90">{result.rationale}</p>
              <p className="text-xs mt-1 opacity-70 font-mono">
                Audit ID: {result.audit_id}
              </p>
            </div>

            <div className="flex items-center space-x-6 text-center">
              <div>
                <div className="text-2xl font-bold font-mono">
                  {(result.risk_score * 100).toFixed(0)}%
                </div>
                <div className="text-[10px] uppercase tracking-wider opacity-80">
                  Risk Score
                </div>
              </div>
              <div>
                <div className="text-2xl font-bold font-mono">
                  {result.critical_violations}
                </div>
                <div className="text-[10px] uppercase tracking-wider opacity-80">
                  Critical Violations
                </div>
              </div>
            </div>
          </div>

          {/* Details Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Rule Hits */}
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-3">
              <h3 className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                Triggered Rule Checks
              </h3>
              {result.rule_hits.length === 0 ? (
                <p className="text-xs text-slate-500">
                  No rule violations triggered.
                </p>
              ) : (
                <ul className="space-y-1.5">
                  {result.rule_hits.map((hit, i) => (
                    <li
                      key={i}
                      className="text-xs px-2 py-1 bg-slate-800/80 text-rose-300 rounded border border-rose-900/50"
                    >
                      {hit}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Model Votes */}
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-3">
              <h3 className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                Ensemble Model Votes
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Random Forest</span>
                  <span className="font-mono text-slate-200">
                    {((result.model_votes.rf_prob || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">XGBoost</span>
                  <span className="font-mono text-slate-200">
                    {((result.model_votes.xgb_prob || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Decision Tree</span>
                  <span className="font-mono text-slate-200">
                    {((result.model_votes.dt_prob || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Isolation Forest</span>
                  <span className="font-mono text-slate-200">
                    {result.model_votes.iso_flag ? "Anomaly" : "Normal"}
                  </span>
                </div>
              </div>
            </div>

            {/* Top Feature Contributions */}
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg space-y-3">
              <h3 className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                Top Risk Feature Weights
              </h3>
              {Object.keys(result.feature_contributions).length === 0 ? (
                <p className="text-xs text-slate-500">
                  No risk feature weights recorded.
                </p>
              ) : (
                <div className="space-y-1.5 text-xs">
                  {Object.entries(result.feature_contributions).map(
                    ([feat, weight]) => (
                      <div
                        key={feat}
                        className="flex justify-between items-center text-xs py-0.5"
                      >
                        <span className="text-slate-400 truncate max-w-[180px]">
                          {feat}
                        </span>
                        <span className="font-mono text-cyan-400">
                          {weight.toFixed(3)}
                        </span>
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
