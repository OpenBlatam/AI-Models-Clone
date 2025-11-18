const { device, expect, element, by, waitFor } = require('detox');

describe('Navigation Flow', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
    // Login first
    await global.testUtils.typeText('email-input', 'test@example.com');
    await global.testUtils.typeText('password-input', 'password123');
    await global.testUtils.tapElement('login-button');
    await global.testUtils.waitForElement('home-screen');
  });

  describe('Tab Navigation', () => {
    it('should navigate between tabs', async () => {
      // Test Home tab
      await global.testUtils.tapElement('home-tab');
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();

      // Test Profile tab
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      await expect(element(by.id('profile-screen'))).toBeVisible();

      // Test Settings tab
      await global.testUtils.tapElement('settings-tab');
      await global.testUtils.waitForElement('settings-screen');
      await expect(element(by.id('settings-screen'))).toBeVisible();
    });

    it('should maintain tab state when switching', async () => {
      // Navigate to profile and perform an action
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Switch to settings and back
      await global.testUtils.tapElement('settings-tab');
      await global.testUtils.tapElement('profile-tab');
      
      // Profile screen should still be visible
      await expect(element(by.id('profile-screen'))).toBeVisible();
    });
  });

  describe('Stack Navigation', () => {
    it('should navigate to detail screen from home', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Tap on a list item
      await global.testUtils.tapElement('home-list-item-0');
      
      // Should navigate to detail screen
      await global.testUtils.waitForElement('detail-screen');
      await expect(element(by.id('detail-screen'))).toBeVisible();
    });

    it('should navigate back from detail screen', async () => {
      // Navigate to detail screen
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Navigate back
      await global.testUtils.tapElement('back-button');
      
      // Should return to home screen
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
    });

    it('should handle deep navigation stack', async () => {
      // Navigate to detail screen
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Navigate to sub-detail screen
      await global.testUtils.tapElement('detail-action-button');
      await global.testUtils.waitForElement('sub-detail-screen');
      
      // Navigate back twice
      await global.testUtils.tapElement('back-button');
      await global.testUtils.waitForElement('detail-screen');
      
      await global.testUtils.tapElement('back-button');
      await global.testUtils.waitForElement('home-screen');
    });
  });

  describe('Drawer Navigation', () => {
    it('should open and close drawer', async () => {
      await global.testUtils.tapElement('drawer-toggle-button');
      await global.testUtils.waitForElement('drawer-menu');
      await expect(element(by.id('drawer-menu'))).toBeVisible();
      
      // Close drawer by tapping outside
      await global.testUtils.tapElement('drawer-overlay');
      await global.testUtils.waitForElementToDisappear('drawer-menu');
    });

    it('should navigate to different screens from drawer', async () => {
      await global.testUtils.tapElement('drawer-toggle-button');
      await global.testUtils.waitForElement('drawer-menu');
      
      // Navigate to help screen
      await global.testUtils.tapElement('drawer-help-item');
      await global.testUtils.waitForElement('help-screen');
      await expect(element(by.id('help-screen'))).toBeVisible();
    });
  });

  describe('Deep Linking', () => {
    it('should handle deep link to specific screen', async () => {
      // Simulate deep link
      await device.openURL({
        url: 'blazeai://profile/settings'
      });
      
      await global.testUtils.waitForElement('settings-screen');
      await expect(element(by.id('settings-screen'))).toBeVisible();
    });

    it('should handle deep link with parameters', async () => {
      await device.openURL({
        url: 'blazeai://detail/123'
      });
      
      await global.testUtils.waitForElement('detail-screen');
      await expect(element(by.id('detail-screen'))).toBeVisible();
      
      // Verify parameter was passed
      await expect(element(by.id('detail-id-123'))).toBeVisible();
    });
  });

  describe('Modal Navigation', () => {
    it('should open and close modal', async () => {
      await global.testUtils.tapElement('open-modal-button');
      await global.testUtils.waitForElement('modal-screen');
      await expect(element(by.id('modal-screen'))).toBeVisible();
      
      // Close modal
      await global.testUtils.tapElement('close-modal-button');
      await global.testUtils.waitForElementToDisappear('modal-screen');
    });

    it('should handle modal with navigation', async () => {
      await global.testUtils.tapElement('open-modal-button');
      await global.testUtils.waitForElement('modal-screen');
      
      // Navigate within modal
      await global.testUtils.tapElement('modal-next-button');
      await global.testUtils.waitForElement('modal-step-2');
      
      // Close modal
      await global.testUtils.tapElement('modal-close-button');
      await global.testUtils.waitForElementToDisappear('modal-screen');
    });
  });

  describe('Navigation State Persistence', () => {
    it('should restore navigation state after app backgrounding', async () => {
      // Navigate to a specific screen
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Background the app
      await device.sendToHome();
      await device.launchApp();
      
      // Should restore to profile screen
      await global.testUtils.waitForElement('profile-screen');
      await expect(element(by.id('profile-screen'))).toBeVisible();
    });
  });
});

