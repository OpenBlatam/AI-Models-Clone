/**
 * @fileoverview React hook for notification management
 * @author Blaze AI Team
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { 
  NotificationManager,
  NotificationPermissionStatus,
  NotificationToken,
  NotificationSettings,
  NotificationEvent,
  NotificationHandler,
  DeepLinkData
} from '../../lib/notifications/notification-manager';
import { NotificationPayload } from '../../lib/notifications/notification-types';

interface UseNotificationsReturn {
  readonly isInitialized: boolean;
  readonly permissionStatus: NotificationPermissionStatus | null;
  readonly notificationToken: NotificationToken | null;
  readonly settings: NotificationSettings;
  readonly lastNotification: NotificationEvent | null;
  readonly requestPermissions: () => Promise<NotificationPermissionStatus>;
  readonly scheduleNotification: (payload: NotificationPayload, trigger?: any) => Promise<string>;
  readonly cancelNotification: (id: string) => Promise<void>;
  readonly cancelAllNotifications: () => Promise<void>;
  readonly setBadgeCount: (count: number) => Promise<void>;
  readonly clearBadge: () => Promise<void>;
  readonly updateSettings: (newSettings: Partial<NotificationSettings>) => void;
  readonly handleDeepLink: (deepLinkData: DeepLinkData) => void;
}

/**
 * Custom hook for managing push notifications
 */
export function useNotifications(
  onDeepLink?: (deepLinkData: DeepLinkData) => void
): UseNotificationsReturn {
  const [isInitialized, setIsInitialized] = useState(false);
  const [permissionStatus, setPermissionStatus] = useState<NotificationPermissionStatus | null>(null);
  const [notificationToken, setNotificationToken] = useState<NotificationToken | null>(null);
  const [settings, setSettings] = useState<NotificationSettings>({
    enabled: true,
    channels: ['general'],
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00'
    },
    categories: ['message', 'reminder']
  });
  const [lastNotification, setLastNotification] = useState<NotificationEvent | null>(null);

  const notificationManagerRef = useRef<NotificationManager | null>(null);
  const appStateRef = useRef<AppStateStatus>(AppState.currentState);

  /**
   * Initializes the notification system
   */
  const initializeNotifications = useCallback(async (): Promise<void> => {
    try {
      const manager = new NotificationManager();
      await manager.initializeNotificationSystem();
      
      const permissions = await manager.requestNotificationPermissions();
      const token = await manager.getNotificationToken();
      
      setPermissionStatus(permissions);
      setNotificationToken(token);
      setIsInitialized(true);
      
      notificationManagerRef.current = manager;
    } catch (error) {
      console.error('Failed to initialize notifications:', error);
    }
  }, []);

  /**
   * Handles app state changes
   */
  const handleAppStateChange = useCallback((nextAppState: AppStateStatus): void => {
    if (appStateRef.current.match(/inactive|background/) && nextAppState === 'active') {
      // App has come to the foreground
      if (notificationManagerRef.current) {
        notificationManagerRef.current.clearBadge();
      }
    }
    appStateRef.current = nextAppState;
  }, []);

  /**
   * Handles notification events
   */
  const handleNotificationEvent = useCallback((event: NotificationEvent): void => {
    setLastNotification(event);
    
    if (event.type === 'opened' && event.deepLinkData && onDeepLink) {
      onDeepLink(event.deepLinkData);
    }
  }, [onDeepLink]);

  /**
   * Requests notification permissions
   */
  const requestPermissions = useCallback(async (): Promise<NotificationPermissionStatus> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    const permissions = await notificationManagerRef.current.requestNotificationPermissions();
    setPermissionStatus(permissions);
    return permissions;
  }, []);

  /**
   * Schedules a local notification
   */
  const scheduleNotification = useCallback(async (
    payload: NotificationPayload,
    trigger?: any
  ): Promise<string> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    return await notificationManagerRef.current.scheduleLocalNotification(payload, trigger);
  }, []);

  /**
   * Cancels a notification
   */
  const cancelNotification = useCallback(async (id: string): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.cancelNotification(id);
  }, []);

  /**
   * Cancels all notifications
   */
  const cancelAllNotifications = useCallback(async (): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.cancelAllNotifications();
  }, []);

  /**
   * Sets badge count
   */
  const setBadgeCount = useCallback(async (count: number): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.setBadgeCount(count);
  }, []);

  /**
   * Clears badge
   */
  const clearBadge = useCallback(async (): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.clearBadge();
  }, []);

  /**
   * Updates notification settings
   */
  const updateSettings = useCallback((newSettings: Partial<NotificationSettings>): void => {
    setSettings(prevSettings => ({
      ...prevSettings,
      ...newSettings
    }));
  }, []);

  /**
   * Handles deep link navigation
   */
  const handleDeepLink = useCallback((deepLinkData: DeepLinkData): void => {
    if (onDeepLink) {
      onDeepLink(deepLinkData);
    }
  }, [onDeepLink]);

  // Initialize notifications on mount
  useEffect(() => {
    initializeNotifications();
  }, [initializeNotifications]);

  // Set up app state listener
  useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, [handleAppStateChange]);

  // Set up notification handlers
  useEffect(() => {
    if (!notificationManagerRef.current) {
      return;
    }

    const handler: NotificationHandler = {
      onReceived: async (event: NotificationEvent) => {
        handleNotificationEvent(event);
      },
      onOpened: async (event: NotificationEvent) => {
        handleNotificationEvent(event);
      },
      onDismissed: async (event: NotificationEvent) => {
        handleNotificationEvent(event);
      }
    };

    notificationManagerRef.current.registerHandler(handler);

    return () => {
      if (notificationManagerRef.current) {
        notificationManagerRef.current.unregisterHandler(handler);
      }
    };
  }, [handleNotificationEvent]);

  return {
    isInitialized,
    permissionStatus,
    notificationToken,
    settings,
    lastNotification,
    requestPermissions,
    scheduleNotification,
    cancelNotification,
    cancelAllNotifications,
    setBadgeCount,
    clearBadge,
    updateSettings,
    handleDeepLink
  };
}
 * @fileoverview React hook for notification management
 * @author Blaze AI Team
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { 
  NotificationManager,
  NotificationPermissionStatus,
  NotificationToken,
  NotificationSettings,
  NotificationEvent,
  NotificationHandler,
  DeepLinkData
} from '../../lib/notifications/notification-manager';
import { NotificationPayload } from '../../lib/notifications/notification-types';

