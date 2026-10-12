import Link from "next/link";

import { PRIMARY_LINK, SiteFrame } from "@/components/site/SiteFrame";

const STEPS = [
  {
    title: "Describe the building",
    body: "Five tabs in order: general information, envelope, windows, spaces and HVAC system. Nothing is pre-filled, so the result reflects your building.",
  },
  {
    title: "Run the prescriptive check",
    body: "Each wall, roof, floor and window is compared with the code's fixed limits and reported element by element.",
  },
  {
    title: "Run the performance check",
    body: "The whole building is simulated in DOE-2.2 and compared with a reference building built to the code.",
  },
];

export default function Landing() {
  return (
    <SiteFrame>
      <section className="mx-auto max-w-3xl text-center">
        <p className="font-mono text-xs font-bold tracking-[0.14em] text-[var(--cobalt)]">ENERGY CODE COMPLIANCE</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900 dark:text-slate-50 max-sm:text-3xl">
          Does this building meet Tunisia&apos;s energy code?
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-base leading-relaxed text-slate-600 dark:text-slate-300">
          TUNBEEC answers it in the browser. Describe the building, then check each element against the
          code&apos;s limits or simulate the whole thing.
        </p>
        <div className="mt-6 flex justify-center">
          <Link href="/tool" className={`px-6 py-3 text-base ${PRIMARY_LINK}`}>
            Get started
          </Link>
        </div>
      </section>

      <figure className="mt-10">
        <video
          className="aspect-video w-full rounded-lg border border-slate-200 bg-slate-900 shadow-[0_1px_2px_rgba(20,30,45,0.05)] dark:border-slate-800"
          controls
          playsInline
          preload="metadata"
          poster="/intro-poster.jpg"
        >
          <source src="/intro.mp4" type="video/mp4" />
        </video>
        <figcaption className="mt-2 text-center text-xs text-slate-500 dark:text-slate-400">
          A 20-second intro, recorded in the live tool.
        </figcaption>
      </figure>

      <ol className="mt-10 grid gap-4 md:grid-cols-3">
        {STEPS.map((step, i) => (
          <li
            key={step.title}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(20,30,45,0.05)] dark:border-slate-800 dark:bg-slate-900"
          >
            <p className="font-mono text-xs font-bold text-[var(--cobalt)]">{i + 1}</p>
            <h2 className="mt-1 text-[13px] font-semibold uppercase tracking-[0.08em] text-slate-700 dark:text-slate-200">
              {step.title}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{step.body}</p>
          </li>
        ))}
      </ol>
    </SiteFrame>
  );
}
