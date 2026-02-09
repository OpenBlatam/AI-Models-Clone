import React, { createContext, useContext, useReducer, useCallback, useMemo } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { useColorScheme } from 'react-native';
import { z } from 'zod';

// ============================================================================
// TYPES
// ============================================================================

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  avatar?: string;
  isEmailVerified: boolean;
  role: 'user' | 'admin' | 'moderator';
  createdAt: string;
  updatedAt: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
}

interface ThemeState {
  mode: 'light' | 'dark' | 'system';
  primaryColor: string;
  fontSize: 'small' | 'medium' | 'large';
  reducedMotion: boolean;
  highContrast: boolean;
}

interface NotificationState {
  email: boolean;
  push: boolean;
  sms: boolean;
  marketing: boolean;
  security: boolean;
  updates: boolean;
}

interface AppState {
  auth: AuthState;
  theme: ThemeState;
  notifications: NotificationState;
  isOnline: boolean;
  isAppActive: boolean;
  lastActiveTime: string | null;
}

// ============================================================================
// ACTION TYPES
// ============================================================================

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; accessToken: string; refreshToken: string } }
  | { type: 'AUTH_FAILURE'; payload: { error: string } }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_UPDATE_USER'; payload: { user: Partial<User> } }
  | { type: 'AUTH_CLEAR_ERROR' };

type ThemeAction =
  | { type: 'THEME_SET_MODE'; payload: { mode: 'light' | 'dark' | 'system' } }
  | { type: 'THEME_SET_PRIMARY_COLOR'; payload: { color: string } }
  | { type: 'THEME_SET_FONT_SIZE'; payload: { size: 'small' | 'medium' | 'large' } }
  | { type: 'THEME_TOGGLE_REDUCED_MOTION' }
  | { type: 'THEME_TOGGLE_HIGH_CONTRAST' };

type NotificationAction =
  | { type: 'NOTIFICATION_TOGGLE_EMAIL' }
  | { type: 'NOTIFICATION_TOGGLE_PUSH' }
  | { type: 'NOTIFICATION_TOGGLE_SMS' }
  | { type: 'NOTIFICATION_TOGGLE_MARKETING' }
  | { type: 'NOTIFICATION_TOGGLE_SECURITY' }
  | { type: 'NOTIFICATION_TOGGLE_UPDATES' }
  | { type: 'NOTIFICATION_SET_ALL'; payload: { settings: Partial<NotificationState> } };

type AppAction =
  | { type: 'APP_SET_ONLINE'; payload: { isOnline: boolean } }
  | { type: 'APP_SET_ACTIVE'; payload: { isActive: boolean } }
  | { type: 'APP_SET_LAST_ACTIVE'; payload: { timestamp: string } };

type Action = AuthAction | ThemeAction | NotificationAction | AppAction;

// ============================================================================
// VALIDATION SCHEMAS
// ============================================================================

const UserSchema = z.object({
  id: z.string(),
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email(),
  username: z.string(),
  avatar: z.string().optional(),
  isEmailVerified: z.boolean(),
  role: z.enum(['user', 'admin', 'moderator']),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialAuthState: AuthState = {
  isAuthenticated: false,
  user: null,
  accessToken: null,
  refreshToken: null,
  isLoading: false,
  error: null,
};

const initialThemeState: ThemeState = {
  mode: 'system',
  primaryColor: '#007AFF',
  fontSize: 'medium',
  reducedMotion: false,
  highContrast: false,
};

const initialNotificationState: NotificationState = {
  email: true,
  push: true,
  sms: false,
  marketing: false,
  security: true,
  updates: true,
};

const initialState: AppState = {
  auth: initialAuthState,
  theme: initialThemeState,
  notifications: initialNotificationState,
  isOnline: true,
  isAppActive: true,
  lastActiveTime: null,
};

// ============================================================================
// REDUCERS
// ============================================================================

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        accessToken: null,
        refreshToken: null,
        isLoading: false,
        error: action.payload.error,
      };
    case 'AUTH_LOGOUT':
      return {
        ...initialAuthState,
      };
    case 'AUTH_UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload.user } : null,
      };
    case 'AUTH_CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
}