interface UseNotificationsReturn {
  readonly isInitialized: boolean;
  readonly permissionStatus: NotificationPermissionStatus | null;
  readonly notificationToken: NotificationToken | null;
  readonly settings: NotificationSettings;
  readonly lastNotification: NotificationEvent | null;
  readonly requestPermissions: () => Promise<NotificationPermissionStatus>;
  readonly scheduleNotification: (payload: NotificationPayload, trigger?: any) => Promise<string>;
  readonly cancelNotification: (id: string) => Promise<void>;
  readonly cancelAllNotifications: () => Promise<void>;
  readonly setBadgeCount: (count: number) => Promise<void>;
  readonly clearBadge: () => Promise<void>;
  readonly updateSettings: (newSettings: Partial<NotificationSettings>) => void;
  readonly handleDeepLink: (deepLinkData: DeepLinkData) => void;
}

/**
 * Custom hook for managing push notifications
 */
export function useNotifications(
  onDeepLink?: (deepLinkData: DeepLinkData) => void
): UseNotificationsReturn {
  const [isInitialized, setIsInitialized] = useState(false);
  const [permissionStatus, setPermissionStatus] = useState<NotificationPermissionStatus | null>(null);
  const [notificationToken, setNotificationToken] = useState<NotificationToken | null>(null);
  const [settings, setSettings] = useState<NotificationSettings>({
    enabled: true,
    channels: ['general'],
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00'
    },
    categories: ['message', 'reminder']
  });
  const [lastNotification, setLastNotification] = useState<NotificationEvent | null>(null);

  const notificationManagerRef = useRef<NotificationManager | null>(null);
  const appStateRef = useRef<AppStateStatus>(AppState.currentState);

  /**
   * Initializes the notification system
   */
  const initializeNotifications = useCallback(async (): Promise<void> => {
    try {
      const manager = new NotificationManager();
      await manager.initializeNotificationSystem();
      
      const permissions = await manager.requestNotificationPermissions();
      const token = await manager.getNotificationToken();
      
      setPermissionStatus(permissions);
      setNotificationToken(token);
      setIsInitialized(true);
      
      notificationManagerRef.current = manager;
    } catch (error) {
      console.error('Failed to initialize notifications:', error);
    }
  }, []);

  /**
   * Handles app state changes
   */
  const handleAppStateChange = useCallback((nextAppState: AppStateStatus): void => {
    if (appStateRef.current.match(/inactive|background/) && nextAppState === 'active') {
      // App has come to the foreground
      if (notificationManagerRef.current) {
        notificationManagerRef.current.clearBadge();
      }
    }
    appStateRef.current = nextAppState;
  }, []);

  /**
   * Handles notification events
   */
  const handleNotificationEvent = useCallback((event: NotificationEvent): void => {
    setLastNotification(event);
    
    if (event.type === 'opened' && event.deepLinkData && onDeepLink) {
      onDeepLink(event.deepLinkData);
    }
  }, [onDeepLink]);

  /**
   * Requests notification permissions
   */
  const requestPermissions = useCallback(async (): Promise<NotificationPermissionStatus> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    const permissions = await notificationManagerRef.current.requestNotificationPermissions();
    setPermissionStatus(permissions);
    return permissions;
  }, []);

  /**
   * Schedules a local notification
   */
  const scheduleNotification = useCallback(async (
    payload: NotificationPayload,
    trigger?: any
  ): Promise<string> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    return await notificationManagerRef.current.scheduleLocalNotification(payload, trigger);
  }, []);

  /**
   * Cancels a notification
   */
  const cancelNotification = useCallback(async (id: string): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.cancelNotification(id);
  }, []);

  /**
   * Cancels all notifications
   */
  const cancelAllNotifications = useCallback(async (): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.cancelAllNotifications();
  }, []);

  /**
   * Sets badge count
   */
  const setBadgeCount = useCallback(async (count: number): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.setBadgeCount(count);
  }, []);

  /**
   * Clears badge
   */
  const clearBadge = useCallback(async (): Promise<void> => {
    if (!notificationManagerRef.current) {
      throw new Error('Notification manager not initialized');
    }
    
    await notificationManagerRef.current.clearBadge();
  }, []);

  /**
   * Updates notification settings
   */
  const updateSettings = useCallback((newSettings: Partial<NotificationSettings>): void => {
    setSettings(prevSettings => ({
      ...prevSettings,
      ...newSettings
    }));
  }, []);

  /**
   * Handles deep link navigation
   */
  const handleDeepLink = useCallback((deepLinkData: DeepLinkData): void => {
    if (onDeepLink) {
      onDeepLink(deepLinkData);
    }
  }, [onDeepLink]);

  // Initialize notifications on mount
  useEffect(() => {
    initializeNotifications();
  }, [initializeNotifications]);

  // Set up app state listener
  useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, [handleAppStateChange]);

  // Set up notification handlers
  useEffect(() => {
    if (!notificationManagerRef.current) {
      return;
    }

    const handler: NotificationHandler = {
      onReceived: async (event: NotificationEvent) => {
        handleNotificationEvent(event);
      },
      onOpened: async (event: NotificationEvent) => {
        handleNotificationEvent(event);
      },
      onDismissed: async (event: NotificationEvent) => {
        handleNotificationEvent(event);
      }
    };

    notificationManagerRef.current.registerHandler(handler);

    return () => {
      if (notificationManagerRef.current) {
        notificationManagerRef.current.unregisterHandler(handler);
      }
    };
  }, [handleNotificationEvent]);

  return {
    isInitialized,
    permissionStatus,
    notificationToken,
    settings,
    lastNotification,
    requestPermissions,
    scheduleNotification,
    cancelNotification,
    cancelAllNotifications,
    setBadgeCount,
    clearBadge,
    updateSettings,
    handleDeepLink
  };
}


