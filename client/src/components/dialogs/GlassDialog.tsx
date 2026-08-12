"use client";

import { useState } from "react";

import { Button, FieldRow, NumberInput, TextInput } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";
import type { GlassEntry } from "@/lib/types";

export function GlassDialog({
  onClose,
  onSave,
}: {
  onClose: () => void;
  onSave: (entry: GlassEntry) => void;
}) {
  const [name, setName] = useState("");
  const [conduct, setConduct] = useState(0);
  const [sc, setSc] = useState(0);
  const [vt, setVt] = useState(0);
  const [error, setError] = useState<string | null>(null);

  function handleSave() {
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Please enter a name.");
      return;
    }
    onSave({
      user_name: trimmed,
      user_type: "GLASS_TYPE",
      type: "SHADING-COEF",
      glass_conduct: conduct,
      sc,
      vt,
    });
  }

  return (
    <Modal title="New Glass Type" onClose={onClose} width="max-w-md">
      <div className="flex flex-col gap-3">
        <FieldRow label="Name:">
          <TextInput value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </FieldRow>
        <FieldRow label="Conductance (W/m2.K):">
          <NumberInput value={conduct} onChange={(v) => setConduct(v ?? 0)} step="0.0001" />
        </FieldRow>
        <FieldRow label="Shading Coefficient (SC):">
          <NumberInput value={sc} onChange={(v) => setSc(v ?? 0)} step="0.001" min={0} max={1} />
        </FieldRow>
        <FieldRow label="Visible Transmittance (VT):">
          <NumberInput value={vt} onChange={(v) => setVt(v ?? 0)} step="0.001" min={0} max={1} />
        </FieldRow>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="mt-2 flex justify-end gap-2">
          <Button onClick={onClose}>Cancel</Button>
          <Button variant="primary" onClick={handleSave}>
            OK
          </Button>
        </div>
      </div>
    </Modal>
  );
}