function themeReducer(state: ThemeState, action: ThemeAction): ThemeState {
  switch (action.type) {
    case 'THEME_SET_MODE':
      return {
        ...state,
        mode: action.payload.mode,
      };
    case 'THEME_SET_PRIMARY_COLOR':
      return {
        ...state,
        primaryColor: action.payload.color,
      };
    case 'THEME_SET_FONT_SIZE':
      return {
        ...state,
        fontSize: action.payload.size,
      };
    case 'THEME_TOGGLE_REDUCED_MOTION':
      return {
        ...state,
        reducedMotion: !state.reducedMotion,
      };
    case 'THEME_TOGGLE_HIGH_CONTRAST':
      return {
        ...state,
        highContrast: !state.highContrast,
      };
    default:
      return state;
  }
}

function notificationReducer(state: NotificationState, action: NotificationAction): NotificationState {
  switch (action.type) {
    case 'NOTIFICATION_TOGGLE_EMAIL':
      return {
        ...state,
        email: !state.email,
      };
    case 'NOTIFICATION_TOGGLE_PUSH':
      return {
        ...state,
        push: !state.push,
      };
    case 'NOTIFICATION_TOGGLE_SMS':
      return {
        ...state,
        sms: !state.sms,
      };
    case 'NOTIFICATION_TOGGLE_MARKETING':
      return {
        ...state,
        marketing: !state.marketing,
      };
    case 'NOTIFICATION_TOGGLE_SECURITY':
      return {
        ...state,
        security: !state.security,
      };
    case 'NOTIFICATION_TOGGLE_UPDATES':
      return {
        ...state,
        updates: !state.updates,
      };
    case 'NOTIFICATION_SET_ALL':
      return {
        ...state,
        ...action.payload.settings,
      };
    default:
      return state;
  }
}

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'APP_SET_ONLINE':
      return {
        ...state,
        isOnline: action.payload.isOnline,
      };
    case 'APP_SET_ACTIVE':
      return {
        ...state,
        isAppActive: action.payload.isActive,
        lastActiveTime: action.payload.isActive ? new Date().toISOString() : state.lastActiveTime,
      };
    case 'APP_SET_LAST_ACTIVE':
      return {
        ...state,
        lastActiveTime: action.payload.timestamp,
      };
    default:
      return {
        ...state,
        auth: authReducer(state.auth, action as AuthAction),
        theme: themeReducer(state.theme, action as ThemeAction),
        notifications: notificationReducer(state.notifications, action as NotificationAction),
      };
  }
}

// ============================================================================
// CONTEXT
// ============================================================================

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<Action>;
  // Auth actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  clearAuthError: () => void;
  // Theme actions
  setThemeMode: (mode: 'light' | 'dark' | 'system') => void;
  setPrimaryColor: (color: string) => void;
  setFontSize: (size: 'small' | 'medium' | 'large') => void;
  toggleReducedMotion: () => void;
  toggleHighContrast: () => void;
  // Notification actions
  toggleNotification: (type: keyof NotificationState) => void;
  setNotificationSettings: (settings: Partial<NotificationState>) => void;
  // App actions
  setOnlineStatus: (isOnline: boolean) => void;
  setAppActiveStatus: (isActive: boolean) => void;
  // Computed values
  isDarkMode: boolean;
  effectiveTheme: 'light' | 'dark';
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// ============================================================================
// PROVIDER COMPONENT
// ============================================================================

interface AppProviderProps {
  children: React.ReactNode;
}

