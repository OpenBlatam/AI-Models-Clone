import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  StatusBar,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as SplashScreen from 'expo-splash-screen';
import * as Font from 'expo-font';
import { useTheme } from '../../store/app-store';

// ============================================================================
// TYPES
// ============================================================================

interface SplashScreenProps {
  onFinish: () => void;
  minimumSplashTime?: number;
}

interface LoadingState {
  fontsLoaded: boolean;
  assetsLoaded: boolean;
  initializationComplete: boolean;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const { width, height } = Dimensions.get('window');
const MINIMUM_SPLASH_TIME = 2000; // 2 seconds minimum

// ============================================================================
// FONT CONFIGURATION
// ============================================================================

const FONT_CONFIG = {
  'Inter-Regular': require('../../assets/fonts/Inter-Regular.ttf'),
  'Inter-Medium': require('../../assets/fonts/Inter-Medium.ttf'),
  'Inter-SemiBold': require('../../assets/fonts/Inter-SemiBold.ttf'),
  'Inter-Bold': require('../../assets/fonts/Inter-Bold.ttf'),
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function SplashScreenComponent({ 
  onFinish, 
  minimumSplashTime = MINIMUM_SPLASH_TIME 
}: SplashScreenProps): JSX.Element {
  const colorScheme = useColorScheme();
  const { isDarkMode } = useTheme();
  
  const [loadingState, setLoadingState] = useState<LoadingState>({
    fontsLoaded: false,
    assetsLoaded: false,
    initializationComplete: false,
  });
  
  const [startTime] = useState(Date.now());
  const [fadeAnim] = useState(new Animated.Value(0));
  const [scaleAnim] = useState(new Animated.Value(0.8));
  const [logoAnim] = useState(new Animated.Value(0));

  // ============================================================================
  // ANIMATIONS
  // ============================================================================

  const startAnimations = useCallback(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.timing(logoAnim, {
        toValue: 1,
        duration: 1000,
        delay: 200,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, scaleAnim, logoAnim]);

  // ============================================================================
  // LOADING FUNCTIONS
  // ============================================================================

  const loadFonts = useCallback(async (): Promise<void> => {
    try {
      await Font.loadAsync(FONT_CONFIG);
      setLoadingState(prev => ({ ...prev, fontsLoaded: true }));
    } catch (error) {
      console.error('Error loading fonts:', error);
      // Continue even if fonts fail to load
      setLoadingState(prev => ({ ...prev, fontsLoaded: true }));
    }
  }, []);

  const loadAssets = useCallback(async (): Promise<void> => {
    try {
      // Load any additional assets here
      // For now, we'll just simulate loading time
      await new Promise(resolve => setTimeout(resolve, 500));
      setLoadingState(prev => ({ ...prev, assetsLoaded: true }));
    } catch (error) {
      console.error('Error loading assets:', error);
      setLoadingState(prev => ({ ...prev, assetsLoaded: true }));
    }
  }, []);

  const initializeApp = useCallback(async (): Promise<void> => {
    try {
      // Perform any app initialization here
      // This could include:
      // - Loading user preferences
      // - Initializing analytics
      // - Setting up error reporting
      // - Loading cached data
      
      await new Promise(resolve => setTimeout(resolve, 300));
      setLoadingState(prev => ({ ...prev, initializationComplete: true }));
    } catch (error) {
      console.error('Error initializing app:', error);
      setLoadingState(prev => ({ ...prev, initializationComplete: true }));
    }
  }, []);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    const loadEverything = async () => {
      // Start animations
      startAnimations();
      
      // Load resources in parallel
      await Promise.all([
        loadFonts(),
        loadAssets(),
        initializeApp(),
      ]);
    };

    loadEverything();
  }, [loadFonts, loadAssets, initializeApp, startAnimations]);

  // ============================================================================
  // FINISH HANDLING
  // ============================================================================

  useEffect(() => {
    const { fontsLoaded, assetsLoaded, initializationComplete } = loadingState;
    
    if (fontsLoaded && assetsLoaded && initializationComplete) {
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, minimumSplashTime - elapsedTime);
      
      setTimeout(() => {
        // Hide the splash screen
        SplashScreen.hideAsync();
        
        // Call the finish callback
        onFinish();
      }, remainingTime);
    }
  }, [loadingState, startTime, minimumSplashTime, onFinish]);

