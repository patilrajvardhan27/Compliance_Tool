/**
 * TypeScript mirrors of python_tunbeec/api/schemas.py. Field names match the Python side
 * verbatim (txtBldgName, cmbBldgType, window_rows, ...) so the wire format needs no
 * renaming/remapping on either end.
 */

export interface WindowAllocationRow {
  south_percent: number;
  north_percent: number;
  east_percent: number;
  west_percent: number;
  glass_type: string;
}

export interface SpaceConditionRow {
  area_type: string;
  percent_area: number;
  occupant: number;
  infiltration: number;
  lighting: number;
  plug_load: number;
  conditioned: boolean;
}

export interface MaterialEntry {
  user_name: string;
  type: "PROPERTIES" | "RESISTANCE";
  thickness: number | null;
  conductivity: number | null;
  density: number | null;
  spec_heat: number | null;
  resistance: number;
}

export interface LayerEntry {
  user_name: string;
  materials: string[];
  u_value: number;
}

export interface ConstructionEntry {
  user_name: string;
  type: "LAYERS" | "U-VALUE";
  absorptance: number;
  roughness: number;
  layer_name: string;
  u_value: number;
}

export interface GlassEntry {
  user_name: string;
  user_type: string;
  type: string;
  glass_conduct: number;
  sc: number;
  vt: number;
}

export interface BuildingInput {
  // Tab 1 - General Information
  txtBldgName: string;
  txtBldgAddress: string;
  cmbBldgType: string;
  cmbBldgLocation: string;
  txtBldgNumFloor: number;
  txtBldgCondArea: number;
  cmbBldgShape: string;
  txtLengX1: number;
  txtLengY1: number;
  txtLengX2: number;
  txtLengY2: number;
  txtLengX3: number;
  txtLengY3: number;
  txtBldgAzi: number;
  txtFloorHeight: number;
  txtFloorArea: number;

  // Tab 2 - Envelope
  cmbSouthWall: string;
  cmbNorthWall: string;
  cmbEastWall: string;
  cmbWestWall: string;
  cmbRoof: string;
  cmbFirstFloorContact: string;
  rdbtnWinWwr: boolean;
  window_rows: WindowAllocationRow[];
  txtWinSouthOverhang: number;
  txtWinSouthFp: number;
  txtSkyltType: string;
  txtSkyltCvr: number;

  // Tab 3 - Spaces
  space_rows: SpaceConditionRow[];

  // Tab 4 - HVAC System
  cmbBldgSystem: string;
  txtHeatSetTemp: number;
  txtCoolSetTemp: number;
  txtCoolCOP: number;
  txtHeatEff: number;
  cmbHotWaterSystem: string;

  // User-defined library entries
  user_constructions_wall: ConstructionEntry[];
  user_constructions_roof: ConstructionEntry[];
  user_layers_wall: LayerEntry[];
  user_layers_roof: LayerEntry[];
  user_materials: MaterialEntry[];
  user_glass: GlassEntry[];
}

/**
 * What the form actually edits: every top-level numeric field may be null, meaning the user has
 * not entered a value yet (rendered as an empty input, never a silent default). Converted to a
 * complete BuildingInput by finalizeDraft() before anything is sent to the API.
 */
export type BuildingDraft = {
  [K in keyof BuildingInput]: BuildingInput[K] extends number ? number | null : BuildingInput[K];
};

export interface BldgType {
  bldg_type: string;
  cat: string;
  use: string;
  sector: string;
  star: string;
}

export interface ReferenceSnapshot {
  bldg_types: BldgType[];
  bldg_locations: string[];
  bldg_shapes: Record<string, string>;
  bldg_systems: string[];
  gui_defaults: Record<string, string>;
  constructions_wall: Record<string, ConstructionEntry>;
  constructions_roof: Record<string, ConstructionEntry>;
  layers_wall: Record<string, LayerEntry>;
  layers_roof: Record<string, LayerEntry>;
  materials: Record<string, MaterialEntry>;
  glass: Record<string, GlassEntry>;
}

export interface EnvelopeResultRow {
  item: string;
  unit: string;
  comp_value_1: number;
  comp_value_2: number;
  bldg_value: number;
  compliant: boolean;
}

export interface PrescriptiveResult {
  climate: number;
  bldg_zone: string;
  x1: number;
  x2: number;
  grade: string;
  code_thresholds: number[][];
  ext_wall_u: number;
  roof_u: number;
  glass_weighted_u: number;
  glass_weighted_sc: number;
  rows: EnvelopeResultRow[];
  compliant: boolean;
  needs_performance_path: boolean;
  report_variant: number;
}

export interface ClassRow {
  class_name: string;
  class_value: number;
  class_bldg: string;
}

export interface PerformanceReport {
  bldg_name: string;
  bldg_address: string;
  bldg_type: string;
  bldg_category: string;
  bldg_sector: string;
  bldg_star: string;
  bldg_loc: string;

  ext_wall_const_u: number;
  ext_wall_const_south_u: number;
  ext_wall_const_north_u: number;
  ext_wall_const_east_u: number;
  ext_wall_const_west_u: number;
  roof_const_u: number;
  glass_u: Record<string, number>;
  glass_sc: Record<string, number>;

  min_bec_th: number;
  bldg_bec_th: number;
  min_class: string;
  bldg_class: string;
  result: string;

  h_load: number;
  c_load: number;
  a_load: number;
  h_energy: number;
  c_energy: number;
  a_energy: number;
  a_src_energy: number;
  a_co2: number;

  class_rows: ClassRow[];
}

export interface PerformanceRunResponse {
  status: "ok" | "simulation_unavailable" | "simulation_failed";
  message: string;
  inp_path: string | null;
  report: PerformanceReport | null;
}

export interface ProjectSummary {
  name: string;
  modified: string;
}
