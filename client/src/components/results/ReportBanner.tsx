"use client";

import { REPORT_COLORS } from "@/lib/constants";

export function TitleHeader({ children }: { children: React.ReactNode }) {
  return (
    <h1 className="text-center text-lg font-bold text-slate-800 dark:text-slate-100">{children}</h1>
  );
}

export function Banner({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded px-3 py-1.5 text-sm font-semibold text-white"
      style={{ background: REPORT_COLORS.bannerBlue }}
    >
      {children}
    </div>
  );
}

export function VerdictBanner({ compliant, children }: { compliant: boolean; children: React.ReactNode }) {
  return (
    <div
      className="rounded px-3 py-2 text-center text-sm font-bold text-white"
      style={{ background: compliant ? REPORT_COLORS.compliantGreen : REPORT_COLORS.nonCompliantRed }}
    >
      {children}
    </div>
  );
}

export function InfoGrid({ rows, columns = 2 }: { rows: [string, string][]; columns?: number }) {
  return (
    <div className={`grid gap-x-6 gap-y-1.5`} style={{ gridTemplateColumns: `repeat(${columns}, max-content 1fr)` }}>
      {rows.map(([label, value], i) => (
        <div key={i} className="contents">
          <span className="text-sm font-semibold text-slate-600 dark:text-slate-300">{label}</span>
          <span className="text-sm text-slate-800 dark:text-slate-100">{value}</span>
        </div>
      ))}
    </div>
  );
}
