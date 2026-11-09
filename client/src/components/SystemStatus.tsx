"use client";

import { useEffect, useState } from "react";

type Status = "checking" | "operational" | "degraded" | "down";

const POLL_INTERVAL_MS = 60_000;
const REQUEST_TIMEOUT_MS = 10_000;

const DISPLAY: Record<Status, { label: string; color: string }> = {
  checking: { label: "Checking system status", color: "#9ca3af" },
  operational: { label: "All systems operational", color: "#00964f" },
  degraded: { label: "Some services degraded", color: "#d97706" },
  down: { label: "Service unavailable", color: "#dc2626" },
};

async function checkHealth(url: string): Promise<Status> {
  try {
    const response = await fetch(url, {
      cache: "no-store",
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    if (response.ok) return "operational";
    return response.status === 503 ? "degraded" : "down";
  } catch {
    return "down";
  }
}

/** Live service status from the API health check. Polls while the tab is visible. */
export function SystemStatus({ url, className = "" }: { url: string; className?: string }) {
  const [status, setStatus] = useState<Status>("checking");
  const [checkedAt, setCheckedAt] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const refresh = async () => {
      if (document.hidden) return;
      const next = await checkHealth(url);
      if (cancelled) return;
      setStatus(next);
      setCheckedAt(new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }));
    };

    refresh();
    const timer = window.setInterval(refresh, POLL_INTERVAL_MS);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [url]);

  const { label, color } = DISPLAY[status];

  return (
    <p
      role="status"
      aria-live="polite"
      title={checkedAt ? `Last checked ${checkedAt}` : undefined}
      className={`inline-flex w-fit items-center gap-2.5 rounded-full border border-black/10 bg-white/70 py-1.5 pl-3 pr-3.5 text-[12px] font-medium leading-none ${className}`}
    >
      <span aria-hidden className="relative flex h-2 w-2">
        {status !== "checking" && (
          <span
            className="absolute -inset-[3px] rounded-full motion-safe:animate-pulse"
            style={{ backgroundColor: `${color}40` }}
          />
        )}
        <span className="relative h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      </span>
      {label}
    </p>
  );
}
