"use client";

import { NumberInput, Section, TextInput } from "@/components/ui/Field";
import type { SpaceConditionRow } from "@/lib/types";
import { useBuildingInput } from "@/providers/BuildingInputProvider";

const ROW_COUNT = 8;
const EMPTY_ROW: SpaceConditionRow = {
  area_type: "",
  percent_area: 0,
  occupant: 0,
  infiltration: 0,
  lighting: 0,
  plug_load: 0,
  conditioned: true,
};

function padded(rows: SpaceConditionRow[]): SpaceConditionRow[] {
  const out = rows.slice(0, ROW_COUNT);
  while (out.length < ROW_COUNT) out.push({ ...EMPTY_ROW });
  return out;
}

export function SpacesTab() {
  const { bi, updateBi } = useBuildingInput();
  if (!bi) return null;

  if (bi.space_rows.length === 0) {
    return (
      <Section title="Space Conditioning">
        <p className="py-6 text-center text-sm text-slate-500 dark:text-slate-400">
          Select a building type on the General Information tab — the code-mandated space
          conditions for that category will appear here for review and adjustment.
        </p>
      </Section>
    );
  }

  const rows = padded(bi.space_rows);
  const total = bi.space_rows.reduce((sum, r) => sum + (Number.isFinite(r.percent_area) ? r.percent_area : 0), 0);

  function commit(index: number, patch: Partial<SpaceConditionRow>) {
    const next = rows.map((r, i) => (i === index ? { ...r, ...patch } : r));
    updateBi({ space_rows: next.filter((r) => r.area_type.trim() !== "") });
  }

  return (
    <Section title="Space Conditioning">
      <div className="overflow-x-auto rounded-md border border-slate-200 dark:border-slate-700">
        <table className="w-full min-w-[820px] text-xs">
          <thead className="bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            <tr>
              {[
                "Space Type",
                "% Area",
                "Occupancy (m2/person)",
                "Infiltration (ACH)",
                "Lighting (W/m2)",
                "Equipment (W/m2)",
                "Conditioned",
                "Unconditioned",
              ].map((h) => (
                <th key={h} className="px-2 py-1.5 text-left font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="border-t border-slate-100 dark:border-slate-800">
                <td className="px-2 py-1">
                  <TextInput value={row.area_type} onChange={(e) => commit(i, { area_type: e.target.value })} />
                </td>
                <td className="px-2 py-1">
                  <NumberInput value={row.percent_area} onChange={(v) => commit(i, { percent_area: v ?? 0 })} step="0.1" />
                </td>
                <td className="px-2 py-1">
                  <NumberInput value={row.occupant} onChange={(v) => commit(i, { occupant: v ?? 0 })} step="0.1" />
                </td>
                <td className="px-2 py-1">
                  <NumberInput value={row.infiltration} onChange={(v) => commit(i, { infiltration: v ?? 0 })} step="0.01" />
                </td>
                <td className="px-2 py-1">
                  <NumberInput value={row.lighting} onChange={(v) => commit(i, { lighting: v ?? 0 })} step="0.1" />
                </td>
                <td className="px-2 py-1">
                  <NumberInput value={row.plug_load} onChange={(v) => commit(i, { plug_load: v ?? 0 })} step="0.1" />
                </td>
                <td className="px-2 py-1 text-center">
                  <input
                    type="radio"
                    name={`cond-${i}`}
                    checked={row.conditioned}
                    onChange={() => commit(i, { conditioned: true })}
                    className="h-3.5 w-3.5"
                    aria-label="Conditioned"
                  />
                </td>
                <td className="px-2 py-1 text-center">
                  <input
                    type="radio"
                    name={`cond-${i}`}
                    checked={!row.conditioned}
                    onChange={() => commit(i, { conditioned: false })}
                    className="h-3.5 w-3.5"
                    aria-label="Unconditioned"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-sm font-medium text-slate-700 dark:text-slate-200">Total: {total.toFixed(0)}%</p>
    </Section>
  );
}
