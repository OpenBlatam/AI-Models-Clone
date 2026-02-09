import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { subscribeWithSelector } from 'zustand/middleware';
import { shallow } from 'zustand/shallow';

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'admin' | 'user' | 'moderator' | 'premium';
  isActive: boolean;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  sms: boolean;
  marketing: boolean;
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'friends';
  dataSharing: boolean;
  analytics: boolean;
}

export interface AppSettings {
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  headerHeight: number;
  footerVisible: boolean;
  breadcrumbsVisible: boolean;
  searchHistory: string[];
  recentPages: string[];
}

export interface UIState {
  isLoading: boolean;
  isSidebarOpen: boolean;
  isMobileMenuOpen: boolean;
  activeModal: string | null;
  activeDropdown: string | null;
  toastNotifications: ToastNotification[];
  globalError: string | null;
}

export interface ToastNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface AppState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  authToken: string | null;
  
  // App settings
  settings: AppSettings;
  
  // UI state
  ui: UIState;
  
  // Performance metrics
  performanceMetrics: {
    pageLoadTime: number;
    timeToFirstByte: number;
    timeToInteractive: number;
    firstContentfulPaint: number;
    largestContentfulPaint: number;
    cumulativeLayoutShift: number;
    firstInputDelay: number;
  };
  
  // Actions
  setUser: (user: User | null) => void;
  setAuthToken: (token: string | null) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  
  // Settings actions
  updateSettings: (settings: Partial<AppSettings>) => void;
  toggleSidebar: () => void;
  setSidebarWidth: (width: number) => void;
  addSearchHistory: (query: string) => void;
  addRecentPage: (page: string) => void;
  
  // UI actions
  setLoading: (isLoading: boolean) => void;
  setSidebarOpen: (isOpen: boolean) => void;
  setMobileMenuOpen: (isOpen: boolean) => void;
  setActiveModal: (modalId: string | null) => void;
  setActiveDropdown: (dropdownId: string | null) => void;
  addToast: (notification: Omit<ToastNotification, 'id'>) => void;
  removeToast: (id: string) => void;
  setGlobalError: (error: string | null) => void;
  
  // Performance actions
  updatePerformanceMetrics: (metrics: Partial<AppState['performanceMetrics']>) => void;
  
  // Utility actions
  resetApp: () => void;
  logout: () => void;
}

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  authToken: null,
  
  settings: {
    sidebarCollapsed: false,
    sidebarWidth: 280,
    headerHeight: 64,
    footerVisible: true,
    breadcrumbsVisible: true,
    searchHistory: [],
    recentPages: [],
  },
  
  ui: {
    isLoading: false,
    isSidebarOpen: true,
    isMobileMenuOpen: false,
    activeModal: null,
    activeDropdown: null,
    toastNotifications: [],
    globalError: null,
  },
  
  performanceMetrics: {
    pageLoadTime: 0,
    timeToFirstByte: 0,
    timeToInteractive: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    cumulativeLayoutShift: 0,
    firstInputDelay: 0,
  },
};

