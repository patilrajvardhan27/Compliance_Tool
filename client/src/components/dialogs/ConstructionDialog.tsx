"use client";

import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { Button, FieldRow, NumberInput, SelectField, TextInput } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";
import { useBuildingInput } from "@/providers/BuildingInputProvider";
import { useReferenceData } from "@/providers/ReferenceDataProvider";
import { computeConstructionUValue } from "@/lib/api";
import type { ConstructionEntry, LayerEntry, MaterialEntry } from "@/lib/types";

import { MaterialDialog } from "./MaterialDialog";

const METHODS = ["Enter layers", "Enter U-Value"];
const LAYER_ROWS = 7;
const CREATE = "-Create-";

interface Row {
  material: string;
}

export function ConstructionDialog({
  kind,
  onClose,
  onSave,
}: {
  kind: "Wall" | "Roof";
  onClose: () => void;
  onSave: (construction: ConstructionEntry) => void;
}) {
  const ref = useReferenceData();
  const { bi, updateBi } = useBuildingInput();

  const [name, setName] = useState("");
  const [method, setMethod] = useState(METHODS[0]);
  const [roughness, setRoughness] = useState(4);
  const [absorptance, setAbsorptance] = useState(0.6);
  const [layerName, setLayerName] = useState("");
  const [rows, setRows] = useState<Row[]>(Array.from({ length: LAYER_ROWS }, () => ({ material: "" })));
  const [uValueDirect, setUValueDirect] = useState(0.5);
  const [materialDialogRow, setMaterialDialogRow] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const allMaterials = useMemo<Record<string, MaterialEntry>>(() => {
    const merged: Record<string, MaterialEntry> = { ...ref.materials };
    for (const m of bi?.user_materials ?? []) merged[m.user_name] = m;
    return merged;
  }, [ref.materials, bi?.user_materials]);

  const materialNames = Object.keys(allMaterials);

  const resistances = useMemo(
    () =>
      rows
        .filter((r) => r.material && allMaterials[r.material])
        .map((r) => allMaterials[r.material].resistance),
    [rows, allMaterials]
  );

  const { data: uValueData } = useQuery({
    queryKey: ["construction-uvalue", resistances],
    queryFn: () => computeConstructionUValue({ resistances }),
    enabled: resistances.length > 0,
  });
  const calculatedU = resistances.length > 0 ? (uValueData?.u_value ?? null) : null;

  function setRowMaterial(index: number, materialName: string) {
    if (materialName === CREATE) {
      setMaterialDialogRow(index);
      return;
    }
    setRows((current) => current.map((r, i) => (i === index ? { material: materialName } : r)));
  }

  function handleMaterialCreated(entry: MaterialEntry) {
    if (bi) updateBi({ user_materials: [...bi.user_materials, entry] });
    if (materialDialogRow !== null) {
      setRows((current) =>
        current.map((r, i) => (i === materialDialogRow ? { material: entry.user_name } : r))
      );
    }
    setMaterialDialogRow(null);
  }

  async function handleSave() {
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Please enter a name.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (method === "Enter layers") {
        const trimmedLayer = layerName.trim();
        if (!trimmedLayer) {
          setError("Please enter a layer name.");
          return;
        }
        const materials = rows.map((r) => r.material).filter((m) => m && m !== CREATE);
        if (materials.length === 0) {
          setError("Please select at least one material.");
          return;
        }
        const resistances = materials.map((m) => allMaterials[m].resistance);
        const { u_value } = await computeConstructionUValue({ resistances });
        const layer: LayerEntry = { user_name: trimmedLayer, materials, u_value };
        if (bi) {
          const target = kind === "Wall" ? "user_layers_wall" : "user_layers_roof";
          updateBi({ [target]: [...bi[target], layer] } as Partial<typeof bi>);
        }
        onSave({
          user_name: trimmed,
          type: "LAYERS",
          absorptance,
          roughness,
          layer_name: trimmedLayer,
          u_value,
        });
      } else {
        onSave({
          user_name: trimmed,
          type: "U-VALUE",
          absorptance,
          roughness,
          layer_name: "",
          u_value: uValueDirect,
        });
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <Modal title={`New Construction (${kind})`} onClose={onClose} width="max-w-2xl">
        <div className="flex flex-col gap-3">
          <FieldRow label="Name:">
            <TextInput value={name} onChange={(e) => setName(e.target.value)} autoFocus />
          </FieldRow>
          <FieldRow label="Method:">
            <SelectField value={method} onChange={setMethod} options={METHODS} />
          </FieldRow>
          <FieldRow label="Roughness:">
            <NumberInput value={roughness} onChange={(v) => setRoughness(v === null ? 4 : Math.round(v))} min={1} max={6} step="1" />
          </FieldRow>
          <FieldRow label="Absorptance:">
            <NumberInput value={absorptance} onChange={(v) => setAbsorptance(v ?? 0)} min={0} max={1} step="0.01" />
          </FieldRow>

          {method === "Enter layers" ? (
            <>
              <FieldRow label="Layer Name:">
                <TextInput value={layerName} onChange={(e) => setLayerName(e.target.value)} />
              </FieldRow>
              <div className="overflow-x-auto rounded-md border border-slate-200 dark:border-slate-700">
                <table className="w-full min-w-[640px] text-xs">
                  <thead className="bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                    <tr>
                      {["Material", "Thickness(m)", "Conductivity(W/m.K)", "Density(kg/m3)", "Specific Heat(J/kg.K)", "R Value(m2.K/W)"].map(
                        (h) => (
                          <th key={h} className="px-2 py-1.5 text-left font-medium">
                            {h}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row, i) => {
                      const mat = row.material ? allMaterials[row.material] : undefined;
                      return (
                        <tr key={i} className="border-t border-slate-100 dark:border-slate-800">
                          <td className="px-2 py-1">
                            <SelectField
                              value={row.material}
                              onChange={(v) => setRowMaterial(i, v)}
                              options={materialNames}
                              placeholder="Select…"
                              createOption={CREATE}
                              onCreate={() => setMaterialDialogRow(i)}
                            />
                          </td>
                          <td className="px-2 py-1 text-slate-600 dark:text-slate-300">{mat?.thickness ?? ""}</td>
                          <td className="px-2 py-1 text-slate-600 dark:text-slate-300">{mat?.conductivity ?? ""}</td>
                          <td className="px-2 py-1 text-slate-600 dark:text-slate-300">{mat?.density ?? ""}</td>
                          <td className="px-2 py-1 text-slate-600 dark:text-slate-300">{mat?.spec_heat ?? ""}</td>
                          <td className="px-2 py-1 text-slate-600 dark:text-slate-300">{mat ? mat.resistance : ""}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Calculated U: {calculatedU !== null ? calculatedU.toFixed(3) : "-"}
              </p>
            </>
          ) : (
            <FieldRow label="U-Value (W/m2.C):">
              <NumberInput value={uValueDirect} onChange={(v) => setUValueDirect(v ?? 0)} step="0.001" />
            </FieldRow>
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="mt-2 flex justify-end gap-2">
            <Button onClick={onClose}>Cancel</Button>
            <Button variant="primary" onClick={handleSave} disabled={saving}>
              {saving ? "Saving…" : "OK"}
            </Button>
          </div>
        </div>
      </Modal>

      {materialDialogRow !== null && (
        <MaterialDialog onClose={() => setMaterialDialogRow(null)} onSave={handleMaterialCreated} />
      )}
    </>
  );
}
