import Link from "next/link";

import { SiteFrame } from "@/components/site/SiteFrame";

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
      {/* Hero tile */}
      <section className="bg-canvas px-6 pb-20 pt-20 text-center max-sm:px-4 max-sm:pb-12 max-sm:pt-12">
        <div className="mx-auto max-w-3xl">
          <p className="animate-enter text-[17px] font-semibold text-primary">Energy code compliance</p>
          <h1 className="animate-enter mt-3 text-[56px] leading-[1.07] tracking-[-0.9px] [animation-delay:80ms] max-md:text-[40px] max-sm:text-[34px] max-sm:tracking-[-0.4px]">
            Does this building meet Tunisia&apos;s energy code?
          </h1>
          <p className="animate-enter mx-auto mt-5 max-w-xl text-[21px] font-light leading-[1.5] text-muted [animation-delay:160ms] max-sm:text-[17px]">
            TUNBEEC answers it in the browser. Describe the building, then check each element against the
            code&apos;s limits or simulate the whole thing.
          </p>
          <div className="animate-enter mt-8 flex flex-wrap justify-center gap-3 [animation-delay:240ms]">
            <Link href="/tool" className="btn btn-primary">
              Open the tool
            </Link>
            <a href="#intro" className="btn btn-secondary">
              Watch the intro
            </a>
          </div>
        </div>

        <figure id="intro" className="animate-scale-in mx-auto mt-14 max-w-[1040px] scroll-mt-24 [animation-delay:320ms]">
          <video
            className="aspect-video w-full rounded-card bg-canopy shadow-render"
            controls
            playsInline
            preload="metadata"
            poster="/intro-poster.jpg"
          >
            <source src="/intro.mp4" type="video/mp4" />
          </video>
          <figcaption className="mt-4 text-[14px] text-faint">A 20-second intro, recorded in the live tool.</figcaption>
        </figure>
      </section>

      {/* Steps tile */}
      <section className="bg-mist px-6 py-20 max-sm:px-4 max-sm:py-12" aria-labelledby="how">
        <div className="mx-auto max-w-[1100px]">
          <h2 id="how" data-reveal className="text-center text-[40px] leading-[1.1] tracking-[-0.5px] max-sm:text-[30px]">
            Three steps to an answer.
          </h2>
          <ol className="mt-12 grid gap-4 md:grid-cols-3">
            {STEPS.map((step, i) => (
              <li
                key={step.title}
                data-reveal
                style={{ "--d": `${i * 90}ms` } as React.CSSProperties}
                className="card p-7"
              >
                <span className="nums flex h-9 w-9 items-center justify-center rounded-full bg-mint-wash text-[15px] font-semibold text-primary">
                  {i + 1}
                </span>
                <h3 className="mt-5 text-[21px] leading-[1.19] tracking-[-0.2px]">{step.title}</h3>
                <p className="mt-2 text-[17px] leading-[1.47] text-muted">{step.body}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Canopy tile */}
      <section className="on-dark bg-canopy px-6 py-20 text-center max-sm:px-4 max-sm:py-14">
        <div data-reveal className="mx-auto max-w-2xl">
          <h2 className="text-[40px] leading-[1.1] tracking-[-0.5px] max-sm:text-[30px]">Your files stay with you.</h2>
          <p className="mt-4 text-[21px] font-light leading-[1.5] text-mint max-sm:text-[17px]">
            Projects are saved as .tct files on your own computer. There are no accounts, and the tool keeps no
            copy of your projects.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-3">
            <Link href="/tool" className="btn btn-on-dark">
              Start a project
            </Link>
            <Link href="/privacy" className="btn border border-white/30 text-white hover:bg-white/10">
              Read the privacy note
            </Link>
          </div>
        </div>
      </section>
    </SiteFrame>
  );
}
