import type { Metadata } from "next";

import { DocumentSection, SiteDocument } from "@/components/site/SiteFrame";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Contact — TUNBEEC" };

export default function Contact() {
  return (
    <SiteDocument
      title="Contact"
      summary="The web version of TUNBEEC is built and maintained at the Larson Building Systems Laboratory, CU Boulder."
    >
      <DocumentSection title="Get in touch">
        <p>Questions, collaboration requests and bug reports go through the lab&apos;s contact form.</p>
        <p>
          <a href={SITE.lab.contactUrl} target="_blank" rel="noreferrer">
            Open the lab contact page
          </a>
        </p>
      </DocumentSection>

      <DocumentSection title="Address">
        <address className="not-italic">
          <strong>{SITE.lab.name}</strong>
          {SITE.lab.address.map((line) => (
            <span key={line} className="block">
              {line}
            </span>
          ))}
          <a href={`tel:+1-${SITE.lab.phone}`} className="nums mt-2 block">
            {SITE.lab.phone}
          </a>
        </address>
      </DocumentSection>

      <DocumentSection title="Reporting a problem">
        <p>It helps to include:</p>
        <ul>
          <li>which check you ran (prescriptive or performance),</li>
          <li>the message shown on screen, word for word,</li>
          <li>the .tct project file, if you are able to share it.</li>
        </ul>
      </DocumentSection>
    </SiteDocument>
  );
}
