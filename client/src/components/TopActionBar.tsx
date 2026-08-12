"use client";

import { Button } from "@/components/ui/Field";

export function TopActionBar({
  fileName,
  dirty,
  onNew,
  onOpen,
  onSave,
  onSaveAs,
  onPrescriptive,
  onPerformance,
  prescriptiveDisabled,
  prescriptiveLoading,
  performanceLoading,
}: {
  /** Name of the .tct file on the user's machine, if the project has been saved/opened. */
  fileName: string | null;
  dirty: boolean;
  onNew: () => void;
  onOpen: () => void;
  onSave: () => void;
  onSaveAs: () => void;
  onPrescriptive: () => void;
  onPerformance: () => void;
  prescriptiveDisabled: boolean;
  prescriptiveLoading: boolean;
  performanceLoading: boolean;
}) {
  return (
    <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 px-4 py-2.5">
        <div className="flex items-center gap-2.5">
          <span
            aria-hidden
            className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--cobalt)] font-mono text-sm font-bold text-white"
          >
            TB
          </span>
          <div className="leading-tight">
            <p className="font-mono text-sm font-bold tracking-[0.14em] text-slate-800 dark:text-slate-100">
              TUNBEEC
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Tunisian Building Energy Efficiency Code
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 border-l border-slate-200 pl-5 dark:border-slate-700">
          <Button variant="ghost" onClick={onNew}>
            New
          </Button>
          <Button variant="ghost" onClick={onOpen}>
            Open…
          </Button>
          <Button variant="ghost" onClick={onSave}>
            Save
          </Button>
          <Button variant="ghost" onClick={onSaveAs}>
            Save As…
          </Button>
          <span className="ml-2 max-w-[260px] truncate text-xs text-slate-500 dark:text-slate-400">
            {fileName ? (
              <>
                <span className="font-mono">{fileName}</span>
                {dirty && <span title="Unsaved changes"> •</span>}
              </>
            ) : (
              "Not saved to a file yet"
            )}
          </span>
        </div>

        <div className="ml-auto flex gap-2">
          <Button
            variant="primary"
            onClick={onPrescriptive}
            disabled={prescriptiveDisabled || prescriptiveLoading}
            title={
              prescriptiveDisabled
                ? "The prescriptive approach is not available for this building category."
                : undefined
            }
          >
            {prescriptiveLoading ? "Checking…" : "Run Prescriptive Check"}
          </Button>
          <Button variant="primary" onClick={onPerformance} disabled={performanceLoading}>
            {performanceLoading ? "Simulating…" : "Run Performance Check"}
          </Button>
        </div>
      </div>
    </header>
  );
}