  // ============================================================================
  // RENDER
  // ============================================================================

  const styles = createStyles(isDarkMode);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={isDarkMode ? '#000000' : '#FFFFFF'} 
      />
      
      <Animated.View 
        style={[
          styles.content,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        {/* Logo Section */}
        <Animated.View 
          style={[
            styles.logoContainer,
            {
              opacity: logoAnim,
              transform: [
                {
                  translateY: logoAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [50, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.logo}>
            <Ionicons 
              name="flash" 
              size={80} 
              color={isDarkMode ? '#007AFF' : '#007AFF'} 
            />
          </View>
          <Text style={styles.appName}>Blaze AI</Text>
          <Text style={styles.tagline}>Intelligent Mobile Experience</Text>
        </Animated.View>

        {/* Loading Indicator */}
        <View style={styles.loadingContainer}>
          <Animated.View style={styles.loadingBar}>
            <Animated.View 
              style={[
                styles.loadingProgress,
                {
                  width: logoAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0%', '100%'],
                  }),
                },
              ]}
            />
          </Animated.View>
          
          <Text style={styles.loadingText}>
            {!loadingState.fontsLoaded && 'Loading fonts...'}
            {loadingState.fontsLoaded && !loadingState.assetsLoaded && 'Loading assets...'}
            {loadingState.assetsLoaded && !loadingState.initializationComplete && 'Initializing app...'}
            {loadingState.initializationComplete && 'Ready!'}
          </Text>
        </View>

        {/* Version Info */}
        <View style={styles.versionContainer}>
          <Text style={styles.versionText}>v1.0.0</Text>
          <Text style={styles.platformText}>
            {Platform.OS === 'ios' ? 'iOS' : 'Android'} • {Platform.Version}
          </Text>
        </View>
      </Animated.View>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(isDark: boolean) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDark ? '#000000' : '#FFFFFF',
    },
    content: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingHorizontal: 40,
    },
    logoContainer: {
      alignItems: 'center',
      marginBottom: 60,
    },
    logo: {
      width: 120,
      height: 120,
      borderRadius: 60,
      backgroundColor: isDark ? '#1C1C1E' : '#F8F9FA',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 24,
      shadowColor: isDark ? '#000000' : '#000000',
      shadowOffset: {
        width: 0,
        height: 4,
      },
      shadowOpacity: isDark ? 0.3 : 0.1,
      shadowRadius: 8,
      elevation: 8,
    },
    appName: {
      fontSize: 32,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 8,
      textAlign: 'center',
    },
    tagline: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      fontWeight: '500',
    },
    loadingContainer: {
      width: '100%',
      alignItems: 'center',
      marginBottom: 40,
    },
    loadingBar: {
      width: '100%',
      height: 4,
      backgroundColor: isDark ? '#3A3A3C' : '#E5E5EA',
      borderRadius: 2,
      marginBottom: 16,
      overflow: 'hidden',
    },
    loadingProgress: {
      height: '100%',
      backgroundColor: '#007AFF',
      borderRadius: 2,
    },
    loadingText: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
    },
    versionContainer: {
      position: 'absolute',
      bottom: 40,
      alignItems: 'center',
    },
    versionText: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 4,
    },
    platformText: {
      fontSize: 10,
      color: isDark ? '#6C6C70' : '#8E8E93',
    },
  });
}

// ============================================================================
// HOOK FOR SPLASH SCREEN
// ============================================================================

export function useSplashScreen() {
  const [isSplashVisible, setIsSplashVisible] = useState(true);

  const hideSplash = useCallback(() => {
    setIsSplashVisible(false);
  }, []);

  return {
    isSplashVisible,
    hideSplash,
  };
}
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  StatusBar,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as SplashScreen from 'expo-splash-screen';
import * as Font from 'expo-font';
import { useTheme } from '../../store/app-store';

// ============================================================================
// TYPES
// ============================================================================

