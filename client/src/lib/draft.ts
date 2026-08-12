/**
 * BuildingDraft lifecycle: a new project starts with every user-facing field blank (the web
 * client deliberately pre-fills nothing), an opened .tct arrives fully populated, and
 * finalizeDraft() gates every API call behind a completeness check.
 */

import { shapeVisibility } from "./constants";
import type { BuildingDraft, BuildingInput, WindowAllocationRow } from "./types";

export const EMPTY_WINDOW_ROW: WindowAllocationRow = {
  south_percent: 0,
  north_percent: 0,
  east_percent: 0,
  west_percent: 0,
  glass_type: "",
};

export function blankWindowRows(): WindowAllocationRow[] {
  return Array.from({ length: 5 }, () => ({ ...EMPTY_WINDOW_ROW }));
}

/** A loaded/saved BuildingInput is by definition complete, so it is a valid draft as-is. */
export function draftFromBuildingInput(bi: BuildingInput): BuildingDraft {
  return { ...bi };
}

/** Strip every pre-filled value from a server-fresh BuildingInput: the user enters their own. */
export function blankDraft(fresh: BuildingInput): BuildingDraft {
  return {
    ...fresh,
    txtBldgName: "",
    txtBldgAddress: "",
    cmbBldgType: "",
    cmbBldgLocation: "",
    txtBldgNumFloor: null,
    txtBldgCondArea: null,
    cmbBldgShape: "",
    txtLengX1: null,
    txtLengY1: null,
    txtLengX2: null,
    txtLengY2: null,
    txtLengX3: null,
    txtLengY3: null,
    txtBldgAzi: null,
    txtFloorHeight: null,
    txtFloorArea: null,
    cmbSouthWall: "",
    cmbNorthWall: "",
    cmbEastWall: "",
    cmbWestWall: "",
    cmbRoof: "",
    cmbFirstFloorContact: "",
    window_rows: blankWindowRows(),
    txtWinSouthOverhang: null,
    txtWinSouthFp: null,
    txtSkyltType: "",
    txtSkyltCvr: null,
    space_rows: [],
    cmbBldgSystem: "",
    cmbHotWaterSystem: "",
    txtHeatSetTemp: null,
    txtCoolSetTemp: null,
    txtCoolCOP: null,
    txtHeatEff: null,
  };
}

interface RequiredField {
  key: keyof BuildingDraft;
  label: string;
  tab: string;
}

const REQUIRED_TEXT: RequiredField[] = [
  { key: "txtBldgName", label: "Building name", tab: "General Information" },
  { key: "cmbBldgType", label: "Building type", tab: "General Information" },
  { key: "cmbBldgLocation", label: "Location", tab: "General Information" },
  { key: "cmbBldgShape", label: "Building shape", tab: "General Information" },
  { key: "cmbSouthWall", label: "South wall construction", tab: "Envelope" },
  { key: "cmbNorthWall", label: "North wall construction", tab: "Envelope" },
  { key: "cmbEastWall", label: "East wall construction", tab: "Envelope" },
  { key: "cmbWestWall", label: "West wall construction", tab: "Envelope" },
  { key: "cmbRoof", label: "Roof construction", tab: "Envelope" },
  { key: "cmbFirstFloorContact", label: "First floor exposure", tab: "Envelope" },
  { key: "txtSkyltType", label: "Skylight type", tab: "Windows" },
  { key: "cmbBldgSystem", label: "HVAC system", tab: "HVAC System" },
  { key: "cmbHotWaterSystem", label: "Hot water system", tab: "HVAC System" },
];

