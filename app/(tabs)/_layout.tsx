import React, { useCallback, useMemo } from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

// ============================================================================
// TYPES
// ============================================================================
interface TabConfig {
  name: string;
  title: string;
  iconName: keyof typeof Ionicons.glyphMap;
  href?: string | null;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================
const TAB_CONFIGS: TabConfig[] = [
  {
    name: 'home',
    title: 'Home',
    iconName: 'home',
  },
  {
    name: 'search',
    title: 'Search',
    iconName: 'search',
  },
  {
    name: 'create',
    title: 'Create',
    iconName: 'add-circle',
    href: null,
  },
  {
    name: 'profile',
    title: 'Profile',
    iconName: 'person',
  },
  {
    name: 'settings',
    title: 'Settings',
    iconName: 'settings',
  },
];

// ============================================================================
// HELPERS
// ============================================================================
const createTabIcon = (iconName: keyof typeof Ionicons.glyphMap) => {
  return React.memo(({ color, size }: { color: string; size: number }) => (
    <Ionicons name={iconName} size={size} color={color} />
  ));
};

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================
export default function TabLayout() {
  const screenOptions = useMemo(() => ({
    tabBarActiveTintColor: '#007AFF',
    tabBarInactiveTintColor: '#8E8E93',
    tabBarStyle: {
      backgroundColor: '#FFFFFF',
      borderTopColor: '#E5E5EA',
    },
    headerStyle: {
      backgroundColor: '#FFFFFF',
    },
    headerTintColor: '#000000',
    headerTitleStyle: {
      fontWeight: '600',
    },
  }), []);

  const renderTabScreen = useCallback((config: TabConfig) => {
    const TabIcon = createTabIcon(config.iconName);
    
    return (
      <Tabs.Screen
        key={config.name}
        name={config.name}
        options={{
          title: config.title,
          tabBarIcon: ({ color, size }) => <TabIcon color={color} size={size} />,
          href: config.href,
        }}
      />
    );
  }, []);

  return (
    <Tabs screenOptions={screenOptions}>
      {TAB_CONFIGS.map(renderTabScreen)}
    </Tabs>
  );
} 