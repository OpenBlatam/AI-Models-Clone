import("./env.mjs");

// ============================================================================
// CONSTANTS
// ============================================================================

// Package constants
const SHARED_PACKAGES = [
  '@radix-ui/react-icons',
  'lucide-react',
  'framer-motion',
  'zustand',
  '@tanstack/react-query',
];

const OPTIMIZED_PACKAGES = [...SHARED_PACKAGES, 'react-hook-form'];
const TRANSPILE_PACKAGES = SHARED_PACKAGES;

// Security header constants
const SECURITY_HEADER_KEYS = {
  X_FRAME_OPTIONS: 'X-Frame-Options',
  X_CONTENT_TYPE_OPTIONS: 'X-Content-Type-Options',
  X_XSS_PROTECTION: 'X-XSS-Protection',
  REFERRER_POLICY: 'Referrer-Policy',
  PERMISSIONS_POLICY: 'Permissions-Policy',
};

const SECURITY_HEADER_VALUES = {
  DENY: 'DENY',
  NOSNIFF: 'nosniff',
  XSS_BLOCK: '1; mode=block',
  REFERRER_STRICT: 'strict-origin-when-cross-origin',
  PERMISSIONS_RESTRICTED: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
};

/**
 * Creates a security header object
 * @param {string} key - Header key
 * @param {string} value - Header value
 * @returns {Object} Header object
 */
const createSecurityHeader = (key, value) => ({ key, value });

/**
 * Creates security headers array from key-value pairs
 * @param {Array<Array<string>>} headerPairs - Array of [key, value] pairs
 * @returns {Array<Object>} Array of security header objects
 */
const createSecurityHeaders = (headerPairs) =>
  headerPairs.map(([key, value]) => createSecurityHeader(key, value));

// Security headers configuration
const SECURITY_HEADER_PAIRS = [
  [SECURITY_HEADER_KEYS.X_FRAME_OPTIONS, SECURITY_HEADER_VALUES.DENY],
  [SECURITY_HEADER_KEYS.X_CONTENT_TYPE_OPTIONS, SECURITY_HEADER_VALUES.NOSNIFF],
  [SECURITY_HEADER_KEYS.X_XSS_PROTECTION, SECURITY_HEADER_VALUES.XSS_BLOCK],
  [SECURITY_HEADER_KEYS.REFERRER_POLICY, SECURITY_HEADER_VALUES.REFERRER_STRICT],
  [SECURITY_HEADER_KEYS.PERMISSIONS_POLICY, SECURITY_HEADER_VALUES.PERMISSIONS_RESTRICTED],
];

// Security headers
const SECURITY_HEADERS = createSecurityHeaders(SECURITY_HEADER_PAIRS);

// Cache control values
const CACHE_CONTROL = {
  IMMUTABLE: 'public, max-age=31536000, immutable',
  NO_CACHE: 'no-cache, no-store, must-revalidate',
};

// Image configuration constants
const IMAGE_CONSTANTS = {
  FORMATS: ['image/webp', 'image/avif'],
  DEVICE_SIZES: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  IMAGE_SIZES: [16, 32, 48, 64, 96, 128, 256, 384],
  MIN_CACHE_TTL: 60,
  CSP: "default-src 'self'; script-src 'none'; sandbox;",
  REMOTE_PROTOCOL: 'https',
  REMOTE_HOSTNAME: '**',
  REMOTE_PATHNAME: '/**',
};

/**
 * Creates a remote pattern for image configuration
 * @param {string} protocol - Protocol (https/http)
 * @param {string} hostname - Hostname pattern
 * @param {string} pathname - Pathname pattern
 * @returns {Object} Remote pattern configuration
 */
const createRemotePattern = (protocol, hostname, pathname) => ({
  protocol,
  hostname,
  port: '',
  pathname,
});

// Image configuration
const IMAGE_CONFIG = {
  formats: IMAGE_CONSTANTS.FORMATS,
  deviceSizes: IMAGE_CONSTANTS.DEVICE_SIZES,
  imageSizes: IMAGE_CONSTANTS.IMAGE_SIZES,
  minimumCacheTTL: IMAGE_CONSTANTS.MIN_CACHE_TTL,
  contentSecurityPolicy: IMAGE_CONSTANTS.CSP,
  remotePatterns: [
    createRemotePattern(
      IMAGE_CONSTANTS.REMOTE_PROTOCOL,
      IMAGE_CONSTANTS.REMOTE_HOSTNAME,
      IMAGE_CONSTANTS.REMOTE_PATHNAME
    ),
  ],
};

