import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  // Add rewrites to proxy API requests to the backend
  // This solves CORS issues by making requests appear to come from the same origin
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },

  // Allow images from external sources (Seoul event images)
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
  },
};

export default nextConfig;
