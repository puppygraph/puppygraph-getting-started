import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const puppygraphHost = process.env.PUPPYGRAPH_HOST || 'localhost';
    const destination = `http://${puppygraphHost}:8081/:path*`;
    console.log(`[Next.js Rewrite] Using PuppyGraph host: ${puppygraphHost}, destination: ${destination}`);
    return [
      {
        source: '/api/puppygraph/:path*',
        destination,
      },
    ];
  },
};

export default nextConfig;
