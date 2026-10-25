"use client";

import { REPORT_COLORS } from "@/lib/constants";

export function TitleHeader({ children }: { children: React.ReactNode }) {
  return (
    <h1 className="text-center text-[24px] tracking-[-0.3px]">{children}</h1>
  );
}

export function Banner({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded-chip px-4 py-2 text-[14px] font-semibold text-white"
      style={{ background: REPORT_COLORS.banner }}
    >
      {children}
    </div>
  );
}

export function VerdictBanner({ compliant, children }: { compliant: boolean; children: React.ReactNode }) {
  return (
    <div
      className="animate-scale-in rounded-chip px-4 py-3 text-center text-[15px] font-semibold text-white"
      style={{ background: compliant ? REPORT_COLORS.compliant : REPORT_COLORS.nonCompliant }}
    >
      {children}
    </div>
  );
}

export function InfoGrid({ rows, columns = 2 }: { rows: [string, string][]; columns?: number }) {
  return (
    <div className="grid gap-x-6 gap-y-1.5" style={{ gridTemplateColumns: `repeat(${columns}, max-content 1fr)` }}>
      {rows.map(([label, value], i) => (
        <div key={i} className="contents">
          <span className="text-[14px] text-muted">{label}</span>
          <span className="nums text-[14px] text-body">{value}</span>
        </div>
      ))}
    </div>
  );
}
