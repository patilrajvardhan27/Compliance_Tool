import Link from "next/link";

import { SITE, SITE_LINKS } from "@/lib/site";

const FOCUS =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--cobalt)]";

export const PRIMARY_LINK = `rounded-md bg-[var(--cobalt)] font-medium text-white transition-colors hover:bg-[var(--cobalt-deep)] ${FOCUS}`;

/** Header and footer shared by the landing page and the legal pages. */
export function SiteFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-2.5">
          <Link href="/" className={`flex items-center gap-2.5 rounded-md ${FOCUS}`}>
            <span
              aria-hidden
              className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--cobalt)] font-mono text-sm font-bold text-white"
            >
              TB
            </span>
            <span className="leading-tight">
              <span className="block font-mono text-sm font-bold tracking-[0.14em] text-slate-800 dark:text-slate-100">
                {SITE.name}
              </span>
              <span className="block text-[11px] text-slate-500 dark:text-slate-400">{SITE.tagline}</span>
            </span>
          </Link>

          <nav aria-label="Site" className="flex items-center gap-1">
            {SITE_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-md px-3 py-1.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-800 dark:text-slate-300 dark:hover:bg-slate-800 max-sm:px-2 ${FOCUS}`}
              >
                {link.label}
              </Link>
            ))}
            <Link href="/tool" className={`ml-2 px-3 py-1.5 text-sm ${PRIMARY_LINK}`}>
              Get started
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10 max-sm:py-6">{children}</main>

      <footer className="border-t border-slate-200 dark:border-slate-800">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-4 text-xs text-slate-500 dark:text-slate-400">
          <p>
            © {SITE.year} {SITE.owner}
          </p>
          <nav aria-label="Legal" className="flex gap-4">
            {SITE_LINKS.map((link) => (
              <Link key={link.href} href={link.href} className={`rounded hover:text-slate-800 dark:hover:text-slate-100 ${FOCUS}`}>
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </footer>
    </div>
  );
}

/** A legal or contact page: a title over a stack of headed cards. */
export function SiteDocument({
  title,
  summary,
  children,
}: {
  title: string;
  summary: string;
  children: React.ReactNode;
}) {
  return (
    <SiteFrame>
      <article className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-slate-50 max-sm:text-2xl">
          {title}
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{summary}</p>
        <div className="mt-6 flex flex-col gap-4">{children}</div>
      </article>
    </SiteFrame>
  );
}

export function DocumentSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(20,30,45,0.05)] dark:border-slate-800 dark:bg-slate-900">
      <h2 className="border-b border-slate-100 pb-2.5 text-[13px] font-semibold uppercase tracking-[0.08em] text-slate-700 dark:border-slate-800 dark:text-slate-200">
        {title}
      </h2>
      <div className="mt-3 space-y-3 text-sm leading-relaxed text-slate-600 dark:text-slate-300 [&_a]:text-[var(--cobalt)] [&_a]:underline [&_a]:underline-offset-2 [&_li]:ml-5 [&_li]:list-disc [&_strong]:font-semibold [&_strong]:text-slate-800 dark:[&_strong]:text-slate-100 [&_ul]:space-y-1.5">
        {children}
      </div>
    </section>
  );
}
