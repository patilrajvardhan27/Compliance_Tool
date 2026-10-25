"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { REPORT_COLORS } from "@/lib/constants";
import type { ClassRow } from "@/lib/types";

/** Class 1-8 horizontal bar chart: red threshold bars ("Compliance") vs the building's own
 * BECth ("Building"), ported from performance_view.py's QtCharts implementation. */
export function BecThChart({ classRows, bldgBecTh }: { classRows: ClassRow[]; bldgBecTh: number }) {
  const data = classRows.map((row) => ({
    name: row.class_name,
    Compliance: row.class_value,
    Building: row.class_bldg ? Number(row.class_bldg) : null,
  }));
  const maxVal = Math.max(...classRows.map((r) => r.class_value), bldgBecTh) * 1.2;

  return (
    <div>
      <p className="mb-1 text-center text-xs font-semibold text-muted">
        [kWh/m2.year]
      </p>
      <ResponsiveContainer width="100%" height={360}>
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 48, bottom: 8, left: 8 }} barGap={2}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="currentColor" className="text-hairline" />
          <XAxis type="number" domain={[0, maxVal]} tick={{ fontSize: 11 }} stroke="currentColor" className="text-muted" />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={56} stroke="currentColor" className="text-muted" />
          <Tooltip
            formatter={(value) => (typeof value === "number" ? value.toFixed(1) : "—")}
            contentStyle={{ fontSize: 12, borderRadius: 11, border: "1px solid var(--color-hairline)" }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar
            dataKey="Compliance"
            fill={REPORT_COLORS.thresholdBar}
            radius={[0, 9, 9, 0]}
            barSize={14}
            label={{ position: "right", fontSize: 10, fill: "currentColor", formatter: (v: unknown) => (typeof v === "number" ? v.toFixed(1) : "") }}
          />
          <Bar
            dataKey="Building"
            fill={REPORT_COLORS.buildingBar}
            radius={[0, 9, 9, 0]}
            barSize={14}
            label={{ position: "right", fontSize: 10, fill: "currentColor", formatter: (v: unknown) => (typeof v === "number" ? v.toFixed(1) : "") }}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
