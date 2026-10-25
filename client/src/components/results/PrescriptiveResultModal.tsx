"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";
import { REPORT_COLORS } from "@/lib/constants";
import { HTML_TYPE, saveLocalFile } from "@/lib/localFile";
import { prescriptiveReportHtml } from "@/lib/reportHtml";
import type { PrescriptiveResult } from "@/lib/types";

import { Banner, InfoGrid, TitleHeader, VerdictBanner } from "./ReportBanner";

export function PrescriptiveResultModal({
  result,
  bldgName,
  onClose,
}: {
  result: PrescriptiveResult;
  bldgName: string;
  onClose: () => void;
}) {
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  async function handleSaveReport() {
    try {
      const html = prescriptiveReportHtml(result, bldgName);
      const saved = await saveLocalFile(
        new Blob([html], { type: "text/html" }),
        `${bldgName} - Prescriptive Report.html`,
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

  return (
    <Modal title="Result - Prescriptive Approach" onClose={onClose} width="max-w-2xl">
      <div className="flex flex-col gap-4">
        <TitleHeader>Prescriptive Compliance Report</TitleHeader>

        <Banner>Building Glazing</Banner>
        <InfoGrid
          rows={[
            ["Climate Zone:", result.bldg_zone],
            ["Glazing Level:", result.grade],
            ["X1 (glazing / total wall):", `${result.x1.toFixed(1)} %`],
            ["X2 (glazing / east+west wall):", `${result.x2.toFixed(1)} %`],
          ]}
        />

        <Banner>Envelope Requirements</Banner>
        {result.needs_performance_path ? (
          <p
            className="animate-scale-in rounded-chip bg-mist p-4 text-center text-[17px] font-semibold"
            style={{ color: REPORT_COLORS.nonCompliant }}
          >
            The glazing ratio exceeds the range covered by the prescriptive approach.
            <br />
            Use the Performance Approach for this building.
          </p>
        ) : (
          <>
            <div className="overflow-x-auto rounded-chip border border-hairline">
              <table className="nums w-full text-[14px]">
                <thead style={{ background: REPORT_COLORS.banner }} className="text-white">
                  <tr>
                    {["Element", "Building Value", "Limit Value", "Result"].map((h) => (
                      <th key={h} className="px-3 py-2 text-left font-semibold">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row) => (
                    <tr key={row.item} className="border-t border-hairline">
                      <td className="px-3 py-2">
                        {row.item} {row.unit}
                      </td>
                      <td className="px-3 py-2 text-center">{row.bldg_value.toFixed(3)}</td>
                      <td className="px-3 py-2 text-center">{row.comp_value_1.toFixed(3)}</td>
                      <td
                        className="px-3 py-2 text-center font-bold"
                        style={{
                          color: row.compliant ? REPORT_COLORS.compliant : REPORT_COLORS.nonCompliant,
                        }}
                      >
                        {row.compliant ? "Compliant" : "Non-Compliant"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <VerdictBanner compliant={result.compliant}>
              Overall Result: {result.compliant ? "Compliant" : "Non-Compliant"}
            </VerdictBanner>
          </>
        )}

        <div className="mt-1 flex items-center justify-end gap-3 border-t border-hairline pt-3">
          {saveMessage && <span className="text-xs text-muted">{saveMessage}</span>}
          <Button onClick={onClose}>Close</Button>
          <Button variant="primary" onClick={handleSaveReport}>
            Save report to my computer
          </Button>
        </div>
      </div>
    </Modal>
  );
}