describe('Navigation Flow', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
    // Login first
    await global.testUtils.typeText('email-input', 'test@example.com');
    await global.testUtils.typeText('password-input', 'password123');
    await global.testUtils.tapElement('login-button');
    await global.testUtils.waitForElement('home-screen');
  });

  describe('Tab Navigation', () => {
    it('should navigate between tabs', async () => {
      // Test Home tab
      await global.testUtils.tapElement('home-tab');
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();

      // Test Profile tab
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      await expect(element(by.id('profile-screen'))).toBeVisible();

      // Test Settings tab
      await global.testUtils.tapElement('settings-tab');
      await global.testUtils.waitForElement('settings-screen');
      await expect(element(by.id('settings-screen'))).toBeVisible();
    });

    it('should maintain tab state when switching', async () => {
      // Navigate to profile and perform an action
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Switch to settings and back
      await global.testUtils.tapElement('settings-tab');
      await global.testUtils.tapElement('profile-tab');
      
      // Profile screen should still be visible
      await expect(element(by.id('profile-screen'))).toBeVisible();
    });
  });

  describe('Stack Navigation', () => {
    it('should navigate to detail screen from home', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Tap on a list item
      await global.testUtils.tapElement('home-list-item-0');
      
      // Should navigate to detail screen
      await global.testUtils.waitForElement('detail-screen');
      await expect(element(by.id('detail-screen'))).toBeVisible();
    });

    it('should navigate back from detail screen', async () => {
      // Navigate to detail screen
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Navigate back
      await global.testUtils.tapElement('back-button');
      
      // Should return to home screen
      await global.testUtils.waitForElement('home-screen');
      await expect(element(by.id('home-screen'))).toBeVisible();
    });

    it('should handle deep navigation stack', async () => {
      // Navigate to detail screen
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Navigate to sub-detail screen
      await global.testUtils.tapElement('detail-action-button');
      await global.testUtils.waitForElement('sub-detail-screen');
      
      // Navigate back twice
      await global.testUtils.tapElement('back-button');
      await global.testUtils.waitForElement('detail-screen');
      
      await global.testUtils.tapElement('back-button');
      await global.testUtils.waitForElement('home-screen');
    });
  });

  describe('Drawer Navigation', () => {
    it('should open and close drawer', async () => {
      await global.testUtils.tapElement('drawer-toggle-button');
      await global.testUtils.waitForElement('drawer-menu');
      await expect(element(by.id('drawer-menu'))).toBeVisible();
      
      // Close drawer by tapping outside
      await global.testUtils.tapElement('drawer-overlay');
      await global.testUtils.waitForElementToDisappear('drawer-menu');
    });

    it('should navigate to different screens from drawer', async () => {
      await global.testUtils.tapElement('drawer-toggle-button');
      await global.testUtils.waitForElement('drawer-menu');
      
      // Navigate to help screen
      await global.testUtils.tapElement('drawer-help-item');
      await global.testUtils.waitForElement('help-screen');
      await expect(element(by.id('help-screen'))).toBeVisible();
    });
  });

  describe('Deep Linking', () => {
    it('should handle deep link to specific screen', async () => {
      // Simulate deep link
      await device.openURL({
        url: 'blazeai://profile/settings'
      });
      
      await global.testUtils.waitForElement('settings-screen');
      await expect(element(by.id('settings-screen'))).toBeVisible();
    });

    it('should handle deep link with parameters', async () => {
      await device.openURL({
        url: 'blazeai://detail/123'
      });
      
      await global.testUtils.waitForElement('detail-screen');
      await expect(element(by.id('detail-screen'))).toBeVisible();
      
      // Verify parameter was passed
      await expect(element(by.id('detail-id-123'))).toBeVisible();
    });
  });

  describe('Modal Navigation', () => {
    it('should open and close modal', async () => {
      await global.testUtils.tapElement('open-modal-button');
      await global.testUtils.waitForElement('modal-screen');
      await expect(element(by.id('modal-screen'))).toBeVisible();
      
      // Close modal
      await global.testUtils.tapElement('close-modal-button');
      await global.testUtils.waitForElementToDisappear('modal-screen');
    });

    it('should handle modal with navigation', async () => {
      await global.testUtils.tapElement('open-modal-button');
      await global.testUtils.waitForElement('modal-screen');
      
      // Navigate within modal
      await global.testUtils.tapElement('modal-next-button');
      await global.testUtils.waitForElement('modal-step-2');
      
      // Close modal
      await global.testUtils.tapElement('modal-close-button');
      await global.testUtils.waitForElementToDisappear('modal-screen');
    });
  });

  describe('Navigation State Persistence', () => {
    it('should restore navigation state after app backgrounding', async () => {
      // Navigate to a specific screen
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Background the app
      await device.sendToHome();
      await device.launchApp();
      
      // Should restore to profile screen
      await global.testUtils.waitForElement('profile-screen');
      await expect(element(by.id('profile-screen'))).toBeVisible();
    });
  });
});


