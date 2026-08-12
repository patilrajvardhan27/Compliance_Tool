"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";
import { REPORT_COLORS } from "@/lib/constants";
import { HTML_TYPE, saveLocalFile } from "@/lib/localFile";
import { performanceReportHtml } from "@/lib/reportHtml";
import type { PerformanceReport } from "@/lib/types";

import { BecThChart } from "./BecThChart";
import { Banner, InfoGrid, TitleHeader } from "./ReportBanner";

export function PerformanceReportModal({
  report,
  onClose,
}: {
  report: PerformanceReport;
  onClose: () => void;
}) {
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  async function handleSaveReport() {
    try {
      const html = performanceReportHtml(report);
      const saved = await saveLocalFile(
        new Blob([html], { type: "text/html" }),
        `${report.bldg_name || "Building"} - Performance Report.html`,
        HTML_TYPE
      );
      if (saved) {
        setSaveMessage(
          saved.handle ? `Saved "${saved.fileName}".` : `"${saved.fileName}" downloaded to your computer.`
        );
      }
    } catch (e) {
      setSaveMessage(`Save failed: ${(e as Error).message}`);
    }
  }
  const glassRows: [string, string][] = Object.keys(report.glass_u)
    .sort((a, b) => Number(a) - Number(b))
    .map((idx) => [
      `Glass ${idx} U / SC:`,
      `${report.glass_u[idx].toFixed(2)} [W/m2.K]  /  ${(report.glass_sc[idx] ?? 0).toFixed(2)}`,
    ]);

  return (
    <Modal title="Performance Compliance Report" onClose={onClose} width="max-w-3xl">
      <div className="flex flex-col gap-4">
        <TitleHeader>Performance Compliance Report</TitleHeader>

        <Banner>Building Information</Banner>
        <InfoGrid
          rows={[
            ["NAME:", report.bldg_name],
            ["LOCATION:", report.bldg_loc],
            ["TYPE:", report.bldg_type],
            ["SECTOR:", report.bldg_sector],
            ["CATEGORY:", report.bldg_category],
            ["HOTEL GRADE:", report.bldg_star || "-"],
            ["ADDRESS:", report.bldg_address],
          ]}
        />

        <Banner>Construction Information</Banner>
        <InfoGrid
          rows={[
            ["Wall U-Value:", `${report.ext_wall_const_u.toFixed(2)}  [W/m2.K]`],
            ["South U:", `${report.ext_wall_const_south_u.toFixed(2)}  [W/m2.K]`],
            ["North U:", `${report.ext_wall_const_north_u.toFixed(2)}  [W/m2.K]`],
            ["East U:", `${report.ext_wall_const_east_u.toFixed(2)}  [W/m2.K]`],
            ["West U:", `${report.ext_wall_const_west_u.toFixed(2)}  [W/m2.K]`],
            ["Roof U-Value:", `${report.roof_const_u.toFixed(2)}  [W/m2.K]`],
            ...glassRows,
          ]}
        />

        <Banner>Performance Analysis</Banner>
        <div className="overflow-x-auto rounded-md border border-slate-200 dark:border-slate-700">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-600 dark:text-slate-300">
                <th className="px-3 py-2 text-left font-semibold" />
                <th className="px-3 py-2 text-center font-semibold">Compliance</th>
                <th className="px-3 py-2 text-center font-semibold">Building</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-slate-100 dark:border-slate-800">
                <td className="px-3 py-2">Thermal loads (BECth) for conditioned space [kWh/m2.year]</td>
                <td className="px-3 py-2 text-center">{report.min_bec_th.toFixed(1)}</td>
                <td className="px-3 py-2 text-center">{report.bldg_bec_th.toFixed(1)}</td>
              </tr>
              <tr className="border-t border-slate-100 dark:border-slate-800">
                <td className="px-3 py-2 font-semibold">CLASS</td>
                <td className="px-3 py-2 text-center">{report.min_class}</td>
                <td className="px-3 py-2 text-center">{report.bldg_class}</td>
              </tr>
              <tr className="border-t border-slate-100 dark:border-slate-800">
                <td
                  className="px-3 py-2 font-bold"
                  style={{ color: REPORT_COLORS.nonCompliantRed }}
                >
                  Performance Compliance Result
                </td>
                <td className="px-3 py-2" />
                <td
                  className="px-3 py-2 text-center font-bold"
                  style={{
                    color:
                      report.result === "Compliant"
                        ? REPORT_COLORS.compliantGreen
                        : REPORT_COLORS.nonCompliantRed,
                  }}
                >
                  {report.result}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <Banner>Annual Loads / Energy / Emissions</Banner>
        <InfoGrid
          rows={[
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
          ]}
        />

        <BecThChart classRows={report.class_rows} bldgBecTh={report.bldg_bec_th} />

        <div className="mt-1 flex items-center justify-end gap-3 border-t border-slate-200 pt-3 dark:border-slate-700">
          {saveMessage && <span className="text-xs text-slate-500 dark:text-slate-400">{saveMessage}</span>}
          <Button onClick={onClose}>Close</Button>
          <Button variant="primary" onClick={handleSaveReport}>
            Save report to my computer
          </Button>
        </div>
      </div>
    </Modal>
  );
}
