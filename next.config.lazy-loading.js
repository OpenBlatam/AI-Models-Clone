/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable experimental features for better lazy loading
  experimental: {
    // Enable concurrent features
    concurrentFeatures: true,
    // Enable server components
    serverComponentsExternalPackages: [],
  },

  // Webpack configuration for optimal code splitting
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Optimize chunk splitting
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        // Vendor chunks for third-party libraries
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        // Common chunks for shared components
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5,
          reuseExistingChunk: true,
        },
        // Analytics chunk
        analytics: {
          test: /[\\/]components[\\/]analytics[\\/]/,
          name: 'analytics',
          chunks: 'all',
          priority: 20,
        },
        // Admin chunk
        admin: {
          test: /[\\/]components[\\/]admin[\\/]/,
          name: 'admin',
          chunks: 'all',
          priority: 20,
        },
        // User chunk
        user: {
          test: /[\\/]components[\\/]user[\\/]/,
          name: 'user',
          chunks: 'all',
          priority: 20,
        },
        // Settings chunk
        settings: {
          test: /[\\/]components[\\/]settings[\\/]/,
          name: 'settings',
          chunks: 'all',
          priority: 20,
        },
        // Chat chunk
        chat: {
          test: /[\\/]components[\\/]chat[\\/]/,
          name: 'chat',
          chunks: 'all',
          priority: 20,
        },
      },
    };

    // Optimize module resolution
    config.resolve.alias = {
      ...config.resolve.alias,
      // Add aliases for better tree shaking
      '@components': path.resolve(__dirname, 'components'),
      '@lib': path.resolve(__dirname, 'lib'),
      '@utils': path.resolve(__dirname, 'utils'),
    };

    // Enable tree shaking
    config.optimization.usedExports = true;
    config.optimization.sideEffects = false;

    // Optimize bundle size
    config.optimization.minimize = !dev;
    
    if (!dev) {
      config.optimization.minimizer.push(
        new webpack.optimize.ModuleConcatenationPlugin()
      );
    }

    return config;
  },

  // Enable compression
  compress: true,

  // Enable gzip compression
  generateEtags: false,

  // Optimize images
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Enable SWC minification
  swcMinify: true,

  // Configure headers for caching
  async headers() {
    return [
      {
        source: '/_next/static/chunks/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/static/css/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },

  // Configure redirects for better performance
  async redirects() {
    return [
      // Redirect old routes to new lazy-loaded routes
      {
        source: '/old-analytics',
        destination: '/analytics',
        permanent: true,
      },
    ];
  },

  // Configure rewrites for API routes
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },

  // Environment variables for lazy loading
  env: {
    ENABLE_LAZY_LOADING: 'true',
    LAZY_LOADING_TIMEOUT: '5000',
    ENABLE_PERFORMANCE_MONITORING: 'true',
  },

  // TypeScript configuration
  typescript: {
    // Enable strict mode for better type safety
    ignoreBuildErrors: false,
  },

  // ESLint configuration
  eslint: {
    // Enable ESLint during builds
    ignoreDuringBuilds: false,
  },

  // Experimental features for better performance
  experimental: {
    // Enable concurrent features
    concurrentFeatures: true,
    // Enable server components
    serverComponentsExternalPackages: [],
    // Enable optimizeCss
    optimizeCss: true,
    // Enable scrollRestoration
    scrollRestoration: true,
    // Enable legacyBrowsers
    legacyBrowsers: false,
    // Enable browsersListForSwc
    browsersListForSwc: true,
  },
};

module.exports = nextConfig; 