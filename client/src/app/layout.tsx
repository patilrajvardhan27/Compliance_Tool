import type { Metadata } from "next";
import { Work_Sans } from "next/font/google";

import { RevealObserver } from "@/components/RevealObserver";

import "./globals.css";

// Work Sans is the BEST Center typeface (best-iucrc.org).
const workSans = Work_Sans({
  variable: "--font-work-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "TUNBEEC",
  description: "Tunisian building energy code compliance tool",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full">
      <body className={`${workSans.variable} flex min-h-full flex-col font-sans antialiased`}>
        <RevealObserver />
        {children}
      </body>
    </html>
  );
}