/**
 * Creates a redirect configuration
 * @param {string} source - Source path
 * @param {string} destination - Destination path
 * @param {boolean} permanent - Whether redirect is permanent
 * @returns {Object} Redirect configuration
 */
const createRedirect = (source, destination, permanent = true) => ({
  source,
  destination,
  permanent,
});

// Redirects configuration
const REDIRECTS = [
  createRedirect('/home', '/'),
  createRedirect('/old-blog/:slug*', '/blog/:slug*'),
];

/**
 * Creates a cache group configuration
 * @param {Object} options - Cache group options
 * @param {RegExp} options.test - Test pattern for matching modules
 * @param {string} options.name - Name of the cache group
 * @param {number} options.priority - Priority of the cache group
 * @param {number} [options.minChunks] - Minimum chunks for common group
 * @param {boolean} [options.reuseExistingChunk] - Reuse existing chunk
 * @returns {Object} Cache group configuration
 */
const createCacheGroup = ({
  test,
  name,
  priority,
  minChunks,
  reuseExistingChunk = false,
}) => ({
  ...(test && { test }),
  name,
  chunks: CACHE_GROUP_CONFIG.CHUNKS_ALL,
  priority,
  ...(minChunks && { minChunks }),
  ...(reuseExistingChunk && { reuseExistingChunk }),
});

// Webpack cache groups configuration
const CACHE_GROUPS = {
  react: createCacheGroup({
    test: CONSTANTS.REACT_MODULES,
    name: 'react',
    priority: CACHE_PRIORITIES.REACT,
  }),
  ui: createCacheGroup({
    test: CONSTANTS.UI_MODULES,
    name: 'ui',
    priority: CACHE_PRIORITIES.UI,
  }),
  vendor: createCacheGroup({
    test: CONSTANTS.NODE_MODULES_PATH,
    name: 'vendors',
    priority: CACHE_PRIORITIES.VENDOR,
  }),
  common: createCacheGroup({
    name: 'common',
    priority: CACHE_PRIORITIES.COMMON,
    minChunks: CACHE_GROUP_CONFIG.MIN_CHUNKS,
    reuseExistingChunk: true,
  }),
};

// Webpack performance constants
const WEBPACK_PERFORMANCE_CONSTANTS = {
  MAX_ENTRYPOINT_SIZE: 512000,
  MAX_ASSET_SIZE: 512000,
};

// Webpack performance configuration
const WEBPACK_PERFORMANCE = {
  maxEntrypointSize: WEBPACK_PERFORMANCE_CONSTANTS.MAX_ENTRYPOINT_SIZE,
  maxAssetSize: WEBPACK_PERFORMANCE_CONSTANTS.MAX_ASSET_SIZE,
};


// Turbo constants
const TURBO_CONSTANTS = {
  SVG_PATTERN: '*.svg',
  SVG_AS: '*.js',
};

/**
 * Creates turbo configuration
 * @returns {Object} Turbo configuration
 */
const createTurboConfig = () => ({
  rules: {
    [TURBO_CONSTANTS.SVG_PATTERN]: {
      loaders: [CONSTANTS.SVG_LOADER],
      as: TURBO_CONSTANTS.SVG_AS,
    },
  },
});

// Turbo configuration
const TURBO_CONFIG = createTurboConfig();

// Server actions constants
const SERVER_ACTIONS_CONSTANTS = {
  BODY_SIZE_LIMIT: '2mb',
};

// Server actions configuration
const SERVER_ACTIONS_CONFIG = {
  bodySizeLimit: SERVER_ACTIONS_CONSTANTS.BODY_SIZE_LIMIT,
};

// Header route patterns
const HEADER_ROUTES = {
  ALL: '/(.*)',
  API: '/api/(.*)',
  STATIC: '/_next/static/(.*)',
};

