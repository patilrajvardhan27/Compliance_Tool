"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { createNewBuilding } from "@/lib/api";
import { blankDraft } from "@/lib/draft";
import type { BuildingDraft } from "@/lib/types";

interface BuildingInputContextValue {
  bi: BuildingDraft | null;
  setBi: (bi: BuildingDraft) => void;
  updateBi: (patch: Partial<BuildingDraft>) => void;
  /** Base name of the .tct file this session is working on, without extension. */
  projectName: string | null;
  setProjectName: (name: string | null) => void;
  reloading: boolean;
  error: string | null;
  /** True once `bi` has diverged from the last markSaved() snapshot. */
  dirty: boolean;
  /** Records the current `bi` as the clean baseline (call after New / Open / Save succeed). */
  markSaved: () => void;
}

const BuildingInputContext = createContext<BuildingInputContextValue | undefined>(undefined);

export function BuildingInputProvider({ children }: { children: React.ReactNode }) {
  const [bi, setBiState] = useState<BuildingDraft | null>(null);
  const [projectName, setProjectName] = useState<string | null>(null);
  const [reloading, setReloading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savedSnapshot, setSavedSnapshot] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    // The server template carries desktop defaults; the web form intentionally starts blank.
    createNewBuilding()
      .then((fresh) => {
        if (cancelled) return;
        const blank = blankDraft(fresh);
        setBiState(blank);
        setSavedSnapshot(JSON.stringify(blank));
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setReloading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const setBi = useCallback((next: BuildingDraft) => setBiState(next), []);

  const updateBi = useCallback((patch: Partial<BuildingDraft>) => {
    setBiState((current) => (current ? { ...current, ...patch } : current));
  }, []);

  const markSaved = useCallback(() => {
    setBiState((current) => {
      setSavedSnapshot(current ? JSON.stringify(current) : null);
      return current;
    });
  }, []);

  const dirty = bi !== null && savedSnapshot !== null && savedSnapshot !== JSON.stringify(bi);

  return (
    <BuildingInputContext.Provider
      value={{ bi, setBi, updateBi, projectName, setProjectName, reloading, error, dirty, markSaved }}
    >
      {children}
    </BuildingInputContext.Provider>
  );
}

export function useBuildingInput(): BuildingInputContextValue {
  const ctx = useContext(BuildingInputContext);
  if (!ctx) throw new Error("useBuildingInput must be used within a BuildingInputProvider");
  return ctx;
}
