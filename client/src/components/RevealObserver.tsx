"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

/**
 * Fades `[data-reveal]` elements up as they scroll into view. Does nothing
 * when the visitor prefers reduced motion, so content is never hidden.
 */
export function RevealObserver() {
  const pathname = usePathname();

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window)) return;

    const root = document.documentElement;
    root.classList.add("reveal-ready");

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.1 },
    );

    let frame = 0;
    const watch = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        document
          .querySelectorAll("[data-reveal]:not(.is-visible)")
          .forEach((el) => io.observe(el));
      });
    };
    watch();

    const mo = new MutationObserver(watch);
    mo.observe(document.body, { childList: true, subtree: true });

    return () => {
      cancelAnimationFrame(frame);
      io.disconnect();
      mo.disconnect();
    };
  }, [pathname]);

  return null;
}
