// Test data and utilities for E2E tests

export const testUsers = {
  validUser: {
    email: 'test@example.com',
    password: 'password123',
    name: 'Test User'
  },
  invalidUser: {
    email: 'wrong@example.com',
    password: 'wrongpassword'
  },
  newUser: {
    name: 'New User',
    email: 'newuser@example.com',
    password: 'newpassword123',
    confirmPassword: 'newpassword123'
  }
};

export const testData = {
  apiKey: 'test-api-key-12345',
  searchQuery: 'test query',
  itemTitle: 'Test Item',
  itemDescription: 'This is a test item description'
};

export const testSelectors = {
  // Authentication
  loginScreen: 'login-screen',
  registerScreen: 'register-screen',
  emailInput: 'email-input',
  passwordInput: 'password-input',
  nameInput: 'name-input',
  confirmPasswordInput: 'confirm-password-input',
  loginButton: 'login-button',
  registerButton: 'register-button',
  forgotPasswordLink: 'forgot-password-link',
  biometricLoginButton: 'biometric-login-button',
  
  // Navigation
  homeTab: 'home-tab',
  profileTab: 'profile-tab',
  settingsTab: 'settings-tab',
  backButton: 'back-button',
  drawerToggleButton: 'drawer-toggle-button',
  
  // Screens
  homeScreen: 'home-screen',
  profileScreen: 'profile-screen',
  settingsScreen: 'settings-screen',
  detailScreen: 'detail-screen',
  helpScreen: 'help-screen',
  
  // Lists and Items
  homeList: 'home-list',
  homeListItem: (index) => `home-list-item-${index}`,
  selectedItemIndicator: 'selected-item-indicator',
  
  // Forms
  saveButton: 'save-button',
  submitButton: 'submit-button',
  apiKeyInput: 'api-key-input',
  
  // Modals and Overlays
  addItemButton: 'add-item-button',
  addItemModal: 'add-item-modal',
  modalTitleInput: 'modal-title-input',
  modalDescriptionInput: 'modal-description-input',
  modalSaveButton: 'modal-save-button',
  modalCloseButton: 'modal-close-button',
  closeModalButton: 'close-modal-button',
  
  // Search
  searchButton: 'search-button',
  searchInput: 'search-input',
  searchResults: 'search-results',
  searchFilterButton: 'search-filter-button',
  filterModal: 'filter-modal',
  filterOption: (index) => `filter-option-${index}`,
  applyFilterButton: 'apply-filter-button',
  filteredResults: 'filtered-results',
  
  // Actions
  refreshButton: 'refresh-button',
  deleteItemButton: 'delete-item-button',
  openModalButton: 'open-modal-button',
  
  // Status Indicators
  loadingIndicator: 'loading-indicator',
  refreshIndicator: 'refresh-indicator',
  successMessage: 'success-message',
  errorMessage: 'error-message',
  networkErrorMessage: 'network-error-message',
  validationError: 'validation-error',
  retryButton: 'retry-button',
  
  // Images
  detailImage: 'detail-image',
  imagePlaceholder: 'image-placeholder',
  imageErrorPlaceholder: 'image-error-placeholder',
  
  // Gestures
  swipeActions: 'swipe-actions',
  contextMenu: 'context-menu',
  swipeIndicator: 'swipe-indicator',
  
  // Accessibility
  highContrastIndicator: 'high-contrast-indicator',
  reducedMotionIndicator: 'reduced-motion-indicator',
  
  // Performance
  splashScreen: 'splash-screen'
};

export const testTimeouts = {
  short: 5000,
  medium: 10000,
  long: 20000,
  veryLong: 30000
};

export const testDelays = {
  short: 100,
  medium: 500,
  long: 1000
};

// Helper functions for test data generation
export const generateTestUser = (overrides = {}) => ({
  ...testUsers.validUser,
  ...overrides
});

export const generateTestItem = (overrides = {}) => ({
  title: testData.itemTitle,
  description: testData.itemDescription,
  ...overrides
});

// Mock data for API responses
export const mockApiResponses = {
  loginSuccess: {
    success: true,
    token: 'mock-jwt-token',
    user: testUsers.validUser
  },
  loginError: {
    success: false,
    error: 'Invalid credentials'
  },
  registerSuccess: {
    success: true,
    message: 'User registered successfully'
  },
  itemsList: {
    items: Array.from({ length: 20 }, (_, i) => ({
      id: i,
      title: `Item ${i}`,
      description: `Description for item ${i}`
    }))
  }
};

