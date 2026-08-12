"use client";

import { useQuery } from "@tanstack/react-query";
import { createContext, useContext } from "react";

import { getReference } from "@/lib/api";
import type { ReferenceSnapshot } from "@/lib/types";

const ReferenceDataContext = createContext<ReferenceSnapshot | undefined>(undefined);

export function ReferenceDataProvider({ children }: { children: React.ReactNode }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["reference"],
    queryFn: getReference,
    staleTime: Infinity,
  });

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-slate-500">
        Loading reference data…
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-red-600">
        Failed to load reference data from the API: {(error as Error)?.message ?? "unknown error"}
      </div>
    );
  }

  return <ReferenceDataContext.Provider value={data}>{children}</ReferenceDataContext.Provider>;
}

export function useReferenceData(): ReferenceSnapshot {
  const ctx = useContext(ReferenceDataContext);
  if (!ctx) throw new Error("useReferenceData must be used within a ReferenceDataProvider");
  return ctx;
}
