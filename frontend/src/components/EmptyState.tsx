import React from "react";

interface EmptyStateProps {
  label: string;
  description: string;
  minHeight?: string;
}

/**
 * Clean, dashed-border placeholder maintaining consistent layout density
 * without layout shifts between empty and populated states.
 */
export default function EmptyState({
  label,
  description,
  minHeight = "120px",
}: EmptyStateProps) {
  return (
    <div
      style={{ minHeight }}
      className="border border-dashed border-border rounded-[4px] p-4 flex flex-col items-center justify-center text-center bg-bg/40 select-none"
    >
      <div className="w-1.5 h-1.5 rounded-full bg-border-str mb-2" />
      <span className="text-[11px] font-mono uppercase tracking-[0.08em] text-text-dim mb-1">
        {label}
      </span>
      <p className="text-[12px] text-text-muted max-w-[280px] leading-relaxed">
        {description}
      </p>
    </div>
  );
}
