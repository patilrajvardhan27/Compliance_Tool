import type { NextConfig } from "next";

// Sent on every page: force HTTPS (HSTS), block MIME sniffing and framing.
const securityHeaders = [
  { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
];

const nextConfig: NextConfig = {
  // Self-contained server bundle (server.js + only the node_modules it actually needs) so Azure
  // App Service deploys receive a prebuilt artifact and never run `npm install`/`next build` on
  // the server -- that Oryx build was blowing past Kudu's ~230s synchronous deploy timeout on the
  // B1 plan and leaving the container crash-looping with a half-built `.next`.
  output: "standalone",
  agentRules: false,
  poweredByHeader: false,
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
