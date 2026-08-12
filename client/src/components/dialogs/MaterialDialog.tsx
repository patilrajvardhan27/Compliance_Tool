"use client";

import { useState } from "react";

import { Button, FieldRow, NumberInput, SelectField, TextInput } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";
import { computeMaterialResistance } from "@/lib/api";
import type { MaterialEntry } from "@/lib/types";

const TYPES = ["Properties", "Resistance"];

export function MaterialDialog({
  onClose,
  onSave,
}: {
  onClose: () => void;
  onSave: (entry: MaterialEntry) => void;
}) {
  const [name, setName] = useState("");
  const [type, setType] = useState("Properties");
  const [thickness, setThickness] = useState(0);
  const [conductivity, setConductivity] = useState(0);
  const [density, setDensity] = useState(0);
  const [specHeat, setSpecHeat] = useState(0);
  const [rValue, setRValue] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Please enter a name.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (type === "Properties") {
        if (conductivity <= 0) {
          setError("Conductivity must be positive.");
          return;
        }
        const { resistance } = await computeMaterialResistance({ thickness, conductivity });
        onSave({
          user_name: trimmed,
          type: "PROPERTIES",
          thickness,
          conductivity,
          density,
          spec_heat: specHeat,
          resistance,
        });
      } else {
        onSave({
          user_name: trimmed,
          type: "RESISTANCE",
          thickness: null,
          conductivity: null,
          density: null,
          spec_heat: null,
          resistance: rValue,
        });
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal title="New Material" onClose={onClose} width="max-w-md">
      <div className="flex flex-col gap-3">
        <FieldRow label="Name:">
          <TextInput value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </FieldRow>
        <FieldRow label="Type:">
          <SelectField value={type} onChange={setType} options={TYPES} />
        </FieldRow>

        {type === "Properties" ? (
          <>
            <FieldRow label="Thickness (m):">
              <NumberInput value={thickness} onChange={(v) => setThickness(v ?? 0)} step="0.001" />
            </FieldRow>
            <FieldRow label="Conductivity (W/m.K):">
              <NumberInput value={conductivity} onChange={(v) => setConductivity(v ?? 0)} step="0.001" />
            </FieldRow>
            <FieldRow label="Density (kg/m3):">
              <NumberInput value={density} onChange={(v) => setDensity(v ?? 0)} step="1" />
            </FieldRow>
            <FieldRow label="Specific Heat (J/kg.K):">
              <NumberInput value={specHeat} onChange={(v) => setSpecHeat(v ?? 0)} step="1" />
            </FieldRow>
          </>
        ) : (
          <FieldRow label="R Value (m2.K/W):">
            <NumberInput value={rValue} onChange={(v) => setRValue(v ?? 0)} step="0.001" />
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
  );
}
