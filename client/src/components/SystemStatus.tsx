"use client";

import { useEffect, useState } from "react";

type Status = "checking" | "operational" | "degraded" | "down";

const POLL_INTERVAL_MS = 60_000;
const REQUEST_TIMEOUT_MS = 10_000;

const DISPLAY: Record<Status, { label: string; dot: string }> = {
  checking: { label: "Checking status", dot: "bg-[#9ca3af]" },
  operational: { label: "All systems operational", dot: "bg-[#00964f]" },
  degraded: { label: "Some services degraded", dot: "bg-[#d97706]" },
  down: { label: "Service unavailable", dot: "bg-[#dc2626]" },
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

  const { label, dot } = DISPLAY[status];

  return (
    <p
      role="status"
      aria-live="polite"
      title={checkedAt ? `${label} (checked ${checkedAt})` : label}
      className={`flex shrink-0 items-center gap-2 text-[13px] ${className}`}
    >
      <span aria-hidden className="relative flex h-2.5 w-2.5">
        {status === "operational" && (
          <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 motion-safe:animate-ping ${dot}`} />
        )}
        <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${dot}`} />
      </span>
      <span className="max-lg:sr-only">{label}</span>
    </p>
  );
}
