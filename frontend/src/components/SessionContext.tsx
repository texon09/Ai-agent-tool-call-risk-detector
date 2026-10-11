import React from "react";

interface SessionContextProps {
  permissions?: string[];
  budget?: number;
}

/**
 * Compact session context metadata display with monospace data values.
 */
export default function SessionContext({
  permissions = ["db_read", "fs_read", "network_internal"],
  budget = 1.0,
}: SessionContextProps) {
  return (
    <div className="border border-border-str rounded-[4px] bg-surface p-4 flex flex-col space-y-3">
      <div className="flex items-center justify-between border-b border-border/80 pb-2">
        <span className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-dim flex items-center space-x-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-brand/80" />
          <span>SESSION CONTEXT</span>
        </span>
        <span className="text-[10px] font-mono text-brand/90 px-1.5 py-0.5 rounded-[2px] bg-brand-glow border border-brand/30">
          PROTECTED SCOPE
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-[13px]">
        {/* Permissions */}
        <div className="flex flex-col space-y-1.5">
          <span className="text-[11px] text-text-dim uppercase tracking-[0.05em]">
            Allowed Permissions
          </span>
          <div className="flex flex-wrap gap-1">
            {permissions.map((p) => (
              <span
                key={p}
                className="font-mono text-[11px] px-1.5 py-0.5 rounded-[2px] bg-surface-2 border border-border text-text-muted"
              >
                {p}
              </span>
            ))}
          </div>
        </div>

        {/* Budget */}
        <div className="flex flex-col space-y-1.5">
          <span className="text-[11px] text-text-dim uppercase tracking-[0.05em]">
            Max Step Budget
          </span>
          <div className="font-mono text-[13px] text-brand tabular-nums font-semibold flex items-baseline space-x-1">
            <span>${budget.toFixed(2)}</span>
            <span className="text-[10px] text-text-dim font-normal">USD / CALL</span>
          </div>
        </div>
      </div>
    </div>
  );
}
