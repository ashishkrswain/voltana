import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow the dev server to be loaded from LAN devices (e.g. the Android phone
  // testing the app). Next.js blocks cross-origin dev resources by default.
  // NOTE: wildcard "*" does NOT match bare-IP origins, so the LAN IP is listed
  // explicitly. Update if your PC's Wi-Fi IP changes.
  allowedDevOrigins: ["192.168.20.48"],
};

export default nextConfig;