// Create store
export const useAppStore = create<AppState>()(
  subscribeWithSelector(
    persist(
      (set, get) => ({
        ...initialState,
        
        // User actions
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        setAuthToken: (token) => set({ authToken: token }),
        setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
        
        // Settings actions
        updateSettings: (newSettings) =>
          set((state) => ({
            settings: { ...state.settings, ...newSettings },
          })),
        
        toggleSidebar: () =>
          set((state) => ({
            settings: {
              ...state.settings,
              sidebarCollapsed: !state.settings.sidebarCollapsed,
            },
          })),
        
        setSidebarWidth: (width) =>
          set((state) => ({
            settings: { ...state.settings, sidebarWidth: width },
          })),
        
        addSearchHistory: (query) =>
          set((state) => {
            const history = state.settings.searchHistory.filter((q) => q !== query);
            return {
              settings: {
                ...state.settings,
                searchHistory: [query, ...history].slice(0, 10),
              },
            };
          }),
        
        addRecentPage: (page) =>
          set((state) => {
            const pages = state.settings.recentPages.filter((p) => p !== page);
            return {
              settings: {
                ...state.settings,
                recentPages: [page, ...pages].slice(0, 5),
              },
            };
          }),
        
        // UI actions
        setLoading: (isLoading) =>
          set((state) => ({
            ui: { ...state.ui, isLoading },
          })),
        
        setSidebarOpen: (isOpen) =>
          set((state) => ({
            ui: { ...state.ui, isSidebarOpen: isOpen },
          })),
        
        setMobileMenuOpen: (isOpen) =>
          set((state) => ({
            ui: { ...state.ui, isMobileMenuOpen: isOpen },
          })),
        
        setActiveModal: (modalId) =>
          set((state) => ({
            ui: { ...state.ui, activeModal: modalId },
          })),
        
        setActiveDropdown: (dropdownId) =>
          set((state) => ({
            ui: { ...state.ui, activeDropdown: dropdownId },
          })),
        
        addToast: (notification) =>
          set((state) => ({
            ui: {
              ...state.ui,
              toastNotifications: [
                ...state.ui.toastNotifications,
                { ...notification, id: Date.now().toString() },
              ],
            },
          })),
        
        removeToast: (id) =>
          set((state) => ({
            ui: {
              ...state.ui,
              toastNotifications: state.ui.toastNotifications.filter(
                (toast) => toast.id !== id
              ),
            },
          })),
        
        setGlobalError: (error) =>
          set((state) => ({
            ui: { ...state.ui, globalError: error },
          })),
        
        // Performance actions
        updatePerformanceMetrics: (metrics) =>
          set((state) => ({
            performanceMetrics: { ...state.performanceMetrics, ...metrics },
          })),
        
        // Utility actions
        resetApp: () => set(initialState),
        
        logout: () =>
          set({
            user: null,
            isAuthenticated: false,
            authToken: null,
            ui: {
              ...initialState.ui,
              toastNotifications: [],
              globalError: null,
            },
          }),
      }),
      {
        name: 'app-storage',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          authToken: state.authToken,
          settings: state.settings,
        }),
      }
    )
  )
);

// Selectors for better performance
export const useUser = () => useAppStore((state) => state.user);
export const useIsAuthenticated = () => useAppStore((state) => state.isAuthenticated);
export const useAuthToken = () => useAppStore((state) => state.authToken);

export const useSettings = () => useAppStore((state) => state.settings);
export const useSidebarCollapsed = () => useAppStore((state) => state.settings.sidebarCollapsed);
export const useSidebarWidth = () => useAppStore((state) => state.settings.sidebarWidth);
export const useSearchHistory = () => useAppStore((state) => state.settings.searchHistory);
export const useRecentPages = () => useAppStore((state) => state.settings.recentPages);

export const useUI = () => useAppStore((state) => state.ui);
export const useIsLoading = () => useAppStore((state) => state.ui.isLoading);
export const useIsSidebarOpen = () => useAppStore((state) => state.ui.isSidebarOpen);
export const useIsMobileMenuOpen = () => useAppStore((state) => state.ui.isMobileMenuOpen);
export const useActiveModal = () => useAppStore((state) => state.ui.activeModal);
export const useActiveDropdown = () => useAppStore((state) => state.ui.activeDropdown);
export const useToastNotifications = () => useAppStore((state) => state.ui.toastNotifications);
export const useGlobalError = () => useAppStore((state) => state.ui.globalError);

export const usePerformanceMetrics = () => useAppStore((state) => state.performanceMetrics);

// Actions
export const useAppActions = () =>
  useAppStore(
    (state) => ({
      setUser: state.setUser,
      setAuthToken: state.setAuthToken,
      setAuthenticated: state.setAuthenticated,
      updateSettings: state.updateSettings,
      toggleSidebar: state.toggleSidebar,
      setSidebarWidth: state.setSidebarWidth,
      addSearchHistory: state.addSearchHistory,
      addRecentPage: state.addRecentPage,
      setLoading: state.setLoading,
      setSidebarOpen: state.setSidebarOpen,
      setMobileMenuOpen: state.setMobileMenuOpen,
      setActiveModal: state.setActiveModal,
      setActiveDropdown: state.setActiveDropdown,
      addToast: state.addToast,
      removeToast: state.removeToast,
      setGlobalError: state.setGlobalError,
      updatePerformanceMetrics: state.updatePerformanceMetrics,
      resetApp: state.resetApp,
      logout: state.logout,
    }),
    shallow
  );

// Subscribe to specific state changes
export const useAppStoreSubscribe = (selector: (state: AppState) => any, callback: (value: any) => void) => {
  const value = selector(useAppStore.getState());
  useAppStore.subscribe(selector, callback);
  return value;
};

// Dev tools (only in development)
if (process.env.NODE_ENV === 'development') {
  // Expose store to window for debugging
  (window as any).__APP_STORE__ = useAppStore;
}