const REQUIRED_NUMBER: RequiredField[] = [
  { key: "txtBldgNumFloor", label: "Number of floors", tab: "General Information" },
  { key: "txtBldgCondArea", label: "Conditioned area (%)", tab: "General Information" },
  { key: "txtBldgAzi", label: "Orientation (deg)", tab: "General Information" },
  { key: "txtFloorHeight", label: "Floor height (m)", tab: "General Information" },
  { key: "txtHeatSetTemp", label: "Heating setpoint (°C)", tab: "HVAC System" },
  { key: "txtCoolSetTemp", label: "Cooling setpoint (°C)", tab: "HVAC System" },
  { key: "txtCoolCOP", label: "Cooling efficiency (COP)", tab: "HVAC System" },
  { key: "txtHeatEff", label: "Heating efficiency (%)", tab: "HVAC System" },
];

const DIM_LABELS: Record<string, RequiredField> = {
  x1: { key: "txtLengX1", label: "Dimension X1 (m)", tab: "General Information" },
  y1: { key: "txtLengY1", label: "Dimension Y1 (m)", tab: "General Information" },
  x2: { key: "txtLengX2", label: "Dimension X2 (m)", tab: "General Information" },
  y2: { key: "txtLengY2", label: "Dimension Y2 (m)", tab: "General Information" },
  x3: { key: "txtLengX3", label: "Dimension X3 (m)", tab: "General Information" },
  y3: { key: "txtLengY3", label: "Dimension Y3 (m)", tab: "General Information" },
};

/** The dimension inputs the current shape actually shows (mirrors GeneralTab's visibility). */
export function requiredDims(draft: BuildingDraft): RequiredField[] {
  if (!draft.cmbBldgShape) return [];
  const vis = shapeVisibility(draft.cmbBldgShape);
  const isPolygon = !["Rectangular", "L-Shape", "T-Shape", "U-Shape"].includes(draft.cmbBldgShape);
  const out: RequiredField[] = [];
  if (vis.x1y1 && !isPolygon) out.push(DIM_LABELS.x1);
  if (vis.x1y1) out.push(DIM_LABELS.y1);
  if (vis.x2y2) out.push(DIM_LABELS.x2, DIM_LABELS.y2);
  if (vis.x3) out.push(DIM_LABELS.x3);
  if (vis.y3) out.push(DIM_LABELS.y3);
  return out;
}

export interface FinalizeResult {
  bi: BuildingInput | null;
  /** Human-readable "Tab — Field" strings for everything still blank. */
  missing: string[];
}

/**
 * Loose conversion for helper calls (floor area, apply-type-defaults) that must not be blocked
 * by an incomplete form: blanks become 0 / stay "".
 */
export function coerceDraft(draft: BuildingDraft): BuildingInput {
  const out = { ...draft } as Record<string, unknown>;
  for (const [k, v] of Object.entries(out)) {
    if (v === null) out[k] = 0;
  }
  return out as unknown as BuildingInput;
}

const TAB_ORDER = ["General Information", "Envelope", "Windows", "Spaces", "HVAC System"];

/** Strict conversion used before Save / Run: reports every blank required field. */
export function finalizeDraft(draft: BuildingDraft): FinalizeResult {
  const blankFields: RequiredField[] = [];

  for (const f of REQUIRED_TEXT) {
    if (!(draft[f.key] as string)?.trim()) blankFields.push(f);
  }
  for (const f of [...REQUIRED_NUMBER, ...requiredDims(draft)]) {
    if (draft[f.key] === null) blankFields.push(f);
  }
  const missing = blankFields
    .sort((a, b) => TAB_ORDER.indexOf(a.tab) - TAB_ORDER.indexOf(b.tab))
    .map((f) => `${f.tab} — ${f.label}`);
  draft.window_rows.forEach((row, i) => {
    const hasArea =
      row.south_percent > 0 || row.north_percent > 0 || row.east_percent > 0 || row.west_percent > 0;
    if (hasArea && !row.glass_type) missing.push(`Windows — Glass type for row ${i + 1}`);
  });

  if (missing.length > 0) return { bi: null, missing };
  // Remaining blanks are the optional fields (overhang, projection factor, skylight coverage,
  // hidden shape dimensions, computed floor area) where empty legitimately means zero.
  return { bi: coerceDraft(draft), missing: [] };
}
