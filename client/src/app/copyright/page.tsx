import type { Metadata } from "next";
import Link from "next/link";

import { DocumentSection, SiteDocument } from "@/components/site/SiteFrame";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Copyright — TUNBEEC" };

export default function Copyright() {
  return (
    <SiteDocument
      title="Copyright and terms of use"
      summary="Who owns the tool, what you may do with its results, and the limits of what it can tell you."
    >
      <DocumentSection title="Copyright">
        <p>
          © {SITE.year} {SITE.owner}. All rights reserved.
        </p>
        <p>
          The software, interface design, text and intro video on this site are protected by copyright. You may
          use the tool and include its reports in your own project documents. Copying or redistributing the
          software or site content needs written permission.
        </p>
      </DocumentSection>

      <DocumentSection title="Third-party material">
        <p>
          The Tunisian building energy code belongs to the authority that publishes it. DOE-2.2, used for the
          performance check, is the property of its respective owners. Neither is covered by the notice above.
        </p>
      </DocumentSection>

      <DocumentSection title="No warranty">
        <p>
          The tool is provided as is. Its reports help you assess a design against the code, but they are not an
          official compliance certificate and do not replace review by the responsible authority or a licensed
          professional. Results depend on the data you enter. The University of Colorado accepts no liability
          for decisions made from them.
        </p>
      </DocumentSection>

      <DocumentSection title="Permissions">
        <p>
          To ask about reuse or licensing, write to the lab through the <Link href="/contact">contact page</Link>.
        </p>
      </DocumentSection>
    </SiteDocument>
  );
}
