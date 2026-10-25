import Link from "next/link";

import { SITE, SITE_LINKS } from "@/lib/site";

/** Global nav: frosted, sticky, with the BEST green rule along the bottom. */
function SiteNav() {
  return (
    <header className="frosted sticky top-0 z-40 border-b-2 border-brand">
      <div className="mx-auto flex h-[52px] max-w-[1200px] items-center justify-between gap-4 px-6 max-sm:px-4">
        <Link href="/" className="flex min-w-0 items-baseline gap-2">
          <span className="text-[17px] font-semibold tracking-[-0.01em] text-ink">{SITE.name}</span>
          <span className="truncate text-[13px] text-muted max-md:hidden">{SITE.tagline}</span>
        </Link>
        <nav aria-label="Site" className="flex items-center gap-6 max-sm:gap-3">
          {SITE_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-[13px] text-muted transition-colors hover:text-body max-sm:hidden"
            >
              {link.label}
            </Link>
          ))}
          <Link href="/tool" className="btn btn-primary btn-sm">
            Open the tool
          </Link>
        </nav>
      </div>
    </header>
  );
}

function SiteFooter() {
  return (
    <footer className="on-dark border-t-4 border-brand bg-charcoal">
      <div className="mx-auto flex max-w-[1200px] flex-wrap items-center justify-between gap-4 px-6 py-10 text-[12px] max-sm:px-4">
        <div>
          <p className="text-[14px] font-semibold text-white">{SITE.name}</p>
          <p className="mt-1 text-mint">
            © <span className="nums">{SITE.year}</span> {SITE.owner}
          </p>
        </div>
        <nav aria-label="Legal" className="flex gap-6">
          {SITE_LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="text-mint transition-colors hover:text-white">
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}

/** Shared frame for the landing page and the legal pages. */
export function SiteFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-canvas">
      <SiteNav />
      <main className="flex-1">{children}</main>
      <SiteFooter />
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
      <article className="bg-mist">
        <div className="mx-auto max-w-[760px] px-6 pb-20 pt-16 max-sm:px-4 max-sm:pt-10">
          <div className="animate-enter">
            <p className="text-[14px] font-semibold text-primary">{SITE.name}</p>
            <h1 className="mt-2 text-[40px] leading-[1.1] tracking-[-0.5px] max-sm:text-[30px]">{title}</h1>
            <p className="mt-4 text-[21px] font-light leading-[1.5] text-muted max-sm:text-[17px]">{summary}</p>
          </div>
          <div className="stagger mt-12 flex flex-col gap-4">{children}</div>
        </div>
      </article>
    </SiteFrame>
  );
}

export function DocumentSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card p-6 max-sm:p-5">
      <h2 className="text-[21px] tracking-[-0.2px]">{title}</h2>
      <div className="mt-3 space-y-3 text-[17px] leading-[1.47] text-muted [&_a]:text-primary [&_a]:underline-offset-2 hover:[&_a]:underline [&_li]:ml-5 [&_li]:list-disc [&_strong]:font-semibold [&_strong]:text-body [&_ul]:space-y-1.5">
        {children}
      </div>
    </section>
  );
}
