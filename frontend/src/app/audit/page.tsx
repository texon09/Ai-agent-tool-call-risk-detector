"use client";

import React, { useEffect, useState } from "react";
import {
  getAuditLog,
  verifyAuditChain,
  AuditRecord,
  AuditVerifyResponse,
} from "@/lib/api";

/**
 * Editorial-grade Tamper-Evident Audit Ledger.
 * Styled with precision palette, hairline borders, tabular numerals,
 * and cryptographic verification banner matching the console design.
 */
export default function AuditPage() {
  const [logs, setLogs] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<AuditVerifyResponse | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const records = await getAuditLog(50, 0);
      setLogs(records);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleVerify = async () => {
    setVerifying(true);
    try {
      const res = await verifyAuditChain();
      setVerifyResult(res);
    } finally {
      setVerifying(false);
    }
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case "ALLOW":
        return "bg-allow-bg text-allow border-allow/40";
      case "CONFIRM":
        return "bg-confirm-bg text-confirm border-confirm/40";
      case "REVISE":
        return "bg-revise-bg text-revise border-revise/40";
      case "BLOCK":
      default:
        return "bg-block-bg text-block border-block/40";
    }
  };

  return (
    <div className="space-y-5 w-full">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-brand" />
            <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
              CRYPTOGRAPHIC LEDGER
            </span>
          </div>
          <h1 className="text-[20px] font-medium tracking-tight text-text mt-0.5">
            Tamper-Evident Audit Log Chain
          </h1>
          <p className="text-[13px] text-text-muted mt-0.5">
            Immutable SHA-256 hash sequence cryptographically anchoring each agent tool execution.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-3 py-1.5 bg-surface-2 hover:bg-surface-3 border border-border-str rounded-[3px] text-[12px] font-medium text-text-muted hover:text-text transition-colors cursor-pointer"
          >
            {loading ? "Refreshing…" : "Refresh"}
          </button>
          <button
            onClick={handleVerify}
            disabled={verifying}
            className="px-3.5 py-1.5 bg-brand hover:bg-brand-hover text-brand-text rounded-[3px] text-[12px] font-semibold tracking-tight shadow-[0_1px_10px_rgba(224,169,72,0.18)] transition-all disabled:opacity-50 cursor-pointer flex items-center space-x-1.5"
          >
            {verifying ? (
              <>
                <span className="w-3 h-3 border-2 border-brand-text border-t-transparent rounded-full animate-spin" />
                <span>Verifying Hashes…</span>
              </>
            ) : (
              <span>Verify Cryptographic Chain →</span>
            )}
          </button>
        </div>
      </div>

      {/* Verification Status Banner */}
      {verifyResult && (
        <div
          className={`p-4 rounded-[4px] border ${
            verifyResult.valid
              ? "bg-allow-bg border-allow text-allow shadow-[0_0_20px_rgba(82,183,136,0.10)]"
              : "bg-block-bg border-block text-block shadow-[0_0_20px_rgba(230,57,70,0.15)]"
          } flex items-center justify-between text-[13px] animate-fade-in`}
        >
          <div className="flex items-start space-x-3">
            <span className="font-mono text-[16px] leading-tight mt-0.5">
              {verifyResult.valid ? "✓" : "⚠"}
            </span>
            <div>
              <p className="font-medium text-text">
                {verifyResult.valid
                  ? "Audit Chain Integrity Verified: 100% Sequence Consistency"
                  : "Audit Chain Integrity Check Failed"}
              </p>
              <p className="text-[12px] text-text-muted mt-0.5">
                {verifyResult.valid
                  ? "All records in SQLite match sequential SHA-256 cryptographic linkage."
                  : `Integrity break detected at record ID ${verifyResult.broken_at_id}: ${verifyResult.reason}`}
              </p>
            </div>
          </div>
          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-[2px] bg-bg/60 border border-current">
            {verifyResult.valid ? "INTACT" : "TAMPERED"}
          </span>
        </div>
      )}

      {/* Audit Logs Table */}
      <div className="border border-border rounded-[4px] bg-surface overflow-hidden">
        <div className="px-5 py-3 border-b border-border bg-surface-2/60 flex justify-between items-center text-[12px]">
          <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim">
            RECORDED SECURITY DECISIONS ({logs.length})
          </span>
          <span className="font-mono text-[11px] text-text-dim">
            LATEST ENTRIES FIRST
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-text-dim font-mono text-[12px]">
            Reading cryptographic records from audit.db…
          </div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-text-muted text-[13px]">
            No audit records logged yet. Run a plan analysis on the workspace to record entries.
          </div>
        ) : (
          <div className="divide-y divide-border/60">
            {logs.map((record) => {
              const isExpanded = expandedId === record.audit_id;
              return (
                <div key={record.audit_id || record.id} className="hover:bg-surface-2/40 transition-colors">
                  <div
                    onClick={() =>
                      setExpandedId(isExpanded ? null : record.audit_id)
                    }
                    className="px-5 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer text-[13px]"
                  >
                    <div className="flex items-center space-x-3 truncate">
                      <span
                        className={`px-2 py-0.5 rounded-[2px] border text-[10px] font-mono font-medium uppercase tracking-[0.05em] shrink-0 ${getDecisionBadge(
                          record.decision
                        )}`}
                      >
                        {record.decision}
                      </span>
                      <span className="text-text-dim font-mono text-[11px] shrink-0">
                        {record.timestamp?.substring(0, 19).replace("T", " ")}
                      </span>
                      <span className="text-text truncate max-w-[380px]">
                        {record.rationale}
                      </span>
                    </div>

                    <div className="flex items-center space-x-3 text-text-dim font-mono text-[11px] shrink-0">
                      <span>Hash: {record.current_hash?.substring(0, 12)}…</span>
                      <span className="text-brand hover:underline">
                        {isExpanded ? "Hide ▲" : "Details ▼"}
                      </span>
                    </div>
                  </div>

                  {/* Expanded Detail Panel */}
                  {isExpanded && (
                    <div className="px-5 pb-4 pt-1 bg-surface-2/60 border-t border-border/60 text-[12px] space-y-3 animate-fade-in">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <p className="text-[11px] font-medium uppercase tracking-[0.05em] text-text-dim">
                            Cryptographic Block Chain Link
                          </p>
                          <div className="space-y-1 font-mono text-[11px] text-text-muted bg-[#14151B] p-2.5 rounded-[3px] border border-border">
                            <div><span className="text-text-dim">ID:</span> {record.id} · <span className="text-text-dim">Audit ID:</span> {record.audit_id}</div>
                            <div><span className="text-text-dim">Trajectory:</span> {record.trajectory_id}</div>
                            <div className="truncate"><span className="text-text-dim">Prev Hash:</span> {record.prev_hash}</div>
                            <div className="truncate text-brand font-medium">
                              <span className="text-text-dim">Curr Hash:</span> {record.current_hash}
                            </div>
                          </div>
                        </div>

                        <div className="space-y-1">
                          <p className="text-[11px] font-medium uppercase tracking-[0.05em] text-text-dim">
                            Logged Request Payload
                          </p>
                          <pre className="p-2.5 bg-[#14151B] border border-border rounded-[3px] font-mono text-[11px] text-text-muted overflow-x-auto max-h-36 selection:bg-border-str">
                            {(() => {
                              try {
                                return JSON.stringify(JSON.parse(record.payload), null, 2);
                              } catch {
                                return record.payload;
                              }
                            })()}
                          </pre>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