interface SplashScreenProps {
  onFinish: () => void;
  minimumSplashTime?: number;
}

interface LoadingState {
  fontsLoaded: boolean;
  assetsLoaded: boolean;
  initializationComplete: boolean;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const { width, height } = Dimensions.get('window');
const MINIMUM_SPLASH_TIME = 2000; // 2 seconds minimum

// ============================================================================
// FONT CONFIGURATION
// ============================================================================

const FONT_CONFIG = {
  'Inter-Regular': require('../../assets/fonts/Inter-Regular.ttf'),
  'Inter-Medium': require('../../assets/fonts/Inter-Medium.ttf'),
  'Inter-SemiBold': require('../../assets/fonts/Inter-SemiBold.ttf'),
  'Inter-Bold': require('../../assets/fonts/Inter-Bold.ttf'),
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function SplashScreenComponent({ 
  onFinish, 
  minimumSplashTime = MINIMUM_SPLASH_TIME 
}: SplashScreenProps): JSX.Element {
  const colorScheme = useColorScheme();
  const { isDarkMode } = useTheme();
  
  const [loadingState, setLoadingState] = useState<LoadingState>({
    fontsLoaded: false,
    assetsLoaded: false,
    initializationComplete: false,
  });
  
  const [startTime] = useState(Date.now());
  const [fadeAnim] = useState(new Animated.Value(0));
  const [scaleAnim] = useState(new Animated.Value(0.8));
  const [logoAnim] = useState(new Animated.Value(0));

  // ============================================================================
  // ANIMATIONS
  // ============================================================================

  const startAnimations = useCallback(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.timing(logoAnim, {
        toValue: 1,
        duration: 1000,
        delay: 200,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, scaleAnim, logoAnim]);

  // ============================================================================
  // LOADING FUNCTIONS
  // ============================================================================

  const loadFonts = useCallback(async (): Promise<void> => {
    try {
      await Font.loadAsync(FONT_CONFIG);
      setLoadingState(prev => ({ ...prev, fontsLoaded: true }));
    } catch (error) {
      console.error('Error loading fonts:', error);
      // Continue even if fonts fail to load
      setLoadingState(prev => ({ ...prev, fontsLoaded: true }));
    }
  }, []);

  const loadAssets = useCallback(async (): Promise<void> => {
    try {
      // Load any additional assets here
      // For now, we'll just simulate loading time
      await new Promise(resolve => setTimeout(resolve, 500));
      setLoadingState(prev => ({ ...prev, assetsLoaded: true }));
    } catch (error) {
      console.error('Error loading assets:', error);
      setLoadingState(prev => ({ ...prev, assetsLoaded: true }));
    }
  }, []);

  const initializeApp = useCallback(async (): Promise<void> => {
    try {
      // Perform any app initialization here
      // This could include:
      // - Loading user preferences
      // - Initializing analytics
      // - Setting up error reporting
      // - Loading cached data
      
      await new Promise(resolve => setTimeout(resolve, 300));
      setLoadingState(prev => ({ ...prev, initializationComplete: true }));
    } catch (error) {
      console.error('Error initializing app:', error);
      setLoadingState(prev => ({ ...prev, initializationComplete: true }));
    }
  }, []);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    const loadEverything = async () => {
      // Start animations
      startAnimations();
      
      // Load resources in parallel
      await Promise.all([
        loadFonts(),
        loadAssets(),
        initializeApp(),
      ]);
    };

    loadEverything();
  }, [loadFonts, loadAssets, initializeApp, startAnimations]);

  // ============================================================================
  // FINISH HANDLING
  // ============================================================================

  useEffect(() => {
    const { fontsLoaded, assetsLoaded, initializationComplete } = loadingState;
    
    if (fontsLoaded && assetsLoaded && initializationComplete) {
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, minimumSplashTime - elapsedTime);
      
      setTimeout(() => {
        // Hide the splash screen
        SplashScreen.hideAsync();
        
        // Call the finish callback
        onFinish();
      }, remainingTime);
    }
  }, [loadingState, startTime, minimumSplashTime, onFinish]);

  // ============================================================================
  // RENDER
  // ============================================================================

