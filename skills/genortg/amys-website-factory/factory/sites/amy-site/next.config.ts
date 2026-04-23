import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Dev-only safety: allow dev resources to be loaded when accessing the dev
  // server via LAN hostnames/IPs.
  allowedDevOrigins: [
    "localhost",
    "127.0.0.1",
    "genorbox1",
    "192.168.1.238",
  ],
};

export default nextConfig;