export const testUsers = {
  validUser: {
    email: 'test@example.com',
    password: 'password123',
    name: 'Test User'
  },
  invalidUser: {
    email: 'wrong@example.com',
    password: 'wrongpassword'
  },
  newUser: {
    name: 'New User',
    email: 'newuser@example.com',
    password: 'newpassword123',
    confirmPassword: 'newpassword123'
  }
};

export const testData = {
  apiKey: 'test-api-key-12345',
  searchQuery: 'test query',
  itemTitle: 'Test Item',
  itemDescription: 'This is a test item description'
};

export const testSelectors = {
  // Authentication
  loginScreen: 'login-screen',
  registerScreen: 'register-screen',
  emailInput: 'email-input',
  passwordInput: 'password-input',
  nameInput: 'name-input',
  confirmPasswordInput: 'confirm-password-input',
  loginButton: 'login-button',
  registerButton: 'register-button',
  forgotPasswordLink: 'forgot-password-link',
  biometricLoginButton: 'biometric-login-button',
  
  // Navigation
  homeTab: 'home-tab',
  profileTab: 'profile-tab',
  settingsTab: 'settings-tab',
  backButton: 'back-button',
  drawerToggleButton: 'drawer-toggle-button',
  
  // Screens
  homeScreen: 'home-screen',
  profileScreen: 'profile-screen',
  settingsScreen: 'settings-screen',
  detailScreen: 'detail-screen',
  helpScreen: 'help-screen',
  
  // Lists and Items
  homeList: 'home-list',
  homeListItem: (index) => `home-list-item-${index}`,
  selectedItemIndicator: 'selected-item-indicator',
  
  // Forms
  saveButton: 'save-button',
  submitButton: 'submit-button',
  apiKeyInput: 'api-key-input',
  
  // Modals and Overlays
  addItemButton: 'add-item-button',
  addItemModal: 'add-item-modal',
  modalTitleInput: 'modal-title-input',
  modalDescriptionInput: 'modal-description-input',
  modalSaveButton: 'modal-save-button',
  modalCloseButton: 'modal-close-button',
  closeModalButton: 'close-modal-button',
  
  // Search
  searchButton: 'search-button',
  searchInput: 'search-input',
  searchResults: 'search-results',
  searchFilterButton: 'search-filter-button',
  filterModal: 'filter-modal',
  filterOption: (index) => `filter-option-${index}`,
  applyFilterButton: 'apply-filter-button',
  filteredResults: 'filtered-results',
  
  // Actions
  refreshButton: 'refresh-button',
  deleteItemButton: 'delete-item-button',
  openModalButton: 'open-modal-button',
  
  // Status Indicators
  loadingIndicator: 'loading-indicator',
  refreshIndicator: 'refresh-indicator',
  successMessage: 'success-message',
  errorMessage: 'error-message',
  networkErrorMessage: 'network-error-message',
  validationError: 'validation-error',
  retryButton: 'retry-button',
  
  // Images
  detailImage: 'detail-image',
  imagePlaceholder: 'image-placeholder',
  imageErrorPlaceholder: 'image-error-placeholder',
  
  // Gestures
  swipeActions: 'swipe-actions',
  contextMenu: 'context-menu',
  swipeIndicator: 'swipe-indicator',
  
  // Accessibility
  highContrastIndicator: 'high-contrast-indicator',
  reducedMotionIndicator: 'reduced-motion-indicator',
  
  // Performance
  splashScreen: 'splash-screen'
};

export const testTimeouts = {
  short: 5000,
  medium: 10000,
  long: 20000,
  veryLong: 30000
};

export const testDelays = {
  short: 100,
  medium: 500,
  long: 1000
};

// Helper functions for test data generation
export const generateTestUser = (overrides = {}) => ({
  ...testUsers.validUser,
  ...overrides
});

export const generateTestItem = (overrides = {}) => ({
  title: testData.itemTitle,
  description: testData.itemDescription,
  ...overrides
});

// Mock data for API responses
export const mockApiResponses = {
  loginSuccess: {
    success: true,
    token: 'mock-jwt-token',
    user: testUsers.validUser
  },
  loginError: {
    success: false,
    error: 'Invalid credentials'
  },
  registerSuccess: {
    success: true,
    message: 'User registered successfully'
  },
  itemsList: {
    items: Array.from({ length: 20 }, (_, i) => ({
      id: i,
      title: `Item ${i}`,
      description: `Description for item ${i}`
    }))
  }
};