export function AppProvider({ children }: AppProviderProps): JSX.Element {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const systemColorScheme = useColorScheme();

  // Computed values
  const isDarkMode = useMemo(() => {
    if (state.theme.mode === 'system') {
      return systemColorScheme === 'dark';
    }
    return state.theme.mode === 'dark';
  }, [state.theme.mode, systemColorScheme]);

  const effectiveTheme = useMemo(() => {
    if (state.theme.mode === 'system') {
      return systemColorScheme || 'light';
    }
    return state.theme.mode;
  }, [state.theme.mode, systemColorScheme]);

  // Auth actions
  const login = useCallback(async (email: string, password: string): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock user data - in real app, this would come from API
      const mockUser: User = {
        id: '1',
        firstName: 'John',
        lastName: 'Doe',
        email,
        username: 'johndoe',
        isEmailVerified: true,
        role: 'user',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      // Validate user data with Zod
      const validatedUser = UserSchema.parse(mockUser);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: validatedUser,
          accessToken: 'mock-access-token',
          refreshToken: 'mock-refresh-token',
        },
      });
    } catch (error) {
      dispatch({
        type: 'AUTH_FAILURE',
        payload: {
          error: error instanceof Error ? error.message : 'Login failed',
        },
      });
    }
  }, []);

  const logout = useCallback((): void => {
    dispatch({ type: 'AUTH_LOGOUT' });
  }, []);

  const updateUser = useCallback((userData: Partial<User>): void => {
    dispatch({ type: 'AUTH_UPDATE_USER', payload: { user: userData } });
  }, []);

  const clearAuthError = useCallback((): void => {
    dispatch({ type: 'AUTH_CLEAR_ERROR' });
  }, []);

  // Theme actions
  const setThemeMode = useCallback((mode: 'light' | 'dark' | 'system'): void => {
    dispatch({ type: 'THEME_SET_MODE', payload: { mode } });
  }, []);

  const setPrimaryColor = useCallback((color: string): void => {
    dispatch({ type: 'THEME_SET_PRIMARY_COLOR', payload: { color } });
  }, []);

  const setFontSize = useCallback((size: 'small' | 'medium' | 'large'): void => {
    dispatch({ type: 'THEME_SET_FONT_SIZE', payload: { size } });
  }, []);

  const toggleReducedMotion = useCallback((): void => {
    dispatch({ type: 'THEME_TOGGLE_REDUCED_MOTION' });
  }, []);

  const toggleHighContrast = useCallback((): void => {
    dispatch({ type: 'THEME_TOGGLE_HIGH_CONTRAST' });
  }, []);

  // Notification actions
  const toggleNotification = useCallback((type: keyof NotificationState): void => {
    const actionMap: Record<keyof NotificationState, NotificationAction['type']> = {
      email: 'NOTIFICATION_TOGGLE_EMAIL',
      push: 'NOTIFICATION_TOGGLE_PUSH',
      sms: 'NOTIFICATION_TOGGLE_SMS',
      marketing: 'NOTIFICATION_TOGGLE_MARKETING',
      security: 'NOTIFICATION_TOGGLE_SECURITY',
      updates: 'NOTIFICATION_TOGGLE_UPDATES',
    };
    
    dispatch({ type: actionMap[type] });
  }, []);

  const setNotificationSettings = useCallback((settings: Partial<NotificationState>): void => {
    dispatch({ type: 'NOTIFICATION_SET_ALL', payload: { settings } });
  }, []);

  // App actions
  const setOnlineStatus = useCallback((isOnline: boolean): void => {
    dispatch({ type: 'APP_SET_ONLINE', payload: { isOnline } });
  }, []);

  const setAppActiveStatus = useCallback((isActive: boolean): void => {
    dispatch({ type: 'APP_SET_ACTIVE', payload: { isActive } });
  }, []);

  // App state monitoring
  React.useEffect(() => {
    const handleAppStateChange = (nextAppState: AppStateStatus): void => {
      setAppActiveStatus(nextAppState === 'active');
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, [setAppActiveStatus]);

  const contextValue: AppContextType = useMemo(() => ({
    state,
    dispatch,
    login,
    logout,
    updateUser,
    clearAuthError,
    setThemeMode,
    setPrimaryColor,
    setFontSize,
    toggleReducedMotion,
    toggleHighContrast,
    toggleNotification,
    setNotificationSettings,
    setOnlineStatus,
    setAppActiveStatus,
    isDarkMode,
    effectiveTheme,
  }), [
    state,
    login,
    logout,
    updateUser,
    clearAuthError,
    setThemeMode,
    setPrimaryColor,
    setFontSize,
    toggleReducedMotion,
    toggleHighContrast,
    toggleNotification,
    setNotificationSettings,
    setOnlineStatus,
    setAppActiveStatus,
    isDarkMode,
    effectiveTheme,
  ]);

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

// ============================================================================
// HOOKS
// ============================================================================

export function useAppStore(): AppContextType {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppStore must be used within an AppProvider');
  }
  return context;
}

export function useAuth(): AuthState & {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  clearError: () => void;
} {
  const { state, login, logout, updateUser, clearAuthError } = useAppStore();
  
  return {
    ...state.auth,
    login,
    logout,
    updateUser,
    clearError: clearAuthError,
  };
}

export function useTheme(): ThemeState & {
  setMode: (mode: 'light' | 'dark' | 'system') => void;
  setPrimaryColor: (color: string) => void;
  setFontSize: (size: 'small' | 'medium' | 'large') => void;
  toggleReducedMotion: () => void;
  toggleHighContrast: () => void;
  isDarkMode: boolean;
  effectiveTheme: 'light' | 'dark';
} {
  const { 
    state, 
    setThemeMode, 
    setPrimaryColor, 
    setFontSize, 
    toggleReducedMotion, 
    toggleHighContrast,
    isDarkMode,
    effectiveTheme,
  } = useAppStore();
  
  return {
    ...state.theme,
    setMode: setThemeMode,
    setPrimaryColor,
    setFontSize,
    toggleReducedMotion,
    toggleHighContrast,
    isDarkMode,
    effectiveTheme,
  };
}

export function useNotifications(): NotificationState & {
  toggle: (type: keyof NotificationState) => void;
  setSettings: (settings: Partial<NotificationState>) => void;
} {
  const { state, toggleNotification, setNotificationSettings } = useAppStore();
  
  return {
    ...state.notifications,
    toggle: toggleNotification,
    setSettings: setNotificationSettings,
  };
}
import { AppState, AppStateStatus } from 'react-native';
import { useColorScheme } from 'react-native';
import { z } from 'zod';

// ============================================================================
// TYPES
// ============================================================================

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  avatar?: string;
  isEmailVerified: boolean;
  role: 'user' | 'admin' | 'moderator';
  createdAt: string;
  updatedAt: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
}

