import type {
  BuildingInput,
  PerformanceRunResponse,
  PrescriptiveResult,
  ReferenceSnapshot,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://localhost:8000";

export function imageUrl(filename: string): string {
  return `${API_BASE}/static/images/${filename}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore body parse errors
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}

// -- reference -------------------------------------------------------------------------------
export const getReference = () => request<ReferenceSnapshot>("/api/reference");

// -- building ---------------------------------------------------------------------------------
export const createNewBuilding = () => post<BuildingInput>("/api/building/new", {});

export const applyTypeDefaults = (building_input: BuildingInput) =>
  post<BuildingInput>("/api/building/apply-type-defaults", building_input);

export const computeFloorArea = (req: {
  shape: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  x3: number;
  y3: number;
}) => post<{ floor_area: number }>("/api/building/floor-area", req);

export const computeMaterialResistance = (req: { thickness: number; conductivity: number }) =>
  post<{ resistance: number }>("/api/building/material-resistance", req);

export const computeConstructionUValue = (req: { resistances: number[] }) =>
  post<{ u_value: number }>("/api/building/construction-uvalue", req);

// -- compliance -------------------------------------------------------------------------------
export const runPrescriptive = (building_input: BuildingInput) =>
  post<PrescriptiveResult>("/api/compliance/prescriptive", building_input);

export const runPerformance = (project_name: string, building_input: BuildingInput) =>
  post<PerformanceRunResponse>("/api/compliance/performance", { project_name, building_input });

// -- projects (local .tct files: the server only converts between JSON and file bytes) --------
export async function serializeProject(name: string, building_input: BuildingInput): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/projects/serialize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, building_input }),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      // ignore body parse errors
    }
    throw new Error(detail);
  }
  return res.blob();
}

export const parseProjectFile = (file: Blob) =>
  request<BuildingInput>("/api/projects/parse", {
    method: "POST",
    headers: { "Content-Type": "application/octet-stream" },
    body: file,
  });
