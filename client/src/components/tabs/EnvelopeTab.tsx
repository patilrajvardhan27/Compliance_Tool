"use client";

import { useMemo, useState } from "react";

import { ConstructionDialog } from "@/components/dialogs/ConstructionDialog";
import { Button, FieldRow, Section, SelectField } from "@/components/ui/Field";
import { FIRST_FLOOR_CONTACTS } from "@/lib/constants";
import type { ConstructionEntry } from "@/lib/types";
import { useBuildingInput } from "@/providers/BuildingInputProvider";
import { useReferenceData } from "@/providers/ReferenceDataProvider";

const CREATE = "-Create-";

export function EnvelopeTab() {
  const ref = useReferenceData();
  const { bi, updateBi } = useBuildingInput();
  const [dialogKind, setDialogKind] = useState<"Wall" | "Roof" | null>(null);

  const wallNames = useMemo(() => {
    const names = new Set(Object.keys(ref.constructions_wall));
    for (const c of bi?.user_constructions_wall ?? []) names.add(c.user_name);
    return Array.from(names);
  }, [ref.constructions_wall, bi?.user_constructions_wall]);

  const roofNames = useMemo(() => {
    const names = new Set(Object.keys(ref.constructions_roof));
    for (const c of bi?.user_constructions_roof ?? []) names.add(c.user_name);
    return Array.from(names);
  }, [ref.constructions_roof, bi?.user_constructions_roof]);

  if (!bi) return null;

  function handleConstructionSaved(entry: ConstructionEntry) {
    if (dialogKind === "Wall") {
      updateBi({
        user_constructions_wall: [...bi!.user_constructions_wall, entry],
        cmbSouthWall: entry.user_name,
        cmbNorthWall: entry.user_name,
        cmbEastWall: entry.user_name,
        cmbWestWall: entry.user_name,
      });
    } else if (dialogKind === "Roof") {
      updateBi({ user_constructions_roof: [...bi!.user_constructions_roof, entry], cmbRoof: entry.user_name });
    }
    setDialogKind(null);
  }

  const wallRow = (label: string, value: string, onChange: (v: string) => void) => (
    <FieldRow label={label}>
      <div className="flex gap-2">
        <SelectField
          value={value}
          onChange={onChange}
          options={wallNames}
          placeholder="Select a construction…"
          createOption={CREATE}
          onCreate={() => setDialogKind("Wall")}
        />
        <Button onClick={() => setDialogKind("Wall")}>Edit</Button>
      </div>
    </FieldRow>
  );

  return (
    <div className="flex flex-col gap-4">
      <Section title="Building Envelope Constructions">
        {wallRow("South Wall:", bi.cmbSouthWall, (v) => updateBi({ cmbSouthWall: v }))}
        {wallRow("North Wall:", bi.cmbNorthWall, (v) => updateBi({ cmbNorthWall: v }))}
        {wallRow("East Wall:", bi.cmbEastWall, (v) => updateBi({ cmbEastWall: v }))}
        {wallRow("West Wall:", bi.cmbWestWall, (v) => updateBi({ cmbWestWall: v }))}
        <FieldRow label="Roof:">
          <div className="flex gap-2">
            <SelectField
              value={bi.cmbRoof}
              onChange={(v) => updateBi({ cmbRoof: v })}
              options={roofNames}
              placeholder="Select a construction…"
              createOption={CREATE}
              onCreate={() => setDialogKind("Roof")}
            />
            <Button onClick={() => setDialogKind("Roof")}>Edit</Button>
          </div>
        </FieldRow>
        <FieldRow label="First Floor Exposure:">
          <SelectField
            value={bi.cmbFirstFloorContact}
            onChange={(v) => updateBi({ cmbFirstFloorContact: v })}
            options={FIRST_FLOOR_CONTACTS}
            placeholder="Select the first floor exposure…"
          />
        </FieldRow>
      </Section>

      {dialogKind && (
        <ConstructionDialog kind={dialogKind} onClose={() => setDialogKind(null)} onSave={handleConstructionSaved} />
      )}
    </div>
  );
}