interface ThemeState {
  mode: 'light' | 'dark' | 'system';
  primaryColor: string;
  fontSize: 'small' | 'medium' | 'large';
  reducedMotion: boolean;
  highContrast: boolean;
}

interface NotificationState {
  email: boolean;
  push: boolean;
  sms: boolean;
  marketing: boolean;
  security: boolean;
  updates: boolean;
}

interface AppState {
  auth: AuthState;
  theme: ThemeState;
  notifications: NotificationState;
  isOnline: boolean;
  isAppActive: boolean;
  lastActiveTime: string | null;
}

// ============================================================================
// ACTION TYPES
// ============================================================================

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; accessToken: string; refreshToken: string } }
  | { type: 'AUTH_FAILURE'; payload: { error: string } }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_UPDATE_USER'; payload: { user: Partial<User> } }
  | { type: 'AUTH_CLEAR_ERROR' };

type ThemeAction =
  | { type: 'THEME_SET_MODE'; payload: { mode: 'light' | 'dark' | 'system' } }
  | { type: 'THEME_SET_PRIMARY_COLOR'; payload: { color: string } }
  | { type: 'THEME_SET_FONT_SIZE'; payload: { size: 'small' | 'medium' | 'large' } }
  | { type: 'THEME_TOGGLE_REDUCED_MOTION' }
  | { type: 'THEME_TOGGLE_HIGH_CONTRAST' };

