"use client";

import React, { useEffect, useState } from "react";
import {
  getAuditLog,
  verifyAuditChain,
  AuditRecord,
  AuditVerifyResponse,
} from "@/lib/api";

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
        return "bg-emerald-900/50 text-emerald-300 border-emerald-700/60";
      case "CONFIRM":
        return "bg-sky-900/50 text-sky-300 border-sky-700/60";
      case "REVISE":
        return "bg-amber-900/50 text-amber-300 border-amber-700/60";
      case "BLOCK":
      default:
        return "bg-rose-900/50 text-rose-300 border-rose-700/60";
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Tamper-Evident Audit Log Chain
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Immutable SHA-256 cryptographic hash chain verifying every security decision.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-xs font-medium text-slate-300 transition"
          >
            Refresh Logs
          </button>
          <button
            onClick={handleVerify}
            disabled={verifying}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
          >
            {verifying ? "Verifying Chain..." : "🔐 Verify Hash Chain"}
          </button>
        </div>
      </div>

      {/* Verification Status Banner */}
      {verifyResult && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between text-sm ${
            verifyResult.valid
              ? "bg-emerald-950/70 border-emerald-500 text-emerald-200"
              : "bg-rose-950/70 border-rose-500 text-rose-200"
          }`}
        >
          <div className="flex items-center space-x-3">
            <span className="text-xl">{verifyResult.valid ? "✅" : "❌"}</span>
            <div>
              <p className="font-semibold">
                {verifyResult.valid
                  ? "Audit Hash Chain Verified: 100% Cryptographically Intact"
                  : "Audit Chain Integrity Check FAILED"}
              </p>
              <p className="text-xs opacity-80 mt-0.5">
                {verifyResult.valid
                  ? "All records in SQLite match their sequential SHA-256 hash digest."
                  : `Violation detected at record ID ${verifyResult.broken_at_id}: ${verifyResult.reason}`}
              </p>
            </div>
          </div>
          <span className="text-xs font-mono uppercase px-2.5 py-1 bg-black/40 rounded">
            {verifyResult.valid ? "VALID" : "TAMPERED"}
          </span>
        </div>
      )}

      {/* Audit Logs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
          <h2 className="text-sm font-semibold text-slate-200">
            Recorded Security Decisions ({logs.length})
          </h2>
          <span className="text-xs text-slate-500">Ordered by most recent</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            Loading audit records from database...
          </div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            No audit records logged yet. Run a plan analysis on the Live Monitor.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {logs.map((record) => {
              const isExpanded = expandedId === record.audit_id;
              return (
                <div key={record.audit_id || record.id} className="hover:bg-slate-800/30 transition">
                  <div
                    onClick={() =>
                      setExpandedId(isExpanded ? null : record.audit_id)
                    }
                    className="px-6 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer text-xs"
                  >
                    <div className="flex items-center space-x-4">
                      <span
                        className={`px-2 py-0.5 rounded border text-[10px] font-semibold uppercase ${getDecisionBadge(
                          record.decision
                        )}`}
                      >
                        {record.decision}
                      </span>
                      <span className="text-slate-400 font-mono">
                        {record.timestamp?.substring(0, 19).replace("T", " ")} UTC
                      </span>
                      <span className="text-slate-200 truncate max-w-[280px]">
                        {record.rationale}
                      </span>
                    </div>

                    <div className="flex items-center space-x-4 text-slate-500 font-mono text-[11px]">
                      <span>Hash: {record.current_hash?.substring(0, 10)}...</span>
                      <span className="text-cyan-400">
                        {isExpanded ? "▲ Hide" : "▼ Details"}
                      </span>
                    </div>
                  </div>

                  {/* Expanded Detail Panel */}
                  {isExpanded && (
                    <div className="px-6 pb-4 pt-1 bg-slate-950/60 border-t border-slate-800/60 text-xs space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-slate-400 font-semibold mb-1">
                            Identifiers & Cryptographic Link
                          </p>
                          <div className="space-y-1 font-mono text-[11px] text-slate-300">
                            <div>Audit ID: {record.audit_id}</div>
                            <div>Trajectory ID: {record.trajectory_id}</div>
                            <div className="truncate">Prev Hash: {record.prev_hash}</div>
                            <div className="truncate text-cyan-400">
                              Current Hash: {record.current_hash}
                            </div>
                          </div>
                        </div>

                        <div>
                          <p className="text-slate-400 font-semibold mb-1">
                            Logged Request Payload
                          </p>
                          <pre className="p-2 bg-slate-900 border border-slate-800 rounded text-[10px] text-slate-300 overflow-x-auto max-h-32">
                            {record.payload}
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
