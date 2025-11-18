
import("./env.mjs");

/** @type {import('next').NextConfig} */
const nextConfig = {
  // React and development settings
  reactStrictMode: true,
  swcMinify: true,
  
  // Experimental features for performance
  experimental: {
    optimizeCss: true,
    optimizePackageImports: [
      'lucide-react',
      '@radix-ui/react-icons',
      'framer-motion',
      'react-hook-form',
      'zustand',
      '@tanstack/react-query'
    ],
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
    // Server actions
    serverActions: {
      bodySizeLimit: '2mb',
    },
    // Optimize images
    optimizePackageImports: ['lucide-react'],
    // Bundle analyzer
    bundlePagesExternals: true,
  },

  // Image optimization
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
        port: '',
        pathname: '/**',
      },
    ],
  },

  // Webpack configuration
  webpack: (config, { dev, isServer }) => {
    // Optimize bundle splitting
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5,
          reuseExistingChunk: true,
        },
        // Separate large libraries
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          chunks: 'all',
          priority: 20,
        },
        ui: {
          test: /[\\/]node_modules[\\/](@radix-ui|lucide-react|framer-motion)[\\/]/,
          name: 'ui',
          chunks: 'all',
          priority: 15,
        },
      },
    };

    // SVG handling
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });

    // Bundle analyzer
    if (process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: 'bundle-report.html',
        })
      );
    }

    // Performance hints
    config.performance = {
      hints: dev ? false : 'warning',
      maxEntrypointSize: 512000,
      maxAssetSize: 512000,
    };

    return config;
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          // Security headers
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
          },
          // Performance headers
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      // API routes with different caching
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
        ],
      },
      // Static assets with long-term caching
      {
        source: '/_next/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },

  // Redirects
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
      {
        source: '/old-blog/:slug*',
        destination: '/blog/:slug*',
        permanent: true,
      },
    ];
  },

  // Rewrites for API proxying
  async rewrites() {
    return [
      {
        source: '/api/external/:path*',
        destination: `${process.env.EXTERNAL_API_URL}/:path*`,
      },
    ];
  },

  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  // PWA support
  ...(process.env.NODE_ENV === 'production' && {
    async generateBuildId() {
      return 'build-' + Date.now();
    },
  }),

  // Compression
  compress: true,

  // Powered by header
  poweredByHeader: false,

  // Trailing slash
  trailingSlash: false,

  // Base path
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',

  // Asset prefix
  assetPrefix: process.env.NEXT_PUBLIC_ASSET_PREFIX || '',

  // Output configuration
  output: 'standalone',

  // Transpile packages
  transpilePackages: [
    '@radix-ui/react-icons',
    'lucide-react',
    'framer-motion',
    'zustand',
    '@tanstack/react-query',
  ],

  // TypeScript configuration
  typescript: {
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    ignoreBuildErrors: false,
  },

  // ESLint configuration
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: false,
  },

  // Bundle analyzer
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config) => {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: 'bundle-report.html',
        })
      );
      return config;
    },
  }),
};

module.exports = nextConfig;
