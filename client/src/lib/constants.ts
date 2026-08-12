/** Ported verbatim from tunbeec/ui/main_window.py's module-level constants. */

export const SHAPES_10 = [
  "Rectangular",
  "L-Shape",
  "T-Shape",
  "U-Shape",
  "Hexagon",
  "Octagon",
  "Decagon",
  "Dodecagon",
  "Hexadecagon",
  "Octadecagon",
] as const;

export const POLYGON_SHAPES: Set<string> = new Set(SHAPES_10.slice(4));

export interface ShapeFieldVisibility {
  x1y1: boolean;
  x2y2: boolean;
  x3: boolean;
  y3: boolean;
}

const BASE_VISIBILITY: Record<string, ShapeFieldVisibility> = {
  Rectangular: { x1y1: true, x2y2: false, x3: false, y3: false },
  "L-Shape": { x1y1: true, x2y2: true, x3: false, y3: false },
  "T-Shape": { x1y1: true, x2y2: true, x3: true, y3: false },
  "U-Shape": { x1y1: true, x2y2: true, x3: true, y3: true },
};

export const SHAPE_FIELD_VISIBILITY: Record<string, ShapeFieldVisibility> = { ...BASE_VISIBILITY };
for (const shape of POLYGON_SHAPES) {
  SHAPE_FIELD_VISIBILITY[shape] = { x1y1: true, x2y2: false, x3: false, y3: false };
}

export function shapeVisibility(shape: string): ShapeFieldVisibility {
  return SHAPE_FIELD_VISIBILITY[shape] ?? { x1y1: true, x2y2: false, x3: false, y3: false };
}

export const SHAPE_IMAGE_FILES: Record<string, string> = {
  Rectangular: "Rectangular.jpg",
  "L-Shape": "L-Shape.jpg",
  "T-Shape": "T-Shape.jpg",
  "U-Shape": "U-Shape.jpg",
  Hexagon: "Hexagon-Shape.jpg",
  Octagon: "Octagon-Shape.jpg",
  Decagon: "Decagon-Shape.jpg",
  Dodecagon: "Dodecagon-Shape.jpg",
  Hexadecagon: "Hexadecagon-Shape.jpg",
  Octadecagon: "Octadecagon-Shape.jpg",
};

export const HVAC_SYSTEM_IMAGE_FILES: Record<string, string> = {
  "Packaged Variable Air Volume System": "PackagedVAV.jpg",
  "Split System with Baseboard": "SplitSystem.jpg",
  "Residential System": "ResidentialSystem.jpg",
  "Fan Coil System": "FancoilSystem.jpg",
  "Central Variable Air Volume System": "VavSystem.jpg",
};

export const SHADING_IMAGE_FILE = "fp.jpg";

export const HOT_WATER_SYSTEMS = ["Tankless Electric DHW System", "Tank Gas-fired DHW System"];
export const SKYLIGHT_TYPES = ["None", "Flat", "Dome"];
export const FIRST_FLOOR_CONTACTS = ["Ground", "Conditioned Space", "Unconditioned Space"];

/** main_window.py's SYSTEM_ENABLEMENT-adjacent rule: Prescriptive is disabled for these categories. */
export const PRESCRIPTIVE_DISABLED_CATEGORIES = new Set(["Hotel", "Hospital"]);

/**
 * app_state.py's SYSTEM_ENABLEMENT: which entries of ReferenceData.bldg_systems a building
 * category may choose from (0-based indices). The web client filters the dropdown but leaves
 * the choice to the user instead of auto-selecting.
 */
export const SYSTEM_ENABLEMENT: Record<string, number[]> = {
  Villa: [0, 1, 3, 4],
  Apartment: [2, 3, 4],
  Hospital: [1, 2, 4],
  Hotel: [1, 2, 4],
  Office: [1, 2, 3],
};

export const REPORT_COLORS = {
  bannerBlue: "#2929d4",
  compliantGreen: "#1d8a2c",
  nonCompliantRed: "#d02020",
  complianceBarRed: "#e8635c",
  buildingBarBlue: "#3f51d8",
};