// Constants for magic numbers/strings
const CONSTANTS = {
  BUILD_ID_PREFIX: 'build-',
  SVG_LOADER: '@svgr/webpack',
  SVG_TEST: /\.svg$/,
  CHUNKS_ALL: 'all',
  WEBPACK_HINT_WARNING: 'warning',
  WEBPACK_HINT_FALSE: false,
  CACHE_CONTROL_KEY: 'Cache-Control',
  API_EXTERNAL_PATH: '/api/external/:path*',
  NODE_MODULES_PATH: /[\\/]node_modules[\\/]/,
  REACT_MODULES: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
  UI_MODULES: /[\\/]node_modules[\\/](@radix-ui|lucide-react|framer-motion)[\\/]/,
};

// Cache group priorities
const CACHE_PRIORITIES = {
  REACT: 20,
  UI: 15,
  VENDOR: 10,
  COMMON: 5,
};

// Cache group configuration
const CACHE_GROUP_CONFIG = {
  MIN_CHUNKS: 2,
  CHUNKS_ALL: CONSTANTS.CHUNKS_ALL,
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

// Environment variable keys
const ENV_KEYS = {
  CUSTOM_KEY: 'CUSTOM_KEY',
  NEXT_PUBLIC_APP_URL: 'NEXT_PUBLIC_APP_URL',
  NEXT_PUBLIC_API_URL: 'NEXT_PUBLIC_API_URL',
  EXTERNAL_API_URL: 'EXTERNAL_API_URL',
  NODE_ENV: 'NODE_ENV',
  ANALYZE: 'ANALYZE',
  NEXT_PUBLIC_BASE_PATH: 'NEXT_PUBLIC_BASE_PATH',
  NEXT_PUBLIC_ASSET_PREFIX: 'NEXT_PUBLIC_ASSET_PREFIX',
};

/**
 * Gets environment variable by key
 * @param {string} key - Environment variable key from ENV_KEYS
 * @returns {string|undefined} Environment variable value
 */
const getEnvVar = (key) => process.env[key];

/**
 * Gets environment variable with fallback
 * @param {string} key - Environment variable key
 * @param {string} fallback - Fallback value
 * @returns {string} Environment variable value or fallback
 */
const getEnv = (key, fallback = BUILD_CONSTANTS.EMPTY_STRING) =>
  getEnvVar(key) || fallback;

/**
 * Conditionally applies configuration based on condition
 * @param {boolean} condition - Condition to check
 * @param {Object|Function} config - Configuration object or function
 * @returns {Object} Configuration object or empty object
 */
const conditionalConfig = (condition, config) =>
  condition ? (typeof config === 'function' ? config() : config) : {};

/**
 * Merges multiple configuration objects
 * @param {...Object} configs - Configuration objects to merge
 * @returns {Object} Merged configuration object
 */
const mergeConfigs = (...configs) => Object.assign({}, ...configs);

// Environment flags
const isProduction = getEnvVar(ENV_KEYS.NODE_ENV) === 'production';
const isAnalyze = getEnvVar(ENV_KEYS.ANALYZE) === 'true';

// ============================================================================
// CONFIGURATION OBJECTS
// ============================================================================

/**
 * Environment variables helper
 * @returns {Object} Environment variables object
 */
const getEnvVars = () => ({
  CUSTOM_KEY: getEnvVar(ENV_KEYS.CUSTOM_KEY),
  NEXT_PUBLIC_APP_URL: getEnvVar(ENV_KEYS.NEXT_PUBLIC_APP_URL),
  NEXT_PUBLIC_API_URL: getEnvVar(ENV_KEYS.NEXT_PUBLIC_API_URL),
});

// TypeScript/ESLint constants
const LINT_CONSTANTS = {
  IGNORE_BUILD_ERRORS: false,
  IGNORE_DURING_BUILDS: false,
};

// TypeScript configuration
const TYPESCRIPT_CONFIG = {
  ignoreBuildErrors: LINT_CONSTANTS.IGNORE_BUILD_ERRORS,
};

// ESLint configuration
const ESLINT_CONFIG = {
  ignoreDuringBuilds: LINT_CONSTANTS.IGNORE_DURING_BUILDS,
};

// Experimental configuration constants
const EXPERIMENTAL_CONSTANTS = {
  OPTIMIZE_CSS: true,
  BUNDLE_PAGES_EXTERNALS: true,
};

/**
 * Creates experimental configuration
 * @returns {Object} Experimental configuration
 */
const createExperimentalConfig = () => ({
  optimizeCss: EXPERIMENTAL_CONSTANTS.OPTIMIZE_CSS,
  optimizePackageImports: OPTIMIZED_PACKAGES,
  turbo: TURBO_CONFIG,
  serverActions: SERVER_ACTIONS_CONFIG,
  bundlePagesExternals: EXPERIMENTAL_CONSTANTS.BUNDLE_PAGES_EXTERNALS,
});

// Experimental configuration
const EXPERIMENTAL_CONFIG = createExperimentalConfig();

// Build configuration constants
const BUILD_CONSTANTS = {
  OUTPUT_STANDALONE: 'standalone',
  EMPTY_STRING: '',
};

// Build configuration
const BUILD_CONFIG = {
  compress: true,
  poweredByHeader: false,
  trailingSlash: false,
  output: BUILD_CONSTANTS.OUTPUT_STANDALONE,
  basePath: getEnv(ENV_KEYS.NEXT_PUBLIC_BASE_PATH),
  assetPrefix: getEnv(ENV_KEYS.NEXT_PUBLIC_ASSET_PREFIX),
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Creates split chunks configuration
 * @returns {Object} Split chunks configuration
 */
const createSplitChunksConfig = () => ({
  chunks: CONSTANTS.CHUNKS_ALL,
  cacheGroups: CACHE_GROUPS,
});

/**
 * Creates SVG rule configuration
 * @returns {Object} SVG rule configuration
 */
const createSVGRule = () => ({
  test: CONSTANTS.SVG_TEST,
  use: [CONSTANTS.SVG_LOADER],
});

// Bundle analyzer constants
const BUNDLE_ANALYZER_CONSTANTS = {
  MODE: 'static',
  REPORT_FILENAME: 'bundle-report.html',
  OPEN_ANALYZER: false,
};

// Bundle analyzer configuration
const BUNDLE_ANALYZER_CONFIG = {
  analyzerMode: BUNDLE_ANALYZER_CONSTANTS.MODE,
  openAnalyzer: BUNDLE_ANALYZER_CONSTANTS.OPEN_ANALYZER,
  reportFilename: BUNDLE_ANALYZER_CONSTANTS.REPORT_FILENAME,
};

/**
 * Adds bundle analyzer plugin if enabled
 * @param {Object} config - Webpack config object
 */
const addBundleAnalyzer = (config) => {
  if (isAnalyze) {
    const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
    config.plugins.push(new BundleAnalyzerPlugin(BUNDLE_ANALYZER_CONFIG));
  }
};

/**
 * Creates performance configuration
 * @param {boolean} dev - Development mode flag
 * @returns {Object} Performance configuration
 */
const createPerformanceConfig = (dev) => ({
  hints: dev ? CONSTANTS.WEBPACK_HINT_FALSE : CONSTANTS.WEBPACK_HINT_WARNING,
  ...WEBPACK_PERFORMANCE,
});

/**
 * Creates webpack configuration with optimizations
 * @param {Object} config - Webpack config object
 * @param {Object} options - Webpack options
 * @param {boolean} options.dev - Development mode flag
 * @returns {Object} Modified webpack config
 */
const createWebpackConfig = (config, { dev }) => {
  // Bundle splitting
  config.optimization.splitChunks = createSplitChunksConfig();

  // SVG handling
  config.module.rules.push(createSVGRule());

  // Bundle analyzer (conditional)
  addBundleAnalyzer(config);

  // Performance hints
  config.performance = createPerformanceConfig(dev);

  return config;
};

/**
 * Creates a cache control header
 * @param {string} value - Cache control value
 * @returns {Object} Header object
 */
const createCacheControlHeader = (value) => ({
  key: CONSTANTS.CACHE_CONTROL_KEY,
  value,
});

/**
 * Creates a header configuration object
 * @param {string} source - Source route pattern
 * @param {Array} headers - Array of header objects
 * @returns {Object} Header configuration
 */
const createHeaderConfig = (source, headers) => ({
  source,
  headers,
});

/**
 * Creates default headers for all routes
 * @returns {Array} Array of header objects
 */
const createDefaultHeaders = () => [
  ...SECURITY_HEADERS,
  createCacheControlHeader(CACHE_CONTROL.IMMUTABLE),
];

/**
 * Creates header configurations from definitions
 * @param {Array<Array>} headerDefs - Array of [source, headers] tuples
 * @returns {Array<Object>} Array of header configurations
 */
const createHeaderConfigs = (headerDefs) =>
  headerDefs.map(([source, headers]) => createHeaderConfig(source, headers));

/**
 * Creates headers configuration for Next.js
 * @param {Array} [additionalHeaders=[]] - Additional header configurations
 * @returns {Array} Array of header configurations
 */
const createHeaders = (additionalHeaders = []) => {
  const defaultHeaderDefs = [
    [HEADER_ROUTES.ALL, createDefaultHeaders()],
    [HEADER_ROUTES.API, [createCacheControlHeader(CACHE_CONTROL.NO_CACHE)]],
    [HEADER_ROUTES.STATIC, [createCacheControlHeader(CACHE_CONTROL.IMMUTABLE)]],
  ];

  return [...additionalHeaders, ...createHeaderConfigs(defaultHeaderDefs)];
};

/**
 * Creates a rewrite rule
 * @param {string} source - Source path pattern
 * @param {string} destination - Destination URL
 * @returns {Object} Rewrite configuration
 */
const createRewrite = (source, destination) => ({
  source,
  destination,
});

/**
 * Creates rewrite configuration for API proxying
 * @param {Array} [additionalRewrites=[]] - Additional rewrite configurations
 * @returns {Array} Array of rewrite configurations
 */
const createRewrites = (additionalRewrites = []) => {
  const rewrites = [...additionalRewrites];
  const externalApiUrl = getEnvVar(ENV_KEYS.EXTERNAL_API_URL);

  if (externalApiUrl) {
    rewrites.push(
      createRewrite(
        CONSTANTS.API_EXTERNAL_PATH,
        `${externalApiUrl}/:path*`
      )
    );
  }

  return rewrites;
};

// Image configuration constants
const IMAGE_CONFIG_CONSTANTS = {
  DANGEROUSLY_ALLOW_SVG: true,
};

/**
 * Creates image configuration with defaults
 * @returns {Object} Image configuration object
 */
const createImageConfig = () => ({
  ...IMAGE_CONFIG,
  dangerouslyAllowSVG: IMAGE_CONFIG_CONSTANTS.DANGEROUSLY_ALLOW_SVG,
});

/**
 * Generates build ID for production builds
 * @returns {string} Build ID string
 */
const generateBuildId = () => `${CONSTANTS.BUILD_ID_PREFIX}${Date.now()}`;

/**
 * Creates production-only configuration
 * @returns {Object} Production configuration object
 */
const createProductionConfig = () => ({
  async generateBuildId() {
    return generateBuildId();
  },
});

// ============================================================================
// NEXT.JS CONFIGURATION
// ============================================================================

// Base configuration constants
const BASE_CONFIG_CONSTANTS = {
  REACT_STRICT_MODE: true,
  SWC_MINIFY: true,
};

/**
 * Creates base Next.js configuration
 * @returns {Object} Base configuration object
 */
const createBaseConfig = () => ({
  reactStrictMode: BASE_CONFIG_CONSTANTS.REACT_STRICT_MODE,
  swcMinify: BASE_CONFIG_CONSTANTS.SWC_MINIFY,
  experimental: EXPERIMENTAL_CONFIG,
  images: createImageConfig(),
  webpack: createWebpackConfig,
  env: getEnvVars(),
  transpilePackages: TRANSPILE_PACKAGES,
  typescript: TYPESCRIPT_CONFIG,
  eslint: ESLINT_CONFIG,
});


/**
 * Next.js configuration object
 * @type {import('next').NextConfig}
 */
const nextConfig = mergeConfigs(
  createBaseConfig(),
  createAsyncConfig(),
  BUILD_CONFIG,
  conditionalConfig(isProduction, createProductionConfig)
);

// ============================================================================
// EXPORT
// ============================================================================

module.exports = nextConfig;