  const styles = createStyles(isDarkMode);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={isDarkMode ? '#000000' : '#FFFFFF'} 
      />
      
      <Animated.View 
        style={[
          styles.content,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        {/* Logo Section */}
        <Animated.View 
          style={[
            styles.logoContainer,
            {
              opacity: logoAnim,
              transform: [
                {
                  translateY: logoAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [50, 0],
                  }),
                },
              ],
            },
          ]}
        >
          <View style={styles.logo}>
            <Ionicons 
              name="flash" 
              size={80} 
              color={isDarkMode ? '#007AFF' : '#007AFF'} 
            />
          </View>
          <Text style={styles.appName}>Blaze AI</Text>
          <Text style={styles.tagline}>Intelligent Mobile Experience</Text>
        </Animated.View>

        {/* Loading Indicator */}
        <View style={styles.loadingContainer}>
          <Animated.View style={styles.loadingBar}>
            <Animated.View 
              style={[
                styles.loadingProgress,
                {
                  width: logoAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0%', '100%'],
                  }),
                },
              ]}
            />
          </Animated.View>
          
          <Text style={styles.loadingText}>
            {!loadingState.fontsLoaded && 'Loading fonts...'}
            {loadingState.fontsLoaded && !loadingState.assetsLoaded && 'Loading assets...'}
            {loadingState.assetsLoaded && !loadingState.initializationComplete && 'Initializing app...'}
            {loadingState.initializationComplete && 'Ready!'}
          </Text>
        </View>

        {/* Version Info */}
        <View style={styles.versionContainer}>
          <Text style={styles.versionText}>v1.0.0</Text>
          <Text style={styles.platformText}>
            {Platform.OS === 'ios' ? 'iOS' : 'Android'} • {Platform.Version}
          </Text>
        </View>
      </Animated.View>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

function createStyles(isDark: boolean) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDark ? '#000000' : '#FFFFFF',
    },
    content: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingHorizontal: 40,
    },
    logoContainer: {
      alignItems: 'center',
      marginBottom: 60,
    },
    logo: {
      width: 120,
      height: 120,
      borderRadius: 60,
      backgroundColor: isDark ? '#1C1C1E' : '#F8F9FA',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 24,
      shadowColor: isDark ? '#000000' : '#000000',
      shadowOffset: {
        width: 0,
        height: 4,
      },
      shadowOpacity: isDark ? 0.3 : 0.1,
      shadowRadius: 8,
      elevation: 8,
    },
    appName: {
      fontSize: 32,
      fontWeight: 'bold',
      color: isDark ? '#FFFFFF' : '#000000',
      marginBottom: 8,
      textAlign: 'center',
    },
    tagline: {
      fontSize: 16,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
      fontWeight: '500',
    },
    loadingContainer: {
      width: '100%',
      alignItems: 'center',
      marginBottom: 40,
    },
    loadingBar: {
      width: '100%',
      height: 4,
      backgroundColor: isDark ? '#3A3A3C' : '#E5E5EA',
      borderRadius: 2,
      marginBottom: 16,
      overflow: 'hidden',
    },
    loadingProgress: {
      height: '100%',
      backgroundColor: '#007AFF',
      borderRadius: 2,
    },
    loadingText: {
      fontSize: 14,
      color: isDark ? '#8E8E93' : '#6C6C70',
      textAlign: 'center',
    },
    versionContainer: {
      position: 'absolute',
      bottom: 40,
      alignItems: 'center',
    },
    versionText: {
      fontSize: 12,
      color: isDark ? '#8E8E93' : '#6C6C70',
      marginBottom: 4,
    },
    platformText: {
      fontSize: 10,
      color: isDark ? '#6C6C70' : '#8E8E93',
    },
  });
}

// ============================================================================
// HOOK FOR SPLASH SCREEN
// ============================================================================

export function useSplashScreen() {
  const [isSplashVisible, setIsSplashVisible] = useState(true);

  const hideSplash = useCallback(() => {
    setIsSplashVisible(false);
  }, []);

  return {
    isSplashVisible,
    hideSplash,
  };
}


