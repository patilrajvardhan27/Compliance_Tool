import type { Metadata } from "next";
import Link from "next/link";

import { DocumentSection, SiteDocument } from "@/components/site/SiteFrame";

export const metadata: Metadata = { title: "Privacy — TUNBEEC" };

export default function Privacy() {
  return (
    <SiteDocument
      title="Privacy policy"
      summary="TUNBEEC has no accounts and asks for no personal information. This page describes what happens to the building data you enter."
    >
      <DocumentSection title="Your project files stay with you">
        <p>
          Projects are saved as <strong>.tct</strong> files on your own computer. The tool does not keep a copy
          of your projects and has no project list on the server.
        </p>
        <p>
          Opening or saving a file sends its contents to our server to be converted. The conversion happens in a
          temporary folder that is deleted as soon as the response is sent.
        </p>
      </DocumentSection>

      <DocumentSection title="What is sent when you run a check">
        <p>
          Running the prescriptive or performance check sends the building description on screen to our server,
          which calculates the result and returns it.
        </p>
        <p>
          The performance check runs DOE-2.2 on the server. To do that it writes simulation input and output
          files, named after your project, to a working folder. These files can remain on the server after the
          run. They describe the building, not you, so avoid putting personal information in the building or
          project name.
        </p>
      </DocumentSection>

      <DocumentSection title="What we do not do">
        <ul>
          <li>No sign-in, no user accounts.</li>
          <li>No cookies and nothing saved in your browser&apos;s storage.</li>
          <li>No analytics, advertising or tracking scripts.</li>
          <li>No third-party fonts or embeds; the intro video is served from this site.</li>
        </ul>
      </DocumentSection>

      <DocumentSection title="Hosting logs">
        <p>
          The site and its server run on Microsoft Azure. As with any website, the host records standard request
          logs (IP address, time, the page requested and browser type) for security and troubleshooting.
        </p>
      </DocumentSection>

      <DocumentSection title="Changes and questions">
        <p>
          If the tool starts handling data differently, this page will be updated first. Questions go to the lab
          through the <Link href="/contact">contact page</Link>.
        </p>
        <p className="font-mono text-xs">Last updated October 2026</p>
      </DocumentSection>
    </SiteDocument>
  );
}
