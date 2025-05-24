const { withContentlayer } = require("next-contentlayer2");

import("./env.mjs");

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "avatars.githubusercontent.com",
      },
      {
        protocol: "https",
        hostname: "lh3.googleusercontent.com",
      },
      {
        protocol: "https",
        hostname: "randomuser.me",
      },
    ],
    domains: ['avatars.githubusercontent.com', 'lh3.googleusercontent.com'],
  },
  experimental: {
    // serverActions está habilitado por defecto en Next.js 14
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Don't resolve 'canvas' package on the client to prevent this error on build --> Error: Can't resolve 'canvas'
      config.resolve.fallback = {
        ...config.resolve.fallback,
        canvas: false,
      };
    }

    // Add specific handling for react-konva
    config.resolve.alias = {
      ...config.resolve.alias,
      'react-konva': 'react-konva/lib/ReactKonva',
      'konva': 'konva/lib/index-umd',
    };

    return config;
  },
};

module.exports = withContentlayer(nextConfig);
