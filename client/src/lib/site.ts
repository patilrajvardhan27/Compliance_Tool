/** Identity and contact details shared by the landing page and the legal pages. */
export const SITE = {
  name: "TUNBEEC",
  tagline: "Tunisian Building Energy Efficiency Code",
  owner: "The Regents of the University of Colorado",
  year: 2026,
  lab: {
    name: "Larson Building Systems Laboratory",
    address: ["CU Boulder Engineering Center", "1111 Engineering Drive, UCB 428", "Boulder, CO 80309"],
    phone: "303-532-6546",
    contactUrl: "https://www.colorado.edu/lab/lbsl/contact",
  },
} as const;

export const SITE_LINKS = [
  { href: "/privacy", label: "Privacy" },
  { href: "/copyright", label: "Copyright" },
  { href: "/contact", label: "Contact" },
] as const;
