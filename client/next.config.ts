import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Self-contained server bundle (server.js + only the node_modules it actually needs) so Azure
  // App Service deploys receive a prebuilt artifact and never run `npm install`/`next build` on
  // the server -- that Oryx build was blowing past Kudu's ~230s synchronous deploy timeout on the
  // B1 plan and leaving the container crash-looping with a half-built `.next`.
  output: "standalone",
};

export default nextConfig;
