"use client";

import React, { useMemo } from "react";
import { Scenario } from "../lib/types";

interface PlanEditorProps {
  value: string;
  onChange: (val: string) => void;
  scenarios: Scenario[];
  onSelectScenario: (sc: Scenario) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

/**
 * Plan editor card with line numbers, monospace JSON editor,
 * scenario dropdown, and full-width primary submission button.
 */
export default function PlanEditor({
  value,
  onChange,
  scenarios,
  onSelectScenario,
  onAnalyze,
  isLoading,
}: PlanEditorProps) {
  const lineCount = useMemo(() => {
    return Math.max(1, value.split("\n").length);
  }, [value]);

  const lineNumbers = useMemo(() => {
    return Array.from({ length: lineCount }, (_, i) => i + 1);
  }, [lineCount]);

  return (
    <div className="border border-border rounded-[4px] bg-surface flex flex-col overflow-hidden">
      {/* Header row */}
      <div className="px-4 py-2.5 border-b border-border flex items-center justify-between bg-surface-2/70">
        <div className="flex items-center space-x-2">
          <span className="w-1.5 h-1.5 rounded-full bg-brand" />
          <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
            PLAN EDITOR
          </span>
        </div>
        <span className="text-[10px] font-mono uppercase tracking-[0.05em] px-2 py-0.5 rounded-[2px] border border-border-str text-text-muted bg-surface-3">
          JSON PAYLOAD
        </span>
      </div>

      {/* Editor area with line numbers */}
      <div className="relative flex min-h-[380px] max-h-[520px] overflow-hidden bg-[#14151B]">
        {/* Line numbers column */}
        <div
          aria-hidden="true"
          className="w-11 select-none py-3 text-right pr-3 text-[11px] font-mono text-text-dim/80 border-r border-border bg-[#16171E] overflow-hidden"
        >
          {lineNumbers.map((num) => (
            <div key={num} className="h-5 leading-5">
              {num}
            </div>
          ))}
        </div>

        {/* Textarea */}
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck={false}
          className="flex-1 p-3.5 font-mono text-[13px] leading-5 text-text bg-transparent resize-none focus:outline-none overflow-y-auto selection:bg-border-str"
          placeholder='{\n  "steps": []\n}'
        />
      </div>

      {/* Bottom utility row */}
      <div className="px-4 py-2 border-t border-border flex items-center justify-between text-[12px] bg-surface-2/40">
        {/* Scenario selector */}
        <div className="flex items-center space-x-2">
          <label
            htmlFor="scenario-select"
            className="text-[11px] uppercase tracking-[0.08em] text-text-dim"
          >
            Scenario:
          </label>
          <select
            id="scenario-select"
            onChange={(e) => {
              const found = scenarios.find((s) => s.name === e.target.value);
              if (found) onSelectScenario(found);
            }}
            defaultValue=""
            className="bg-surface-2 border border-border-str text-text text-[12px] px-2.5 py-1 rounded-[3px] focus:outline-none focus:border-brand/70 hover:border-text-dim transition-colors cursor-pointer"
          >
            <option value="" disabled>
              Load scenario ▾
            </option>
            {scenarios.map((sc) => (
              <option key={sc.name} value={sc.name}>
                {sc.name} ({sc.expected_decision})
              </option>
            ))}
          </select>
        </div>

        {/* Character count */}
        <span className="font-mono text-[11px] text-text-dim">
          {value.length.toLocaleString()} chars · {lineCount} lines
        </span>
      </div>

      {/* Action button */}
      <div className="p-3 border-t border-border bg-surface">
        <button
          onClick={onAnalyze}
          disabled={isLoading}
          className="w-full h-10 rounded-[3px] bg-brand text-brand-text text-[13px] font-semibold tracking-tight hover:bg-brand-hover active:scale-[0.99] disabled:opacity-50 transition-all flex items-center justify-center space-x-2 cursor-pointer disabled:cursor-not-allowed shadow-[0_1px_12px_rgba(224,169,72,0.18)] hover:shadow-[0_2px_16px_rgba(224,169,72,0.28)]"
        >
          {isLoading ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-brand-text border-t-transparent rounded-full animate-spin" />
              <span>Analyzing Agent Plan…</span>
            </>
          ) : (
            <span className="flex items-center space-x-1.5">
              <span>Analyze Plan</span>
              <span className="text-[14px]">→</span>
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
