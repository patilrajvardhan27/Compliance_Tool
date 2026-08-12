"use client";

import { useMutation } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { PerformanceReportModal } from "@/components/results/PerformanceReportModal";
import { PrescriptiveResultModal } from "@/components/results/PrescriptiveResultModal";
import { TabStrip, type TabName } from "@/components/TabStrip";
import { TopActionBar } from "@/components/TopActionBar";
import { EnvelopeTab } from "@/components/tabs/EnvelopeTab";
import { GeneralTab } from "@/components/tabs/GeneralTab";
import { HvacTab } from "@/components/tabs/HvacTab";
import { SpacesTab } from "@/components/tabs/SpacesTab";
import { WindowsTab } from "@/components/tabs/WindowsTab";
import {
  createNewBuilding,
  parseProjectFile,
  runPerformance,
  runPrescriptive,
  serializeProject,
} from "@/lib/api";
import { PRESCRIPTIVE_DISABLED_CATEGORIES } from "@/lib/constants";
import { blankDraft, draftFromBuildingInput, finalizeDraft } from "@/lib/draft";
import { openLocalTct, saveLocalFile, writeToHandle } from "@/lib/localFile";
import type { BuildingDraft, BuildingInput, PerformanceReport, PrescriptiveResult } from "@/lib/types";
import { useBuildingInput } from "@/providers/BuildingInputProvider";
import { useReferenceData } from "@/providers/ReferenceDataProvider";

interface Notice {
  kind: "info" | "error";
  message: string;
  /** Optional itemized detail (e.g. the list of fields still blank). */
  items?: string[];
}

function wwrViolations(bi: BuildingDraft): string[] {
  if (!bi.rdbtnWinWwr) return [];
  const orientations: [string, "south_percent" | "north_percent" | "east_percent" | "west_percent"][] = [
    ["South", "south_percent"],
    ["North", "north_percent"],
    ["East", "east_percent"],
    ["West", "west_percent"],
  ];
  const violations: string[] = [];
  for (const [label, key] of orientations) {
    const total = bi.window_rows.reduce((sum, row) => sum + (row[key] || 0), 0);
    if (total > 100) {
      violations.push(
        `The window rows on the ${label} wall add up to ${total.toFixed(0)}% of the wall area. ` +
          "The combined Window-to-Wall Ratio per orientation cannot exceed 100% -- DOE-2.2 would " +
          "reject the building (windows larger than the wall). Please reduce the window percentages."
      );
    }
  }
  return violations;
}

const stem = (fileName: string) => fileName.replace(/\.tct$/i, "");

