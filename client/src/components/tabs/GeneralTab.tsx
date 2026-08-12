"use client";

import { useEffect, useState } from "react";

import { FieldRow, NumberInput, Section, SelectField, TextInput } from "@/components/ui/Field";
import { applyTypeDefaults, computeFloorArea, imageUrl } from "@/lib/api";
import { POLYGON_SHAPES, SHAPES_10, SHAPE_IMAGE_FILES, shapeVisibility } from "@/lib/constants";
import { blankWindowRows, coerceDraft } from "@/lib/draft";
import { useDebouncedValue } from "@/lib/useDebouncedValue";
import { useBuildingInput } from "@/providers/BuildingInputProvider";
import { useReferenceData } from "@/providers/ReferenceDataProvider";

export function GeneralTab() {
  const ref = useReferenceData();
  const { bi, updateBi } = useBuildingInput();
  const [typeChanging, setTypeChanging] = useState(false);

  const vis0 = bi ? shapeVisibility(bi.cmbBldgShape) : null;
  const isPolygon0 = bi ? POLYGON_SHAPES.has(bi.cmbBldgShape) : false;

  // Only compute the floor area once the shape and every visible dimension have been entered.
  const dimsReady =
    !!bi &&
    !!bi.cmbBldgShape &&
    !!vis0 &&
    (!vis0.x1y1 || isPolygon0 || bi.txtLengX1 !== null) &&
    (!vis0.x1y1 || bi.txtLengY1 !== null) &&
    (!vis0.x2y2 || (bi.txtLengX2 !== null && bi.txtLengY2 !== null)) &&
    (!vis0.x3 || bi.txtLengX3 !== null) &&
    (!vis0.y3 || bi.txtLengY3 !== null);

  const dims = useDebouncedValue(
    bi && dimsReady
      ? {
          shape: bi.cmbBldgShape,
          x1: bi.txtLengX1 ?? 0,
          y1: bi.txtLengY1 ?? 0,
          x2: bi.txtLengX2 ?? 0,
          y2: bi.txtLengY2 ?? 0,
          x3: bi.txtLengX3 ?? 0,
          y3: bi.txtLengY3 ?? 0,
        }
      : null,
    250
  );

  useEffect(() => {
    if (!dims) return;
    let cancelled = false;
    computeFloorArea(dims)
      .then(({ floor_area }) => {
        if (!cancelled) updateBi({ txtFloorArea: floor_area });
      })
      .catch(() => {
        /* ignore transient calc errors while typing */
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dims]);

  if (!bi) return null;

  const vis = shapeVisibility(bi.cmbBldgShape);
  const isPolygon = POLYGON_SHAPES.has(bi.cmbBldgShape);
  const showX1 = vis.x1y1 && !isPolygon && !!bi.cmbBldgShape;

  async function handleTypeChange(newType: string) {
    if (!bi) return;
    setTypeChanging(true);
    try {
      // The server derives the code-mandated space conditions for the chosen category; the
      // user-facing inputs (window allocation, HVAC system) stay blank for the user to fill.
      const updated = await applyTypeDefaults(coerceDraft({ ...bi, cmbBldgType: newType }));
      updateBi({
        cmbBldgType: newType,
        space_rows: updated.space_rows,
        window_rows: blankWindowRows(),
        cmbBldgSystem: "",
      });
    } finally {
      setTypeChanging(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <Section title="General Project Information">
        <FieldRow label="Building Name:">
          <TextInput
            value={bi.txtBldgName}
            onChange={(e) => updateBi({ txtBldgName: e.target.value })}
            placeholder="e.g. Résidence El Yasmine"
            required
          />
        </FieldRow>
        <FieldRow label="Address:">
          <TextInput
            value={bi.txtBldgAddress}
            onChange={(e) => updateBi({ txtBldgAddress: e.target.value })}
            placeholder="Street, city"
          />
        </FieldRow>
      </Section>

      <Section title="Building Type">
        <FieldRow label="Type:">
          <SelectField
            value={bi.cmbBldgType}
            onChange={handleTypeChange}
            options={ref.bldg_types.map((t) => t.bldg_type)}
            placeholder="Select a building type…"
            disabled={typeChanging}
          />
        </FieldRow>
        <FieldRow label="Location:">
          <SelectField
            value={bi.cmbBldgLocation}
            onChange={(v) => updateBi({ cmbBldgLocation: v })}
            options={ref.bldg_locations}
            placeholder="Select a location…"
          />
        </FieldRow>
        <FieldRow label="Number of Floors:">
          <NumberInput
            value={bi.txtBldgNumFloor}
            onChange={(v) => updateBi({ txtBldgNumFloor: v === null ? null : Math.round(v) })}
            min={1}
            max={200}
            step="1"
          />
        </FieldRow>
        <FieldRow label="Conditioned Area (%):">
          <NumberInput
            value={bi.txtBldgCondArea}
            onChange={(v) => updateBi({ txtBldgCondArea: v })}
            min={0}
            max={100}
            step="0.1"
          />
        </FieldRow>
      </Section>

      <Section title="Building Shape">
        <div className="flex flex-wrap gap-6">
          <div className="flex min-w-[280px] flex-1 flex-col gap-3">
            <FieldRow label="Shape:">
              <SelectField
                value={bi.cmbBldgShape}
                onChange={(v) => updateBi({ cmbBldgShape: v })}
                options={[...SHAPES_10]}
                placeholder="Select a shape…"
              />
            </FieldRow>
            {showX1 && (
              <FieldRow label="X1 (m):">
                <NumberInput value={bi.txtLengX1} onChange={(v) => updateBi({ txtLengX1: v })} step="0.1" />
              </FieldRow>
            )}
            {vis.x1y1 && !!bi.cmbBldgShape && (
              <FieldRow label="Y1 (m):">
                <NumberInput value={bi.txtLengY1} onChange={(v) => updateBi({ txtLengY1: v })} step="0.1" />
              </FieldRow>
            )}
            {vis.x2y2 && (
              <>
                <FieldRow label="X2 (m):">
                  <NumberInput value={bi.txtLengX2} onChange={(v) => updateBi({ txtLengX2: v })} step="0.1" />
                </FieldRow>
                <FieldRow label="Y2 (m):">
                  <NumberInput value={bi.txtLengY2} onChange={(v) => updateBi({ txtLengY2: v })} step="0.1" />
                </FieldRow>
              </>
            )}
            {vis.x3 && (
              <FieldRow label="X3 (m):">
                <NumberInput value={bi.txtLengX3} onChange={(v) => updateBi({ txtLengX3: v })} step="0.1" />
              </FieldRow>
            )}
            {vis.y3 && (
              <FieldRow label="Y3 (m):">
                <NumberInput value={bi.txtLengY3} onChange={(v) => updateBi({ txtLengY3: v })} step="0.1" />
              </FieldRow>
            )}
            <FieldRow label="Floor Area (m2):">
              <TextInput
                value={bi.txtFloorArea === null ? "" : bi.txtFloorArea.toFixed(2)}
                placeholder="Computed from the dimensions"
                readOnly
                disabled
                className="font-mono"
              />
            </FieldRow>
            <FieldRow label="Orientation (deg):">
              <NumberInput
                value={bi.txtBldgAzi}
                onChange={(v) => updateBi({ txtBldgAzi: v })}
                min={0}
                max={360}
                step="1"
              />
            </FieldRow>
            <FieldRow label="Floor Height (m):">
              <NumberInput
                value={bi.txtFloorHeight}
                onChange={(v) => updateBi({ txtFloorHeight: v })}
                min={0}
                max={20}
                step="0.1"
              />
            </FieldRow>
          </div>
          <div className="flex w-64 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-50 p-2 dark:border-slate-700 dark:bg-slate-800">
            {bi.cmbBldgShape && SHAPE_IMAGE_FILES[bi.cmbBldgShape] ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={imageUrl(SHAPE_IMAGE_FILES[bi.cmbBldgShape])}
                alt={bi.cmbBldgShape}
                className="max-h-52 max-w-full object-contain"
              />
            ) : (
              <span className="px-4 text-center text-xs text-slate-400">
                Pick a shape to see its dimension diagram
              </span>
            )}
          </div>
        </div>
      </Section>
    </div>
  );
}
