module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      'react-native-reanimated/plugin',
      [
        'module-resolver',
        {
          root: ['./'],
          alias: {
            '@': './',
            '@/types': './types',
            '@/services': './services',
            '@/components': './components',
            '@/screens': './app',
            '@/utils': './utils',
            '@/hooks': './hooks',
            '@/store': './store',
          },
        },
      ],
    ],
  };
};