export function Workspace() {
  const ref = useReferenceData();
  const { bi, setBi, projectName, setProjectName, reloading, error, dirty, markSaved } = useBuildingInput();
  const [activeTab, setActiveTab] = useState<TabName>("General Information");
  const [notice, setNotice] = useState<Notice | null>(null);
  const [prescriptiveResult, setPrescriptiveResult] = useState<PrescriptiveResult | null>(null);
  const [performanceReport, setPerformanceReport] = useState<PerformanceReport | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const fileHandleRef = useRef<FileSystemFileHandle | null>(null);

  /** Runs the completeness check and reports blank fields; null means "not ready yet". */
  function requireComplete(): BuildingInput | null {
    if (!bi) return null;
    const { bi: complete, missing } = finalizeDraft(bi);
    if (!complete) {
      setNotice({
        kind: "error",
        message: "Please fill in the highlighted fields first — nothing is assumed by default:",
        items: missing,
      });
      return null;
    }
    return complete;
  }

  const prescriptiveMutation = useMutation({
    mutationFn: runPrescriptive,
    onSuccess: (res) => {
      setNotice(null);
      setPrescriptiveResult(res);
    },
    onError: (e: Error) => setNotice({ kind: "error", message: e.message }),
  });

  const performanceMutation = useMutation({
    mutationFn: ({ name, input }: { name: string; input: BuildingInput }) => runPerformance(name, input),
    onSuccess: (res) => {
      if (res.status === "ok" && res.report) {
        setNotice(null);
        setPerformanceReport(res.report);
      } else {
        setNotice({ kind: res.status === "simulation_unavailable" ? "info" : "error", message: res.message });
      }
    },
    onError: (e: Error) => setNotice({ kind: "error", message: e.message }),
  });

  if (reloading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-slate-500">Loading…</div>
    );
  }
  if (error || !bi) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-red-600">
        Failed to initialize: {error ?? "unknown error"}
      </div>
    );
  }

  const typeRow = ref.bldg_types.find((t) => t.bldg_type === bi.cmbBldgType);
  const prescriptiveDisabled = typeRow ? PRESCRIPTIVE_DISABLED_CATEGORIES.has(typeRow.cat) : false;

  async function handleNew() {
    if (dirty && !confirm("Discard unsaved changes and start a new project?")) return;
    try {
      const fresh = await createNewBuilding();
      const blank = blankDraft(fresh);
      setBi(blank);
      setProjectName(null);
      setFileName(null);
      fileHandleRef.current = null;
      markSaved();
      setNotice(null);
      setActiveTab("General Information");
    } catch (e) {
      setNotice({ kind: "error", message: (e as Error).message });
    }
  }

  async function handleOpen() {
    if (dirty && !confirm("Discard unsaved changes and open another project?")) return;
    try {
      const opened = await openLocalTct();
      if (!opened) return; // user cancelled the picker
      const loaded = await parseProjectFile(opened.file);
      const draft = draftFromBuildingInput(loaded);
      setBi(draft);
      fileHandleRef.current = opened.handle;
      setFileName(opened.file.name);
      setProjectName(stem(opened.file.name));
      markSaved();
      setNotice({ kind: "info", message: `Opened "${opened.file.name}" from your computer.` });
    } catch (e) {
      setNotice({ kind: "error", message: `Unable to open the file: ${(e as Error).message}` });
    }
  }

  async function handleSave(saveAs: boolean) {
    const complete = requireComplete();
    if (!complete) return;
    const name = fileName ? stem(fileName) : complete.txtBldgName.trim();
    try {
      const blob = await serializeProject(name, complete);
      if (!saveAs && fileHandleRef.current) {
        await writeToHandle(fileHandleRef.current, blob);
        markSaved();
        setNotice({ kind: "info", message: `Saved "${fileName}".` });
        return;
      }
      const saved = await saveLocalFile(blob, `${name}.tct`);
      if (!saved) return; // user cancelled the save dialog
      fileHandleRef.current = saved.handle;
      setFileName(saved.fileName);
      setProjectName(stem(saved.fileName));
      markSaved();
      setNotice({
        kind: "info",
        message: saved.handle
          ? `Saved "${saved.fileName}" to your computer.`
          : `"${saved.fileName}" was downloaded to your computer (check your Downloads folder).`,
      });
    } catch (e) {
      setNotice({ kind: "error", message: `Save failed: ${(e as Error).message}` });
    }
  }

  function handlePrescriptive() {
    const complete = requireComplete();
    if (!complete) return;
    prescriptiveMutation.mutate(complete);
  }

  function handlePerformance() {
    const complete = requireComplete();
    if (!complete) return;
    const violations = wwrViolations(bi!);
    if (violations.length > 0) {
      setNotice({ kind: "error", message: violations[0] });
      return;
    }
    const name = projectName ?? complete.txtBldgName.trim();
    performanceMutation.mutate({ name, input: complete });
  }

  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <TopActionBar
        fileName={fileName}
        dirty={dirty}
        onNew={handleNew}
        onOpen={handleOpen}
        onSave={() => handleSave(false)}
        onSaveAs={() => handleSave(true)}
        onPrescriptive={handlePrescriptive}
        onPerformance={handlePerformance}
        prescriptiveDisabled={prescriptiveDisabled}
        prescriptiveLoading={prescriptiveMutation.isPending}
        performanceLoading={performanceMutation.isPending}
      />

      <TabStrip active={activeTab} onChange={setActiveTab} />

      {notice && (
        <div
          role={notice.kind === "error" ? "alert" : "status"}
          className={`mx-4 mt-3 flex items-start justify-between gap-4 rounded-md border px-3.5 py-2.5 text-sm ${
            notice.kind === "error"
              ? "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"
              : "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950/40 dark:text-blue-300"
          }`}
        >
          <div>
            <p className="whitespace-pre-line">{notice.message}</p>
            {notice.items && (
              <ul className="mt-1.5 list-disc space-y-0.5 pl-5 text-[13px]">
                {notice.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            )}
          </div>
          <button
            onClick={() => setNotice(null)}
            className="shrink-0 font-medium opacity-70 hover:opacity-100"
          >
            Dismiss
          </button>
        </div>
      )}

      <main className="mx-auto w-full max-w-5xl flex-1 p-4">
        {activeTab === "General Information" && <GeneralTab />}
        {activeTab === "Envelope" && <EnvelopeTab />}
        {activeTab === "Windows" && <WindowsTab />}
        {activeTab === "Spaces" && <SpacesTab />}
        {activeTab === "HVAC System" && <HvacTab />}
      </main>

      {prescriptiveResult && (
        <PrescriptiveResultModal
          result={prescriptiveResult}
          bldgName={bi.txtBldgName || projectName || "Building"}
          onClose={() => setPrescriptiveResult(null)}
        />
      )}
      {performanceReport && (
        <PerformanceReportModal report={performanceReport} onClose={() => setPerformanceReport(null)} />
      )}
    </div>
  );
}
