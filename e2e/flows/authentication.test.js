const { device, expect, element, by, waitFor } = require('detox');

describe('Authentication Flow', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
  });

  describe('Login Flow', () => {
    it('should display login screen on app launch', async () => {
      await global.testUtils.waitForElement('login-screen');
      await expect(element(by.id('login-screen'))).toBeVisible();
    });

    it('should show validation errors for empty fields', async () => {
      await global.testUtils.waitForElement('login-button');
      await global.testUtils.tapElement('login-button');
      
      await global.testUtils.waitForElement('email-error');
      await global.testUtils.waitForElement('password-error');
      
      await expect(element(by.id('email-error'))).toBeVisible();
      await expect(element(by.id('password-error'))).toBeVisible();
    });

    it('should show validation error for invalid email format', async () => {
      await global.testUtils.typeText('email-input', 'invalid-email');
      await global.testUtils.tapElement('login-button');
      
      await global.testUtils.waitForElement('email-error');
      await expect(element(by.id('email-error'))).toBeVisible();
    });

    it('should successfully login with valid credentials', async () => {
      await global.testUtils.typeText('email-input', 'test@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.tapElement('login-button');
      
      // Wait for navigation to home screen
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
      
      // Verify user is logged in
      await expect(element(by.id('user-profile-button'))).toBeVisible();
    });

    it('should show error for invalid credentials', async () => {
      await global.testUtils.typeText('email-input', 'wrong@example.com');
      await global.testUtils.typeText('password-input', 'wrongpassword');
      await global.testUtils.tapElement('login-button');
      
      await global.testUtils.waitForElement('login-error-message');
      await expect(element(by.id('login-error-message'))).toBeVisible();
    });

    it('should navigate to forgot password screen', async () => {
      await global.testUtils.waitForElement('forgot-password-link');
      await global.testUtils.tapElement('forgot-password-link');
      
      await global.testUtils.waitForElement('forgot-password-screen');
      await expect(element(by.id('forgot-password-screen'))).toBeVisible();
    });
  });

  describe('Registration Flow', () => {
    it('should navigate to registration screen', async () => {
      await global.testUtils.waitForElement('register-link');
      await global.testUtils.tapElement('register-link');
      
      await global.testUtils.waitForElement('register-screen');
      await expect(element(by.id('register-screen'))).toBeVisible();
    });

    it('should validate registration form fields', async () => {
      await global.testUtils.tapElement('register-link');
      await global.testUtils.waitForElement('register-screen');
      
      await global.testUtils.tapElement('register-button');
      
      // Check for validation errors
      await global.testUtils.waitForElement('name-error');
      await global.testUtils.waitForElement('email-error');
      await global.testUtils.waitForElement('password-error');
      await global.testUtils.waitForElement('confirm-password-error');
    });

    it('should show error for password mismatch', async () => {
      await global.testUtils.tapElement('register-link');
      await global.testUtils.waitForElement('register-screen');
      
      await global.testUtils.typeText('name-input', 'Test User');
      await global.testUtils.typeText('email-input', 'test@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.typeText('confirm-password-input', 'differentpassword');
      
      await global.testUtils.tapElement('register-button');
      
      await global.testUtils.waitForElement('password-mismatch-error');
      await expect(element(by.id('password-mismatch-error'))).toBeVisible();
    });

    it('should successfully register new user', async () => {
      await global.testUtils.tapElement('register-link');
      await global.testUtils.waitForElement('register-screen');
      
      await global.testUtils.typeText('name-input', 'Test User');
      await global.testUtils.typeText('email-input', 'newuser@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.typeText('confirm-password-input', 'password123');
      
      await global.testUtils.tapElement('register-button');
      
      // Wait for successful registration and navigation
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
    });
  });

  describe('Logout Flow', () => {
    beforeEach(async () => {
      // Login first
      await global.testUtils.typeText('email-input', 'test@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.tapElement('login-button');
      await global.testUtils.waitForElement('home-screen');
    });

    it('should logout successfully', async () => {
      await global.testUtils.tapElement('user-profile-button');
      await global.testUtils.waitForElement('profile-menu');
      
      await global.testUtils.tapElement('logout-button');
      
      // Confirm logout
      await global.testUtils.waitForElement('logout-confirm-button');
      await global.testUtils.tapElement('logout-confirm-button');
      
      // Should return to login screen
      await global.testUtils.waitForElement('login-screen');
      await expect(element(by.id('login-screen'))).toBeVisible();
    });
  });

  describe('Biometric Authentication', () => {
    it('should show biometric login option when available', async () => {
      await global.testUtils.waitForElement('biometric-login-button');
      await expect(element(by.id('biometric-login-button'))).toBeVisible();
    });

    it('should authenticate with biometrics', async () => {
      await global.testUtils.tapElement('biometric-login-button');
      
      // Wait for biometric prompt and authentication
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
    });
  });
});

describe('Authentication Flow', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
  });

  describe('Login Flow', () => {
    it('should display login screen on app launch', async () => {
      await global.testUtils.waitForElement('login-screen');
      await expect(element(by.id('login-screen'))).toBeVisible();
    });

    it('should show validation errors for empty fields', async () => {
      await global.testUtils.waitForElement('login-button');
      await global.testUtils.tapElement('login-button');
      
      await global.testUtils.waitForElement('email-error');
      await global.testUtils.waitForElement('password-error');
      
      await expect(element(by.id('email-error'))).toBeVisible();
      await expect(element(by.id('password-error'))).toBeVisible();
    });

    it('should show validation error for invalid email format', async () => {
      await global.testUtils.typeText('email-input', 'invalid-email');
      await global.testUtils.tapElement('login-button');
      
      await global.testUtils.waitForElement('email-error');
      await expect(element(by.id('email-error'))).toBeVisible();
    });

    it('should successfully login with valid credentials', async () => {
      await global.testUtils.typeText('email-input', 'test@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.tapElement('login-button');
      
      // Wait for navigation to home screen
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
      
      // Verify user is logged in
      await expect(element(by.id('user-profile-button'))).toBeVisible();
    });

    it('should show error for invalid credentials', async () => {
      await global.testUtils.typeText('email-input', 'wrong@example.com');
      await global.testUtils.typeText('password-input', 'wrongpassword');
      await global.testUtils.tapElement('login-button');
      
      await global.testUtils.waitForElement('login-error-message');
      await expect(element(by.id('login-error-message'))).toBeVisible();
    });

    it('should navigate to forgot password screen', async () => {
      await global.testUtils.waitForElement('forgot-password-link');
      await global.testUtils.tapElement('forgot-password-link');
      
      await global.testUtils.waitForElement('forgot-password-screen');
      await expect(element(by.id('forgot-password-screen'))).toBeVisible();
    });
  });

  describe('Registration Flow', () => {
    it('should navigate to registration screen', async () => {
      await global.testUtils.waitForElement('register-link');
      await global.testUtils.tapElement('register-link');
      
      await global.testUtils.waitForElement('register-screen');
      await expect(element(by.id('register-screen'))).toBeVisible();
    });

    it('should validate registration form fields', async () => {
      await global.testUtils.tapElement('register-link');
      await global.testUtils.waitForElement('register-screen');
      
      await global.testUtils.tapElement('register-button');
      
      // Check for validation errors
      await global.testUtils.waitForElement('name-error');
      await global.testUtils.waitForElement('email-error');
      await global.testUtils.waitForElement('password-error');
      await global.testUtils.waitForElement('confirm-password-error');
    });

    it('should show error for password mismatch', async () => {
      await global.testUtils.tapElement('register-link');
      await global.testUtils.waitForElement('register-screen');
      
      await global.testUtils.typeText('name-input', 'Test User');
      await global.testUtils.typeText('email-input', 'test@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.typeText('confirm-password-input', 'differentpassword');
      
      await global.testUtils.tapElement('register-button');
      
      await global.testUtils.waitForElement('password-mismatch-error');
      await expect(element(by.id('password-mismatch-error'))).toBeVisible();
    });

    it('should successfully register new user', async () => {
      await global.testUtils.tapElement('register-link');
      await global.testUtils.waitForElement('register-screen');
      
      await global.testUtils.typeText('name-input', 'Test User');
      await global.testUtils.typeText('email-input', 'newuser@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.typeText('confirm-password-input', 'password123');
      
      await global.testUtils.tapElement('register-button');
      
      // Wait for successful registration and navigation
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
    });
  });

  describe('Logout Flow', () => {
    beforeEach(async () => {
      // Login first
      await global.testUtils.typeText('email-input', 'test@example.com');
      await global.testUtils.typeText('password-input', 'password123');
      await global.testUtils.tapElement('login-button');
      await global.testUtils.waitForElement('home-screen');
    });

    it('should logout successfully', async () => {
      await global.testUtils.tapElement('user-profile-button');
      await global.testUtils.waitForElement('profile-menu');
      
      await global.testUtils.tapElement('logout-button');
      
      // Confirm logout
      await global.testUtils.waitForElement('logout-confirm-button');
      await global.testUtils.tapElement('logout-confirm-button');
      
      // Should return to login screen
      await global.testUtils.waitForElement('login-screen');
      await expect(element(by.id('login-screen'))).toBeVisible();
    });
  });

  describe('Biometric Authentication', () => {
    it('should show biometric login option when available', async () => {
      await global.testUtils.waitForElement('biometric-login-button');
      await expect(element(by.id('biometric-login-button'))).toBeVisible();
    });

    it('should authenticate with biometrics', async () => {
      await global.testUtils.tapElement('biometric-login-button');
      
      // Wait for biometric prompt and authentication
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
    });
  });
});


