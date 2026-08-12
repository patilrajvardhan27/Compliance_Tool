import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { BuildingInputProvider } from "@/providers/BuildingInputProvider";
import { QueryProvider } from "@/providers/QueryProvider";
import { ReferenceDataProvider } from "@/providers/ReferenceDataProvider";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TUNBEEC",
  description: "Tunisian building energy code compliance tool",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <QueryProvider>
          <ReferenceDataProvider>
            <BuildingInputProvider>{children}</BuildingInputProvider>
          </ReferenceDataProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
