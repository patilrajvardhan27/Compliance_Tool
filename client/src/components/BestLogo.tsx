import Image from "next/image";

/** BEST Center wordmark, linking to best-iucrc.org. Served from /public. */
export function BestLogo({ height = 32, className = "" }: { height?: number; className?: string }) {
  return (
    <a
      href="https://best-iucrc.org"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="BEST Center website"
      className={`shrink-0 ${className}`}
    >
      <Image
        src="/best-logo.png"
        alt="BEST Center"
        width={Math.round(height * 4.4)}
        height={height}
        unoptimized
        style={{ height, width: "auto" }}
      />
    </a>
  );
}
