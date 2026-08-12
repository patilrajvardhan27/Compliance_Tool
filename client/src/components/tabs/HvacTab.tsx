"use client";

import { FieldRow, NumberInput, Section, SelectField } from "@/components/ui/Field";
import { imageUrl } from "@/lib/api";
import { HOT_WATER_SYSTEMS, HVAC_SYSTEM_IMAGE_FILES, SYSTEM_ENABLEMENT } from "@/lib/constants";
import { useBuildingInput } from "@/providers/BuildingInputProvider";
import { useReferenceData } from "@/providers/ReferenceDataProvider";

export function HvacTab() {
  const ref = useReferenceData();
  const { bi, updateBi } = useBuildingInput();
  if (!bi) return null;

  // Offer only the systems the code allows for the selected building category; the choice
  // itself is the user's (nothing is pre-selected).
  const typeRow = ref.bldg_types.find((t) => t.bldg_type === bi.cmbBldgType);
  const allowedIdx = typeRow ? SYSTEM_ENABLEMENT[typeRow.cat] : undefined;
  const systemOptions = allowedIdx
    ? allowedIdx.filter((i) => i < ref.bldg_systems.length).map((i) => ref.bldg_systems[i])
    : ref.bldg_systems;

  const illustration = HVAC_SYSTEM_IMAGE_FILES[bi.cmbBldgSystem];

  return (
    <div className="flex flex-col gap-4">
      <Section
        title="System"
        hint={
          typeRow
            ? `Systems available for ${typeRow.cat} buildings.`
            : "Select a building type on the General Information tab to filter the available systems."
        }
      >
        <div className="flex flex-wrap gap-6">
          <div className="flex min-w-[280px] flex-1 flex-col gap-3">
            <FieldRow label="HVAC System:">
              <SelectField
                value={bi.cmbBldgSystem}
                onChange={(v) => updateBi({ cmbBldgSystem: v })}
                options={systemOptions}
                placeholder="Select an HVAC system…"
              />
            </FieldRow>
            <FieldRow label="Heating Setpoint (°C):">
              <NumberInput
                value={bi.txtHeatSetTemp}
                onChange={(v) => updateBi({ txtHeatSetTemp: v })}
                step="0.1"
                max={40}
              />
            </FieldRow>
            <FieldRow label="Cooling Setpoint (°C):">
              <NumberInput
                value={bi.txtCoolSetTemp}
                onChange={(v) => updateBi({ txtCoolSetTemp: v })}
                step="0.1"
                max={40}
              />
            </FieldRow>
          </div>
          <div className="flex w-72 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-50 p-2 dark:border-slate-700 dark:bg-slate-800">
            {illustration ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={imageUrl(illustration)}
                alt={bi.cmbBldgSystem}
                className="max-h-48 max-w-full object-contain"
              />
            ) : (
              <span className="px-4 text-center text-xs text-slate-400">
                Pick a system to see its schematic
              </span>
            )}
          </div>
        </div>
      </Section>

      <Section
        title="Energy Efficiency"
        hint="Enter the equipment's rated values. Heating efficiency above 100% represents a heat pump."
      >
        <FieldRow label="Cooling Efficiency — COP:">
          <NumberInput
            value={bi.txtCoolCOP}
            onChange={(v) => updateBi({ txtCoolCOP: v })}
            step="0.1"
            min={0.5}
            max={10}
          />
        </FieldRow>
        <FieldRow label="Heating Efficiency (%):">
          <NumberInput
            value={bi.txtHeatEff}
            onChange={(v) => updateBi({ txtHeatEff: v })}
            step="1"
            min={10}
            max={500}
          />
        </FieldRow>
      </Section>

      <Section title="Domestic Hot Water">
        <FieldRow label="System:">
          <SelectField
            value={bi.cmbHotWaterSystem}
            onChange={(v) => updateBi({ cmbHotWaterSystem: v })}
            options={HOT_WATER_SYSTEMS}
            placeholder="Select a hot water system…"
          />
        </FieldRow>
      </Section>
    </div>
  );
}
