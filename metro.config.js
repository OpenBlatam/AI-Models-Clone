const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// ============================================================================
// PERFORMANCE OPTIMIZATIONS
// ============================================================================

// Enable CSS support with optimization
config.transformer.babelTransformerPath = require.resolve('react-native-css-transformer');

// Add support for additional file extensions
config.resolver.sourceExts.push('css');

// Configure asset handling with optimization
config.resolver.assetExts.push('db', 'mp3', 'ttf', 'obj', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp');

// Enable symlinks for better development experience
config.resolver.enableSymlinks = true;

// Configure watchman for better file watching
config.watchFolders = [__dirname];

// ============================================================================
// BUNDLE OPTIMIZATIONS
// ============================================================================

// Enable tree shaking and dead code elimination
config.transformer.minifierConfig = {
  keep_fnames: true,
  mangle: {
    keep_fnames: true,
  },
  output: {
    ascii_only: true,
    quote_style: 3,
    wrap_iife: true,
  },
  compress: {
    reduce_funcs: false,
  },
};

// Optimize resolver for faster module resolution
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

// Enable Hermes engine optimizations
config.transformer.enableBabelRCLookup = false;
config.transformer.enableBabelRuntime = false;

// Configure asset optimization
config.transformer.assetPlugins = ['expo-asset/tools/hashAssetFiles'];

// ============================================================================
// CACHE OPTIMIZATIONS
// ============================================================================

// Enable persistent cache for faster rebuilds
config.cacheStores = [
  {
    name: 'metro-cache',
    type: 'file',
    options: {
      maxAge: 1000 * 60 * 60 * 24 * 7, // 7 days
    },
  },
];

// Configure cache key generation
config.cacheKey = (filePath, transformOptions) => {
  return `${filePath}-${JSON.stringify(transformOptions)}`;
};

module.exports = config; 