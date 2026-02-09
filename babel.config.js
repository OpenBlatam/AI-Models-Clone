module.exports = function (api) {
  api.cache(true);
  
  return {
    presets: [
      ['babel-preset-expo', { 
        jsxImportSource: 'react',
        jsxRuntime: 'automatic'
      }]
    ],
    plugins: [
      // Expo Router plugin for file-based routing
      'expo-router/babel',
      
      // React Native Reanimated plugin for animations
      'react-native-reanimated/plugin',
      
      // ============================================================================
      // PERFORMANCE OPTIMIZATIONS
      // ============================================================================
      
      // Enable tree shaking and dead code elimination
      ['@babel/plugin-transform-runtime', {
        helpers: true,
        regenerator: true,
        useESModules: true,
      }],
      
      // Optimize object spread and rest
      '@babel/plugin-proposal-object-rest-spread',
      
      // Enable optional chaining and nullish coalescing
      '@babel/plugin-proposal-optional-chaining',
      '@babel/plugin-proposal-nullish-coalescing-operator',
      
      // ============================================================================
      // EXPERIMENTAL FEATURES
      // ============================================================================
      
      // Enable experimental features for better performance
      ['@babel/plugin-proposal-decorators', { legacy: true }],
      ['@babel/plugin-proposal-class-properties', { loose: true }],
      
      // Enable private methods
      '@babel/plugin-proposal-private-methods',
      '@babel/plugin-proposal-private-property-in-object',
      
      // ============================================================================
      // DEVELOPMENT OPTIMIZATIONS
      // ============================================================================
      
      // Enable better debugging in development
      ...(api.env('development') ? [
        ['@babel/plugin-transform-react-jsx-source'],
        ['@babel/plugin-transform-react-jsx-self'],
      ] : []),
    ],
    env: {
      development: {
        plugins: [
          // Development-specific optimizations
          ['@babel/plugin-transform-react-jsx-source'],
          ['@babel/plugin-transform-react-jsx-self'],
        ]
      },
      production: {
        plugins: [
          // Production optimizations
          'transform-remove-console',
          'transform-remove-debugger',
          
          // Optimize for size
          ['@babel/plugin-transform-runtime', {
            helpers: true,
            regenerator: false,
            useESModules: true,
          }],
        ]
      },
      test: {
        plugins: [
          // Test-specific optimizations
          '@babel/plugin-transform-modules-commonjs',
        ]
      }
    }
  };
}; 