type NotificationAction =
  | { type: 'NOTIFICATION_TOGGLE_EMAIL' }
  | { type: 'NOTIFICATION_TOGGLE_PUSH' }
  | { type: 'NOTIFICATION_TOGGLE_SMS' }
  | { type: 'NOTIFICATION_TOGGLE_MARKETING' }
  | { type: 'NOTIFICATION_TOGGLE_SECURITY' }
  | { type: 'NOTIFICATION_TOGGLE_UPDATES' }
  | { type: 'NOTIFICATION_SET_ALL'; payload: { settings: Partial<NotificationState> } };

type AppAction =
  | { type: 'APP_SET_ONLINE'; payload: { isOnline: boolean } }
  | { type: 'APP_SET_ACTIVE'; payload: { isActive: boolean } }
  | { type: 'APP_SET_LAST_ACTIVE'; payload: { timestamp: string } };

type Action = AuthAction | ThemeAction | NotificationAction | AppAction;

// ============================================================================
// VALIDATION SCHEMAS
// ============================================================================

const UserSchema = z.object({
  id: z.string(),
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email(),
  username: z.string(),
  avatar: z.string().optional(),
  isEmailVerified: z.boolean(),
  role: z.enum(['user', 'admin', 'moderator']),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialAuthState: AuthState = {
  isAuthenticated: false,
  user: null,
  accessToken: null,
  refreshToken: null,
  isLoading: false,
  error: null,
};

const initialThemeState: ThemeState = {
  mode: 'system',
  primaryColor: '#007AFF',
  fontSize: 'medium',
  reducedMotion: false,
  highContrast: false,
};

const initialNotificationState: NotificationState = {
  email: true,
  push: true,
  sms: false,
  marketing: false,
  security: true,
  updates: true,
};

const initialState: AppState = {
  auth: initialAuthState,
  theme: initialThemeState,
  notifications: initialNotificationState,
  isOnline: true,
  isAppActive: true,
  lastActiveTime: null,
};

// ============================================================================
// REDUCERS
// ============================================================================

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        accessToken: null,
        refreshToken: null,
        isLoading: false,
        error: action.payload.error,
      };
    case 'AUTH_LOGOUT':
      return {
        ...initialAuthState,
      };
    case 'AUTH_UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload.user } : null,
      };
    case 'AUTH_CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
}

function themeReducer(state: ThemeState, action: ThemeAction): ThemeState {
  switch (action.type) {
    case 'THEME_SET_MODE':
      return {
        ...state,
        mode: action.payload.mode,
      };
    case 'THEME_SET_PRIMARY_COLOR':
      return {
        ...state,
        primaryColor: action.payload.color,
      };
    case 'THEME_SET_FONT_SIZE':
      return {
        ...state,
        fontSize: action.payload.size,
      };
    case 'THEME_TOGGLE_REDUCED_MOTION':
      return {
        ...state,
        reducedMotion: !state.reducedMotion,
      };
    case 'THEME_TOGGLE_HIGH_CONTRAST':
      return {
        ...state,
        highContrast: !state.highContrast,
      };
    default:
      return state;
  }
}

function notificationReducer(state: NotificationState, action: NotificationAction): NotificationState {
  switch (action.type) {
    case 'NOTIFICATION_TOGGLE_EMAIL':
      return {
        ...state,
        email: !state.email,
      };
    case 'NOTIFICATION_TOGGLE_PUSH':
      return {
        ...state,
        push: !state.push,
      };
    case 'NOTIFICATION_TOGGLE_SMS':
      return {
        ...state,
        sms: !state.sms,
      };
    case 'NOTIFICATION_TOGGLE_MARKETING':
      return {
        ...state,
        marketing: !state.marketing,
      };
    case 'NOTIFICATION_TOGGLE_SECURITY':
      return {
        ...state,
        security: !state.security,
      };
    case 'NOTIFICATION_TOGGLE_UPDATES':
      return {
        ...state,
        updates: !state.updates,
      };
    case 'NOTIFICATION_SET_ALL':
      return {
        ...state,
        ...action.payload.settings,
      };
    default:
      return state;
  }
}

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'APP_SET_ONLINE':
      return {
        ...state,
        isOnline: action.payload.isOnline,
      };
    case 'APP_SET_ACTIVE':
      return {
        ...state,
        isAppActive: action.payload.isActive,
        lastActiveTime: action.payload.isActive ? new Date().toISOString() : state.lastActiveTime,
      };
    case 'APP_SET_LAST_ACTIVE':
      return {
        ...state,
        lastActiveTime: action.payload.timestamp,
      };
    default:
      return {
        ...state,
        auth: authReducer(state.auth, action as AuthAction),
        theme: themeReducer(state.theme, action as ThemeAction),
        notifications: notificationReducer(state.notifications, action as NotificationAction),
      };
  }
}

