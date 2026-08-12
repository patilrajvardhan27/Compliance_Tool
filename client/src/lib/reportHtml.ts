/**
 * Standalone, printable HTML files for the two compliance reports, saved to the user's machine
 * from the result dialogs. Self-contained (inline CSS + SVG chart) so the file opens anywhere.
 */

import { REPORT_COLORS } from "./constants";
import type { ClassRow, PerformanceReport, PrescriptiveResult } from "./types";

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function page(title: string, body: string): string {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<style>
  :root { color-scheme: light; }
  body { font-family: "Segoe UI", system-ui, -apple-system, sans-serif; color: #1b2733; margin: 0;
         background: #f4f5f4; }
  .sheet { max-width: 760px; margin: 24px auto; background: #fff; padding: 40px 48px;
           box-shadow: 0 1px 8px rgba(27,39,51,.12); }
  h1 { font-size: 20px; text-align: center; margin: 0 0 4px; letter-spacing: .02em; }
  .stamp { text-align: center; font-size: 11px; color: #68737d; margin-bottom: 24px; }
  .banner { background: ${REPORT_COLORS.bannerBlue}; color: #fff; font-size: 13px; font-weight: 600;
            padding: 6px 12px; border-radius: 4px; margin: 20px 0 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 6px 10px; text-align: left; border-bottom: 1px solid #e6e8ea; }
  th { background: #f0f2f4; font-weight: 600; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
  .kv { display: grid; grid-template-columns: max-content 1fr; gap: 4px 24px; font-size: 13px; }
  .kv b { font-weight: 600; color: #47525c; }
  .ok { color: ${REPORT_COLORS.compliantGreen}; font-weight: 700; }
  .bad { color: ${REPORT_COLORS.nonCompliantRed}; font-weight: 700; }
  .verdict { border-radius: 4px; color: #fff; font-weight: 700; text-align: center;
             padding: 10px; font-size: 14px; margin-top: 16px; }
  @media print { body { background: #fff; } .sheet { box-shadow: none; margin: 0; max-width: none; } }
</style>
</head>
<body><div class="sheet">${body}</div></body>
</html>`;
}

const stamp = () => `<p class="stamp">TUNBEEC — Tunisian Building Energy Efficiency Code · Generated ${new Date().toLocaleString()}</p>`;

const kv = (rows: [string, string][]) =>
  `<div class="kv">${rows.map(([k, v]) => `<b>${esc(k)}</b><span>${esc(v)}</span>`).join("")}</div>`;

export function prescriptiveReportHtml(result: PrescriptiveResult, bldgName: string): string {
  let envelope: string;
  if (result.needs_performance_path) {
    envelope = `<p class="bad" style="text-align:center;padding:16px 0">
      The glazing ratio exceeds the range covered by the prescriptive approach.<br>
      Use the Performance Approach for this building.</p>`;
  } else {
    envelope = `<table>
      <thead><tr><th>Element</th><th class="num">Building Value</th><th class="num">Limit Value</th><th>Result</th></tr></thead>
      <tbody>${result.rows
        .map(
          (r) => `<tr><td>${esc(r.item)} ${esc(r.unit)}</td><td class="num">${r.bldg_value.toFixed(3)}</td>
            <td class="num">${r.comp_value_1.toFixed(3)}</td>
            <td class="${r.compliant ? "ok" : "bad"}">${r.compliant ? "Compliant" : "Non-Compliant"}</td></tr>`
        )
        .join("")}</tbody></table>
      <div class="verdict" style="background:${result.compliant ? REPORT_COLORS.compliantGreen : REPORT_COLORS.nonCompliantRed}">
        Overall Result: ${result.compliant ? "Compliant" : "Non-Compliant"}</div>`;
  }

  const body = `
    <h1>Prescriptive Compliance Report</h1>
    ${stamp()}
    ${kv([["Building:", bldgName]])}
    <div class="banner">Building Glazing</div>
    ${kv([
      ["Climate Zone:", result.bldg_zone],
      ["Glazing Level:", result.grade],
      ["X1 (glazing / total wall):", `${result.x1.toFixed(1)} %`],
      ["X2 (glazing / east+west wall):", `${result.x2.toFixed(1)} %`],
    ])}
    <div class="banner">Envelope Requirements</div>
    ${envelope}`;
  return page(`Prescriptive Report — ${bldgName}`, body);
}

function classChartSvg(classRows: ClassRow[], bldgBecTh: number): string {
  const width = 640;
  const rowH = 34;
  const labelW = 70;
  const height = classRows.length * rowH + 30;
  const maxVal = Math.max(...classRows.map((r) => r.class_value), bldgBecTh, 1) * 1.15;
  const scale = (v: number) => ((width - labelW - 60) * v) / maxVal;

  const bars = classRows
    .map((row, i) => {
      const y = i * rowH + 10;
      const bldg = row.class_bldg ? Number(row.class_bldg) : null;
      const threshold = `<rect x="${labelW}" y="${y}" width="${scale(row.class_value).toFixed(1)}" height="11" rx="2" fill="${REPORT_COLORS.complianceBarRed}"/>
        <text x="${(labelW + scale(row.class_value) + 4).toFixed(1)}" y="${y + 9}" font-size="9" fill="#68737d">${row.class_value.toFixed(1)}</text>`;
      const building =
        bldg !== null
          ? `<rect x="${labelW}" y="${y + 13}" width="${scale(bldg).toFixed(1)}" height="11" rx="2" fill="${REPORT_COLORS.buildingBarBlue}"/>
             <text x="${(labelW + scale(bldg) + 4).toFixed(1)}" y="${y + 22}" font-size="9" fill="#68737d">${bldg.toFixed(1)}</text>`
          : "";
      return `<text x="${labelW - 8}" y="${y + 14}" font-size="11" text-anchor="end" fill="#47525c">${esc(row.class_name)}</text>${threshold}${building}`;
    })
    .join("\n");

  const legendY = classRows.length * rowH + 18;
  return `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">
    ${bars}
    <rect x="${labelW}" y="${legendY - 9}" width="10" height="10" fill="${REPORT_COLORS.complianceBarRed}"/>
    <text x="${labelW + 14}" y="${legendY}" font-size="10" fill="#47525c">Compliance threshold</text>
    <rect x="${labelW + 150}" y="${legendY - 9}" width="10" height="10" fill="${REPORT_COLORS.buildingBarBlue}"/>
    <text x="${labelW + 164}" y="${legendY}" font-size="10" fill="#47525c">Building</text>
  </svg>`;
}

export function performanceReportHtml(report: PerformanceReport): string {
  const glassRows: [string, string][] = Object.keys(report.glass_u)
    .sort((a, b) => Number(a) - Number(b))
    .map((idx) => [
      `Glass ${idx} U / SC:`,
      `${report.glass_u[idx].toFixed(2)} [W/m2.K]  /  ${(report.glass_sc[idx] ?? 0).toFixed(2)}`,
    ]);

  const body = `
    <h1>Performance Compliance Report</h1>
    ${stamp()}
    <div class="banner">Building Information</div>
    ${kv([
      ["NAME:", report.bldg_name],
      ["LOCATION:", report.bldg_loc],
      ["TYPE:", report.bldg_type],
      ["SECTOR:", report.bldg_sector],
      ["CATEGORY:", report.bldg_category],
      ["HOTEL GRADE:", report.bldg_star || "-"],
      ["ADDRESS:", report.bldg_address],
    ])}
    <div class="banner">Construction Information</div>
    ${kv([
      ["Wall U-Value:", `${report.ext_wall_const_u.toFixed(2)} [W/m2.K]`],
      ["South U:", `${report.ext_wall_const_south_u.toFixed(2)} [W/m2.K]`],
      ["North U:", `${report.ext_wall_const_north_u.toFixed(2)} [W/m2.K]`],
      ["East U:", `${report.ext_wall_const_east_u.toFixed(2)} [W/m2.K]`],
      ["West U:", `${report.ext_wall_const_west_u.toFixed(2)} [W/m2.K]`],
      ["Roof U-Value:", `${report.roof_const_u.toFixed(2)} [W/m2.K]`],
      ...glassRows,
    ])}
    <div class="banner">Performance Analysis</div>
    <table>
      <thead><tr><th></th><th class="num">Compliance</th><th class="num">Building</th></tr></thead>
      <tbody>
        <tr><td>Thermal loads (BECth) for conditioned space [kWh/m2.year]</td>
            <td class="num">${report.min_bec_th.toFixed(1)}</td><td class="num">${report.bldg_bec_th.toFixed(1)}</td></tr>
        <tr><td><b>CLASS</b></td><td class="num">${esc(report.min_class)}</td><td class="num">${esc(report.bldg_class)}</td></tr>
      </tbody>
    </table>
    <div class="verdict" style="background:${report.result === "Compliant" ? REPORT_COLORS.compliantGreen : REPORT_COLORS.nonCompliantRed}">
      Performance Compliance Result: ${esc(report.result)}</div>
    <div class="banner">Annual Loads / Energy / Emissions</div>
    ${kv([
      ["Annual Thermal Load", "[kWh/m2.year]"],
      ["Heating:", report.h_load.toFixed(1)],
      ["Cooling:", report.c_load.toFixed(1)],
      ["Annual:", report.a_load.toFixed(1)],
      ["Annual Site Energy", "[kWh/m2.year]"],
      ["Electricity:", report.c_energy.toFixed(1)],
      ["Gas:", report.h_energy.toFixed(1)],
      ["Annual:", report.a_energy.toFixed(1)],
      ["Annual Source Energy [kWh/m2.year]:", report.a_src_energy.toFixed(1)],
      ["Annual CO2 Emission [kg/m2.year]:", report.a_co2.toFixed(1)],
    ])}
    <div class="banner">BECth by Class [kWh/m2.year]</div>
    ${classChartSvg(report.class_rows, report.bldg_bec_th)}`;
  return page(`Performance Report — ${report.bldg_name}`, body);
}
