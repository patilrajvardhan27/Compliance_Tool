"use client";

import { useMemo, useState } from "react";

import { GlassDialog } from "@/components/dialogs/GlassDialog";
import { Button, FieldRow, NumberInput, RadioGroup, Section, SelectField } from "@/components/ui/Field";
import { imageUrl } from "@/lib/api";
import { SHADING_IMAGE_FILE, SKYLIGHT_TYPES } from "@/lib/constants";
import type { GlassEntry, WindowAllocationRow } from "@/lib/types";
import { useBuildingInput } from "@/providers/BuildingInputProvider";
import { useReferenceData } from "@/providers/ReferenceDataProvider";

const CREATE = "-Create-";
const ORIENTATIONS: { key: keyof WindowAllocationRow; label: string }[] = [
  { key: "south_percent", label: "South" },
  { key: "north_percent", label: "North" },
  { key: "east_percent", label: "East" },
  { key: "west_percent", label: "West" },
];

export function WindowsTab() {
  const ref = useReferenceData();
  const { bi, updateBi } = useBuildingInput();
  const [glassDialogRow, setGlassDialogRow] = useState<number | null>(null);

  const glassNames = useMemo(() => {
    const names = new Set(Object.keys(ref.glass));
    for (const g of bi?.user_glass ?? []) names.add(g.user_name);
    return Array.from(names);
  }, [ref.glass, bi?.user_glass]);

  if (!bi) return null;

  function updateRow(index: number, patch: Partial<WindowAllocationRow>) {
    const rows = bi!.window_rows.map((r, i) => (i === index ? { ...r, ...patch } : r));
    updateBi({ window_rows: rows });
  }

  function handleGlassCreated(entry: GlassEntry) {
    updateBi({ user_glass: [...bi!.user_glass, entry] });
    if (glassDialogRow !== null) updateRow(glassDialogRow, { glass_type: entry.user_name });
    setGlassDialogRow(null);
  }

  const unitLabel = bi.rdbtnWinWwr ? "Window-to-Wall Ratio (%)" : "Window Area (m2)";

  return (
    <div className="flex flex-col gap-4">
      <Section title="Windows — conditioned zones only">
        <RadioGroup
          name="win-unit"
          value={bi.rdbtnWinWwr ? "wwr" : "area"}
          onChange={(v) => updateBi({ rdbtnWinWwr: v === "wwr" })}
          options={[
            { value: "wwr", label: "Window-to-Wall Ratio (%)" },
            { value: "area", label: "Window Area (m2)" },
          ]}
        />

        <div className="overflow-x-auto rounded-md border border-slate-200 dark:border-slate-700">
          <table className="w-full min-w-[720px] text-xs">
            <thead className="bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th className="px-2 py-1.5 text-left font-medium">#</th>
                {ORIENTATIONS.map((o) => (
                  <th key={o.key} className="px-2 py-1.5 text-left font-medium">
                    {o.label}
                  </th>
                ))}
                <th className="px-2 py-1.5 text-left font-medium">Glass Type</th>
                <th className="px-2 py-1.5" />
              </tr>
            </thead>
            <tbody>
              {bi.window_rows.map((row, i) => (
                <tr key={i} className="border-t border-slate-100 dark:border-slate-800">
                  <td className="px-2 py-1 text-slate-500">#{i + 1}</td>
                  {ORIENTATIONS.map((o) => (
                    <td key={o.key} className="px-2 py-1">
                      <NumberInput
                        value={row[o.key] as number}
                        onChange={(v) => updateRow(i, { [o.key]: v ?? 0 } as Partial<WindowAllocationRow>)}
                        step="0.1"
                        min={0}
                      />
                    </td>
                  ))}
                  <td className="px-2 py-1">
                    <SelectField
                      value={row.glass_type}
                      onChange={(v) => updateRow(i, { glass_type: v })}
                      options={glassNames}
                      placeholder="Select glass…"
                      createOption={CREATE}
                      onCreate={() => setGlassDialogRow(i)}
                    />
                  </td>
                  <td className="px-2 py-1">
                    <Button
                      onClick={() =>
                        row.glass_type && row.glass_type !== CREATE
                          ? alert(
                              `Selected glass: ${row.glass_type}\n(editing an existing glass type is not supported — use "-Create-" to add a new type).`
                            )
                          : alert("Please select a glass type first.")
                      }
                    >
                      Edit
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-500">Values entered above are treated as {unitLabel}.</p>

        <div className="flex gap-6">
          <div className="flex flex-1 flex-col gap-3">
            <FieldRow label="South Overhang Depth (m):">
              <NumberInput value={bi.txtWinSouthOverhang} onChange={(v) => updateBi({ txtWinSouthOverhang: v })} step="0.01" min={0} max={10} />
            </FieldRow>
            <FieldRow label="South Projection Factor:">
              <NumberInput value={bi.txtWinSouthFp} onChange={(v) => updateBi({ txtWinSouthFp: v })} step="0.01" min={0} max={5} />
            </FieldRow>
          </div>
          <div className="flex w-52 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-50 p-2 dark:border-slate-700 dark:bg-slate-800">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={imageUrl(SHADING_IMAGE_FILE)} alt="Shading" className="max-h-40 max-w-full object-contain" />
          </div>
        </div>

        <FieldRow label="Skylight Type:">
          <SelectField
            value={bi.txtSkyltType}
            onChange={(v) => updateBi({ txtSkyltType: v })}
            options={SKYLIGHT_TYPES}
            placeholder="Select a skylight type…"
          />
        </FieldRow>
        <FieldRow label="Coverage (%):">
          <NumberInput value={bi.txtSkyltCvr} onChange={(v) => updateBi({ txtSkyltCvr: v })} min={0} max={100} step="0.1" />
        </FieldRow>
      </Section>

      {glassDialogRow !== null && (
        <GlassDialog onClose={() => setGlassDialogRow(null)} onSave={handleGlassCreated} />
      )}
    </div>
  );
}
