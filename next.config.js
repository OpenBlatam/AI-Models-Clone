const { withContentlayer } = require("next-contentlayer2");

import("./env.mjs");

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
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
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "example.com",
      },
      {
        protocol: "https",
        hostname: "blatamcursos.s3.amazonaws.com",
      },
    ],
    domains: ['avatars.githubusercontent.com', 'lh3.googleusercontent.com', 'images.unsplash.com', 'example.com', 'blatamcursos.s3.amazonaws.com'],
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
