import React from 'react';
import { Tabs } from 'expo-router';
import { useTheme } from '../../store/app-store';
import { Ionicons } from '@expo/vector-icons';

// ============================================================================
// TAB LAYOUT COMPONENT
// ============================================================================

export default function TabLayout(): JSX.Element {
  const { isDarkMode } = useTheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: isDarkMode ? '#8E8E93' : '#6C6C70',
        tabBarStyle: {
          backgroundColor: isDarkMode ? '#1C1C1E' : '#FFFFFF',
          borderTopColor: isDarkMode ? '#3A3A3C' : '#E5E5EA',
          borderTopWidth: 1,
          paddingBottom: 8,
          paddingTop: 8,
          height: 88,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
          marginTop: 4,
        },
        tabBarIconStyle: {
          marginTop: 4,
        },
        headerShown: false,
        tabBarHideOnKeyboard: true,
        tabBarShowLabel: true,
        tabBarBadgeStyle: {
          backgroundColor: '#FF3B30',
          color: '#FFFFFF',
          fontSize: 10,
          fontWeight: '600',
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'home' : 'home-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'grid' : 'grid-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="modules"
        options={{
          title: 'Modules',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'cube' : 'cube-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="analytics"
        options={{
          title: 'Analytics',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'analytics' : 'analytics-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'person' : 'person-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
    </Tabs>
  );
}
import { Tabs } from 'expo-router';
import { useTheme } from '../../store/app-store';
import { Ionicons } from '@expo/vector-icons';

// ============================================================================
// TAB LAYOUT COMPONENT
// ============================================================================

export default function TabLayout(): JSX.Element {
  const { isDarkMode } = useTheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: isDarkMode ? '#8E8E93' : '#6C6C70',
        tabBarStyle: {
          backgroundColor: isDarkMode ? '#1C1C1E' : '#FFFFFF',
          borderTopColor: isDarkMode ? '#3A3A3C' : '#E5E5EA',
          borderTopWidth: 1,
          paddingBottom: 8,
          paddingTop: 8,
          height: 88,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
          marginTop: 4,
        },
        tabBarIconStyle: {
          marginTop: 4,
        },
        headerShown: false,
        tabBarHideOnKeyboard: true,
        tabBarShowLabel: true,
        tabBarBadgeStyle: {
          backgroundColor: '#FF3B30',
          color: '#FFFFFF',
          fontSize: 10,
          fontWeight: '600',
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'home' : 'home-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'grid' : 'grid-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="modules"
        options={{
          title: 'Modules',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'cube' : 'cube-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="analytics"
        options={{
          title: 'Analytics',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'analytics' : 'analytics-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size, focused }) => (
            <Ionicons 
              name={focused ? 'person' : 'person-outline'} 
              size={size} 
              color={color} 
            />
          ),
        }}
      />
    </Tabs>
  );
}


