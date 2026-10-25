"use client";

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

export type SearchOption = { value: string; label?: string; group?: string };

type Props = {
  id?: string;
  value: string;
  options: readonly (string | SearchOption)[];
  onChange: (value: string) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  disabled?: boolean;
  className?: string;
};

const fold = (text: string) =>
  text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

/**
 * A select with a search box, for long option lists. The list opens in a
 * portal so scrolling containers and dialogs never clip it.
 */
export function SearchSelect({
  id,
  value,
  options,
  onChange,
  placeholder = "Select…",
  searchPlaceholder = "Search",
  disabled,
  className = "",
}: Props) {
  const auto = useId();
  const triggerId = id ?? `${auto}-trigger`;
  const listId = `${auto}-list`;
  const trigger = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  const list = useRef<HTMLUListElement>(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const [box, setBox] = useState<{ left: number; width: number; top?: number; bottom?: number }>();

  const all = useMemo(
    () => options.map((o) => (typeof o === "string" ? { value: o, label: o } : { ...o, label: o.label ?? o.value })),
    [options],
  );
  const shown = useMemo(() => {
    const words = fold(query).split(/\s+/).filter(Boolean);
    if (!words.length) return all;
    return all.filter((o) => {
      const hay = fold(`${o.label} ${o.group ?? ""}`);
      return words.every((w) => hay.includes(w));
    });
  }, [all, query]);
  const current = all.find((o) => o.value === value);

  const place = () => {
    const r = trigger.current?.getBoundingClientRect();
    if (!r) return;
    const below = window.innerHeight - r.bottom;
    const width = Math.max(r.width, 288);
    const left = Math.min(r.left, window.innerWidth - width - 8);
    setBox(below < 320 && r.top > below
      ? { left, width, bottom: window.innerHeight - r.top + 6 }
      : { left, width, top: r.bottom + 6 });
  };

  const show = (seed = "") => {
    if (disabled) return;
    place();
    setQuery(seed);
    setActive(Math.max(0, seed ? 0 : all.findIndex((o) => o.value === value)));
    setOpen(true);
  };
  const close = (refocus = true) => {
    setOpen(false);
    if (refocus) trigger.current?.focus();
  };
  const pick = (v: string) => {
    onChange(v);
    close();
  };

  useLayoutEffect(() => {
    if (!open) return;
    const update = (e: Event) => {
      if (!(e.target instanceof Node && panel.current?.contains(e.target))) place();
    };
    window.addEventListener("resize", update);
    window.addEventListener("scroll", update, true);
    return () => {
      window.removeEventListener("resize", update);
      window.removeEventListener("scroll", update, true);
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const away = (e: PointerEvent) => {
      const t = e.target as Node;
      if (!panel.current?.contains(t) && !trigger.current?.contains(t)) close(false);
    };
    document.addEventListener("pointerdown", away);
    return () => document.removeEventListener("pointerdown", away);
  }, [open]);

  useEffect(() => {
    if (open) list.current?.querySelector(`[data-index="${active}"]`)?.scrollIntoView({ block: "nearest" });
  }, [active, open]);

  const onSearchKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") setActive((i) => Math.min(i + 1, shown.length - 1));
    else if (e.key === "ArrowUp") setActive((i) => Math.max(i - 1, 0));
    else if (e.key === "Home") setActive(0);
    else if (e.key === "End") setActive(shown.length - 1);
    else if (e.key === "Enter" && shown[active]) pick(shown[active].value);
    else if (e.key === "Escape") close();
    else if (e.key === "Tab") {
      // Hand focus back to the field so Tab carries on to the next one.
      close();
      return;
    } else return;
    e.preventDefault();
  };

  const onTriggerKey = (e: React.KeyboardEvent) => {
    if (["ArrowDown", "ArrowUp", "Enter", " "].includes(e.key)) {
      e.preventDefault();
      show();
    } else if (e.key.length === 1 && !e.metaKey && !e.ctrlKey && !e.altKey) {
      e.preventDefault();
      show(e.key);
    }
  };

  return (
    <>
      <button
        ref={trigger}
        id={triggerId}
        type="button"
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        onClick={() => (open ? close() : show())}
        onKeyDown={onTriggerKey}
        className={`field flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-[14px] disabled:cursor-not-allowed disabled:bg-mist disabled:text-faint max-sm:py-2.5 max-sm:text-base ${className}`}
      >
        <span className={`truncate ${current ? "text-body" : "text-muted"}`}>
          {current?.label ?? placeholder}
        </span>
        <svg aria-hidden viewBox="0 0 20 20" className={`h-4 w-4 shrink-0 text-muted transition-transform duration-200 ${open ? "rotate-180" : ""}`}>
          <path d="M5 7.5l5 5 5-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && box &&
        createPortal(
          <div
            ref={panel}
            style={{ position: "fixed", left: box.left, width: box.width, top: box.top, bottom: box.bottom }}
            className="animate-scale-in z-[60] overflow-hidden rounded-card border border-hairline bg-canvas font-sans shadow-render"
          >
            <div className="border-b border-hairline p-2">
              <div className="relative">
                <svg aria-hidden viewBox="0 0 20 20" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted">
                  <circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M13 13l3.5 3.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
                <input
                  autoFocus
                  role="combobox"
                  aria-expanded="true"
                  aria-controls={listId}
                  aria-autocomplete="list"
                  aria-activedescendant={shown[active] ? `${listId}-${active}` : undefined}
                  aria-label={searchPlaceholder}
                  placeholder={searchPlaceholder}
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setActive(0);
                  }}
                  onKeyDown={onSearchKey}
                  onFocus={(e) => e.currentTarget.setSelectionRange(query.length, query.length)}
                  className="w-full rounded-full border border-hairline bg-mist py-2 pl-9 pr-3 text-[14px] text-body outline-none focus:border-brand max-sm:text-base"
                />
              </div>
            </div>
            <ul ref={list} id={listId} role="listbox" className="max-h-72 overflow-y-auto overscroll-contain p-1.5">
              {shown.map((o, i) => {
                const header = o.group && o.group !== shown[i - 1]?.group ? o.group : null;
                const selected = o.value === value;
                return (
                  <li key={o.value} role="presentation">
                    {header && (
                      <p className="px-3 pb-1 pt-2.5 text-[12px] font-semibold text-muted">{header}</p>
                    )}
                    <div
                      id={`${listId}-${i}`}
                      data-index={i}
                      role="option"
                      aria-selected={selected}
                      onPointerMove={() => setActive(i)}
                      onClick={() => pick(o.value)}
                      className={`flex cursor-pointer items-center justify-between gap-2 rounded-[8px] px-3 py-2 text-[14px] ${
                        i === active ? "bg-mint text-ink" : "text-body"
                      } ${selected ? "font-semibold" : ""}`}
                    >
                      <span>{o.label}</span>
                      {selected && (
                        <svg aria-hidden viewBox="0 0 20 20" className="h-4 w-4 shrink-0 text-primary">
                          <path d="M5 10.5l3.5 3.5L15 7" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      )}
                    </div>
                  </li>
                );
              })}
              {shown.length === 0 && (
                <li role="presentation" className="px-3 py-6 text-center text-[14px] text-muted">
                  No matches for “{query}”
                </li>
              )}
            </ul>
            <p className="nums border-t border-hairline px-4 py-2 text-[12px] text-faint" aria-live="polite">
              {shown.length} of {all.length}
            </p>
          </div>,
          document.body,
        )}
    </>
  );
}
