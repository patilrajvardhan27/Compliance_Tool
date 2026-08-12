"use client";

export const TAB_NAMES = ["General Information", "Envelope", "Windows", "Spaces", "HVAC System"] as const;
export type TabName = (typeof TAB_NAMES)[number];

/**
 * The five tabs are a real fill-in order (geometry before envelope before systems), so they are
 * presented as a numbered workflow rail rather than plain tabs.
 */
export function TabStrip({ active, onChange }: { active: TabName; onChange: (tab: TabName) => void }) {
  return (
    <nav className="border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-900">
      <div className="flex gap-1 overflow-x-auto">
        {TAB_NAMES.map((tab, i) => {
          const isActive = active === tab;
          return (
            <button
              key={tab}
              onClick={() => onChange(tab)}
              aria-current={isActive ? "page" : undefined}
              className={`group flex items-baseline gap-2 whitespace-nowrap border-b-2 px-3.5 py-2.5 text-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-[var(--cobalt)] ${
                isActive
                  ? "border-[var(--cobalt)] font-semibold text-[var(--cobalt)]"
                  : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
            >
              <span
                className={`font-mono text-[11px] tabular-nums ${
                  isActive ? "text-[var(--cobalt)]" : "text-slate-400 dark:text-slate-500"
                }`}
              >
                {String(i + 1).padStart(2, "0")}
              </span>
              {tab}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
