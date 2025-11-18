/**
 * @fileoverview Analytics-enhanced button component
 * @author Blaze AI Team
 */

import React from 'react';
import { TouchableOpacity, Text, StyleSheet, TouchableOpacityProps } from 'react-native';
import { useAnalyticsContext } from './analytics-provider';
import { UserActionEvent } from '../../lib/analytics/analytics-types';

interface AnalyticsButtonProps extends TouchableOpacityProps {
  readonly title: string;
  readonly eventName?: string;
  readonly eventProperties?: Record<string, any>;
  readonly screenName?: string;
  readonly elementId?: string;
  readonly elementText?: string;
  readonly trackTap?: boolean;
  readonly style?: any;
  readonly textStyle?: any;
}

/**
 * Button component with automatic analytics tracking
 */
export function AnalyticsButton({
  title,
  eventName,
  eventProperties,
  screenName,
  elementId,
  elementText,
  trackTap = true,
  style,
  textStyle,
  onPress,
  ...props
}: AnalyticsButtonProps): React.JSX.Element {
  const analytics = useAnalyticsContext();

  /**
   * Handles button press with analytics tracking
   */
  const handlePress = async (event: any): Promise<void> => {
    try {
      // Track user action
      if (trackTap && analytics.isInitialized) {
        const userAction: UserActionEvent = {
          actionType: 'tap',
          elementType: 'button',
          elementId: elementId || 'button',
          elementText: elementText || title,
          screenName: screenName || 'unknown',
          properties: {
            ...eventProperties,
            timestamp: Date.now()
          }
        };

        await analytics.trackUserAction(userAction);
      }

      // Track custom event if provided
      if (eventName && analytics.isInitialized) {
        await analytics.trackEvent(eventName, {
          ...eventProperties,
          elementType: 'button',
          elementText: title,
          screenName: screenName || 'unknown',
          timestamp: Date.now()
        });
      }

      // Call original onPress handler
      if (onPress) {
        onPress(event);
      }
    } catch (error) {
      console.error('Failed to track button press:', error);
      
      // Still call original onPress handler even if analytics fails
      if (onPress) {
        onPress(event);
      }
    }
  };

  return (
    <TouchableOpacity
      style={[styles.button, style]}
      onPress={handlePress}
      accessibilityLabel={title}
      accessibilityRole="button"
      {...props}
    >
      <Text style={[styles.text, textStyle]}>
        {title}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center'
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  }
});
 * @fileoverview Analytics-enhanced button component
 * @author Blaze AI Team
 */

import React from 'react';
import { TouchableOpacity, Text, StyleSheet, TouchableOpacityProps } from 'react-native';
import { useAnalyticsContext } from './analytics-provider';
import { UserActionEvent } from '../../lib/analytics/analytics-types';

interface AnalyticsButtonProps extends TouchableOpacityProps {
  readonly title: string;
  readonly eventName?: string;
  readonly eventProperties?: Record<string, any>;
  readonly screenName?: string;
  readonly elementId?: string;
  readonly elementText?: string;
  readonly trackTap?: boolean;
  readonly style?: any;
  readonly textStyle?: any;
}

/**
 * Button component with automatic analytics tracking
 */
export function AnalyticsButton({
  title,
  eventName,
  eventProperties,
  screenName,
  elementId,
  elementText,
  trackTap = true,
  style,
  textStyle,
  onPress,
  ...props
}: AnalyticsButtonProps): React.JSX.Element {
  const analytics = useAnalyticsContext();

  /**
   * Handles button press with analytics tracking
   */
  const handlePress = async (event: any): Promise<void> => {
    try {
      // Track user action
      if (trackTap && analytics.isInitialized) {
        const userAction: UserActionEvent = {
          actionType: 'tap',
          elementType: 'button',
          elementId: elementId || 'button',
          elementText: elementText || title,
          screenName: screenName || 'unknown',
          properties: {
            ...eventProperties,
            timestamp: Date.now()
          }
        };

        await analytics.trackUserAction(userAction);
      }

      // Track custom event if provided
      if (eventName && analytics.isInitialized) {
        await analytics.trackEvent(eventName, {
          ...eventProperties,
          elementType: 'button',
          elementText: title,
          screenName: screenName || 'unknown',
          timestamp: Date.now()
        });
      }

      // Call original onPress handler
      if (onPress) {
        onPress(event);
      }
    } catch (error) {
      console.error('Failed to track button press:', error);
      
      // Still call original onPress handler even if analytics fails
      if (onPress) {
        onPress(event);
      }
    }
  };

  return (
    <TouchableOpacity
      style={[styles.button, style]}
      onPress={handlePress}
      accessibilityLabel={title}
      accessibilityRole="button"
      {...props}
    >
      <Text style={[styles.text, textStyle]}>
        {title}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center'
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  }
});


