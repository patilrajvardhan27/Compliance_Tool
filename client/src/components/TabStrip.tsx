"use client";

import { useLayoutEffect, useRef, useState } from "react";

export const TAB_NAMES = ["General Information", "Envelope", "Windows", "Spaces", "HVAC System"] as const;
export type TabName = (typeof TAB_NAMES)[number];

/**
 * The five tabs are a real fill-in order (geometry before envelope before systems), so they are
 * numbered, with a white thumb that slides to the active step.
 */
export function TabStrip({ active, onChange }: { active: TabName; onChange: (tab: TabName) => void }) {
  const track = useRef<HTMLDivElement>(null);
  const buttons = useRef(new Map<TabName, HTMLButtonElement>());
  const [thumb, setThumb] = useState<{ x: number; w: number } | null>(null);

  useLayoutEffect(() => {
    const update = () => {
      const el = buttons.current.get(active);
      if (el) setThumb({ x: el.offsetLeft, w: el.offsetWidth });
    };
    update();
    const observer = new ResizeObserver(update);
    if (track.current) observer.observe(track.current);
    return () => observer.disconnect();
  }, [active]);

  return (
    <nav aria-label="Steps" className="border-b border-hairline bg-canvas px-4 py-2.5">
      <div className="overflow-x-auto">
        <div ref={track} className="segmented">
          {thumb && (
            <span
              aria-hidden
              className="segmented-thumb"
              style={{ width: thumb.w, transform: `translateX(${thumb.x}px)` }}
            />
          )}
          {TAB_NAMES.map((tab, i) => {
            const isActive = active === tab;
            return (
              <button
                key={tab}
                ref={(el) => {
                  if (el) buttons.current.set(tab, el);
                  else buttons.current.delete(tab);
                }}
                onClick={() => onChange(tab)}
                aria-current={isActive ? "page" : undefined}
                className="segmented-item flex shrink-0 items-center gap-2 whitespace-nowrap"
              >
                <span
                  className={`nums flex h-5 w-5 items-center justify-center rounded-full text-[11px] font-semibold transition-colors ${
                    isActive ? "bg-primary text-white" : "bg-canvas text-muted"
                  }`}
                >
                  {i + 1}
                </span>
                {tab}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