// ============================================================================
// CONTEXT
// ============================================================================

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<Action>;
  // Auth actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  clearAuthError: () => void;
  // Theme actions
  setThemeMode: (mode: 'light' | 'dark' | 'system') => void;
  setPrimaryColor: (color: string) => void;
  setFontSize: (size: 'small' | 'medium' | 'large') => void;
  toggleReducedMotion: () => void;
  toggleHighContrast: () => void;
  // Notification actions
  toggleNotification: (type: keyof NotificationState) => void;
  setNotificationSettings: (settings: Partial<NotificationState>) => void;
  // App actions
  setOnlineStatus: (isOnline: boolean) => void;
  setAppActiveStatus: (isActive: boolean) => void;
  // Computed values
  isDarkMode: boolean;
  effectiveTheme: 'light' | 'dark';
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// ============================================================================
// PROVIDER COMPONENT
// ============================================================================

interface AppProviderProps {
  children: React.ReactNode;
}

export function AppProvider({ children }: AppProviderProps): JSX.Element {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const systemColorScheme = useColorScheme();

  // Computed values
  const isDarkMode = useMemo(() => {
    if (state.theme.mode === 'system') {
      return systemColorScheme === 'dark';
    }
    return state.theme.mode === 'dark';
  }, [state.theme.mode, systemColorScheme]);

  const effectiveTheme = useMemo(() => {
    if (state.theme.mode === 'system') {
      return systemColorScheme || 'light';
    }
    return state.theme.mode;
  }, [state.theme.mode, systemColorScheme]);

  // Auth actions
  const login = useCallback(async (email: string, password: string): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock user data - in real app, this would come from API
      const mockUser: User = {
        id: '1',
        firstName: 'John',
        lastName: 'Doe',
        email,
        username: 'johndoe',
        isEmailVerified: true,
        role: 'user',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      // Validate user data with Zod
      const validatedUser = UserSchema.parse(mockUser);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: validatedUser,
          accessToken: 'mock-access-token',
          refreshToken: 'mock-refresh-token',
        },
      });
    } catch (error) {
      dispatch({
        type: 'AUTH_FAILURE',
        payload: {
          error: error instanceof Error ? error.message : 'Login failed',
        },
      });
    }
  }, []);

  const logout = useCallback((): void => {
    dispatch({ type: 'AUTH_LOGOUT' });
  }, []);

  const updateUser = useCallback((userData: Partial<User>): void => {
    dispatch({ type: 'AUTH_UPDATE_USER', payload: { user: userData } });
  }, []);

  const clearAuthError = useCallback((): void => {
    dispatch({ type: 'AUTH_CLEAR_ERROR' });
  }, []);

  // Theme actions
  const setThemeMode = useCallback((mode: 'light' | 'dark' | 'system'): void => {
    dispatch({ type: 'THEME_SET_MODE', payload: { mode } });
  }, []);

  const setPrimaryColor = useCallback((color: string): void => {
    dispatch({ type: 'THEME_SET_PRIMARY_COLOR', payload: { color } });
  }, []);

  const setFontSize = useCallback((size: 'small' | 'medium' | 'large'): void => {
    dispatch({ type: 'THEME_SET_FONT_SIZE', payload: { size } });
  }, []);

  const toggleReducedMotion = useCallback((): void => {
    dispatch({ type: 'THEME_TOGGLE_REDUCED_MOTION' });
  }, []);

  const toggleHighContrast = useCallback((): void => {
    dispatch({ type: 'THEME_TOGGLE_HIGH_CONTRAST' });
  }, []);

  // Notification actions
  const toggleNotification = useCallback((type: keyof NotificationState): void => {
    const actionMap: Record<keyof NotificationState, NotificationAction['type']> = {
      email: 'NOTIFICATION_TOGGLE_EMAIL',
      push: 'NOTIFICATION_TOGGLE_PUSH',
      sms: 'NOTIFICATION_TOGGLE_SMS',
      marketing: 'NOTIFICATION_TOGGLE_MARKETING',
      security: 'NOTIFICATION_TOGGLE_SECURITY',
      updates: 'NOTIFICATION_TOGGLE_UPDATES',
    };
    
    dispatch({ type: actionMap[type] });
  }, []);

  const setNotificationSettings = useCallback((settings: Partial<NotificationState>): void => {
    dispatch({ type: 'NOTIFICATION_SET_ALL', payload: { settings } });
  }, []);

  // App actions
  const setOnlineStatus = useCallback((isOnline: boolean): void => {
    dispatch({ type: 'APP_SET_ONLINE', payload: { isOnline } });
  }, []);

  const setAppActiveStatus = useCallback((isActive: boolean): void => {
    dispatch({ type: 'APP_SET_ACTIVE', payload: { isActive } });
  }, []);

  // App state monitoring
  React.useEffect(() => {
    const handleAppStateChange = (nextAppState: AppStateStatus): void => {
      setAppActiveStatus(nextAppState === 'active');
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, [setAppActiveStatus]);

  const contextValue: AppContextType = useMemo(() => ({
    state,
    dispatch,
    login,
    logout,
    updateUser,
    clearAuthError,
    setThemeMode,
    setPrimaryColor,
    setFontSize,
    toggleReducedMotion,
    toggleHighContrast,
    toggleNotification,
    setNotificationSettings,
    setOnlineStatus,
    setAppActiveStatus,
    isDarkMode,
    effectiveTheme,
  }), [
    state,
    login,
    logout,
    updateUser,
    clearAuthError,
    setThemeMode,
    setPrimaryColor,
    setFontSize,
    toggleReducedMotion,
    toggleHighContrast,
    toggleNotification,
    setNotificationSettings,
    setOnlineStatus,
    setAppActiveStatus,
    isDarkMode,
    effectiveTheme,
  ]);

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

// ============================================================================
// HOOKS
// ============================================================================

export function useAppStore(): AppContextType {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppStore must be used within an AppProvider');
  }
  return context;
}

export function useAuth(): AuthState & {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  clearError: () => void;
} {
  const { state, login, logout, updateUser, clearAuthError } = useAppStore();
  
  return {
    ...state.auth,
    login,
    logout,
    updateUser,
    clearError: clearAuthError,
  };
}

export function useTheme(): ThemeState & {
  setMode: (mode: 'light' | 'dark' | 'system') => void;
  setPrimaryColor: (color: string) => void;
  setFontSize: (size: 'small' | 'medium' | 'large') => void;
  toggleReducedMotion: () => void;
  toggleHighContrast: () => void;
  isDarkMode: boolean;
  effectiveTheme: 'light' | 'dark';
} {
  const { 
    state, 
    setThemeMode, 
    setPrimaryColor, 
    setFontSize, 
    toggleReducedMotion, 
    toggleHighContrast,
    isDarkMode,
    effectiveTheme,
  } = useAppStore();
  
  return {
    ...state.theme,
    setMode: setThemeMode,
    setPrimaryColor,
    setFontSize,
    toggleReducedMotion,
    toggleHighContrast,
    isDarkMode,
    effectiveTheme,
  };
}

export function useNotifications(): NotificationState & {
  toggle: (type: keyof NotificationState) => void;
  setSettings: (settings: Partial<NotificationState>) => void;
} {
  const { state, toggleNotification, setNotificationSettings } = useAppStore();
  
  return {
    ...state.notifications,
    toggle: toggleNotification,
    setSettings: setNotificationSettings,
  };
}


