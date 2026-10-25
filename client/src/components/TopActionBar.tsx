"use client";

import Link from "next/link";

import { BestLogo } from "@/components/BestLogo";
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
    <header className="frosted sticky top-0 z-40 border-b-2 border-brand">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 px-4 py-2">
        <div className="flex items-center gap-3">
          <BestLogo height={30} />
          <span aria-hidden className="h-6 w-px bg-hairline" />
          <p className="text-[17px] font-semibold tracking-[-0.01em] text-ink">TUNBEEC</p>
          <p className="text-[13px] text-muted max-xl:hidden">Tunisian Building Energy Efficiency Code</p>
        </div>

        <div className="flex flex-wrap items-center gap-1 border-l border-hairline pl-4">
          <Link
            href="/"
            onClick={(e) => {
              if (dirty && !confirm("Leave the tool? Unsaved changes will be lost.")) e.preventDefault();
            }}
            className="btn btn-sm rounded-field px-3 text-muted hover:bg-mist hover:text-body"
          >
            Home
          </Link>
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
          <span className="ml-2 max-w-[260px] truncate text-[13px] text-muted">
            {fileName ? (
              <>
                <span className="font-medium text-body">{fileName}</span>
                {dirty && (
                  <span title="Unsaved changes" className="ml-1.5 inline-block h-1.5 w-1.5 rounded-full bg-warning align-middle" />
                )}
              </>
            ) : (
              "Not saved to a file yet"
            )}
          </span>
        </div>

        <div className="ml-auto flex flex-wrap gap-2">
          <Button
            variant="secondary"
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
