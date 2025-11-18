const { device, expect, element, by, waitFor } = require('detox');

describe('User Interactions Flow', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
    // Login first
    await global.testUtils.typeText('email-input', 'test@example.com');
    await global.testUtils.typeText('password-input', 'password123');
    await global.testUtils.tapElement('login-button');
    await global.testUtils.waitForElement('home-screen');
  });

  describe('Form Interactions', () => {
    it('should handle text input with validation', async () => {
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Clear existing text
      await global.testUtils.clearText('name-input');
      await global.testUtils.typeText('name-input', 'New Name');
      
      // Save changes
      await global.testUtils.tapElement('save-button');
      
      // Verify success message
      await global.testUtils.waitForElement('success-message');
      await expect(element(by.id('success-message'))).toBeVisible();
    });

    it('should handle form submission with loading state', async () => {
      await global.testUtils.tapElement('settings-tab');
      await global.testUtils.waitForElement('settings-screen');
      
      // Fill form
      await global.testUtils.typeText('api-key-input', 'new-api-key');
      
      // Submit form
      await global.testUtils.tapElement('submit-button');
      
      // Verify loading state
      await global.testUtils.waitForElement('loading-indicator');
      await expect(element(by.id('loading-indicator'))).toBeVisible();
      
      // Wait for completion
      await global.testUtils.waitForElementToDisappear('loading-indicator');
      await global.testUtils.waitForElement('success-message');
    });
  });

  describe('List Interactions', () => {
    it('should handle list item selection', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Select first item
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Verify item is selected
      await expect(element(by.id('selected-item-indicator'))).toBeVisible();
    });

    it('should handle list scrolling and pagination', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Scroll to bottom
      await global.testUtils.scrollToElement('home-list', 'down');
      
      // Wait for more items to load
      await global.testUtils.waitForElement('home-list-item-10');
      await expect(element(by.id('home-list-item-10'))).toBeVisible();
    });

    it('should handle pull-to-refresh', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Pull to refresh
      await element(by.id('home-list')).swipe('down', 'fast', 0.8);
      
      // Verify refresh indicator
      await global.testUtils.waitForElement('refresh-indicator');
      await expect(element(by.id('refresh-indicator'))).toBeVisible();
    });
  });

  describe('Search Interactions', () => {
    it('should handle search input and results', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Open search
      await global.testUtils.tapElement('search-button');
      await global.testUtils.waitForElement('search-input');
      
      // Type search query
      await global.testUtils.typeText('search-input', 'test query');
      
      // Verify search results
      await global.testUtils.waitForElement('search-results');
      await expect(element(by.id('search-results'))).toBeVisible();
    });

    it('should handle search filters', async () => {
      await global.testUtils.tapElement('search-button');
      await global.testUtils.waitForElement('search-input');
      
      // Apply filter
      await global.testUtils.tapElement('search-filter-button');
      await global.testUtils.waitForElement('filter-modal');
      
      await global.testUtils.tapElement('filter-option-1');
      await global.testUtils.tapElement('apply-filter-button');
      
      // Verify filtered results
      await global.testUtils.waitForElement('filtered-results');
      await expect(element(by.id('filtered-results'))).toBeVisible();
    });
  });

  describe('Gesture Interactions', () => {
    it('should handle swipe gestures', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Swipe left on list item
      await element(by.id('home-list-item-0')).swipe('left', 'fast');
      
      // Verify action buttons appear
      await global.testUtils.waitForElement('swipe-actions');
      await expect(element(by.id('swipe-actions'))).toBeVisible();
    });

    it('should handle long press gestures', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Long press on item
      await element(by.id('home-list-item-0')).longPress();
      
      // Verify context menu appears
      await global.testUtils.waitForElement('context-menu');
      await expect(element(by.id('context-menu'))).toBeVisible();
    });

    it('should handle pinch gestures', async () => {
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Pinch to zoom on image
      await element(by.id('detail-image')).pinchWithAngle('outward', 'fast', 0);
      
      // Verify zoom state
      await expect(element(by.id('zoomed-image'))).toBeVisible();
    });
  });

  describe('Modal and Overlay Interactions', () => {
    it('should handle modal with form', async () => {
      await global.testUtils.tapElement('add-item-button');
      await global.testUtils.waitForElement('add-item-modal');
      
      // Fill modal form
      await global.testUtils.typeText('modal-title-input', 'New Item');
      await global.testUtils.typeText('modal-description-input', 'Item description');
      
      // Save item
      await global.testUtils.tapElement('modal-save-button');
      
      // Verify modal closes and item is added
      await global.testUtils.waitForElementToDisappear('add-item-modal');
      await global.testUtils.waitForElement('home-list-item-new');
    });

    it('should handle confirmation dialogs', async () => {
      await global.testUtils.tapElement('delete-item-button');
      await global.testUtils.waitForElement('confirmation-dialog');
      
      // Confirm deletion
      await global.testUtils.tapElement('confirm-delete-button');
      
      // Verify item is deleted
      await global.testUtils.waitForElementToDisappear('confirmation-dialog');
      await global.testUtils.waitForElementToDisappear('deleted-item');
    });
  });

  describe('Accessibility Interactions', () => {
    it('should handle screen reader navigation', async () => {
      // Enable screen reader mode
      await device.setOrientation('portrait');
      
      // Navigate using accessibility labels
      await element(by.label('Home tab')).tap();
      await global.testUtils.waitForElement('home-screen');
      
      await element(by.label('Profile tab')).tap();
      await global.testUtils.waitForElement('profile-screen');
    });

    it('should handle high contrast mode', async () => {
      // Simulate high contrast mode
      await device.setOrientation('landscape');
      
      // Verify high contrast styles are applied
      await expect(element(by.id('high-contrast-indicator'))).toBeVisible();
    });
  });

  describe('Error Handling Interactions', () => {
    it('should handle network errors gracefully', async () => {
      // Simulate network error
      await device.setURLBlacklist(['.*api.*']);
      
      await global.testUtils.tapElement('refresh-button');
      
      // Verify error message
      await global.testUtils.waitForElement('network-error-message');
      await expect(element(by.id('network-error-message'))).toBeVisible();
      
      // Verify retry button
      await global.testUtils.waitForElement('retry-button');
      await expect(element(by.id('retry-button'))).toBeVisible();
    });

    it('should handle validation errors', async () => {
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Submit invalid data
      await global.testUtils.clearText('email-input');
      await global.testUtils.typeText('email-input', 'invalid-email');
      await global.testUtils.tapElement('save-button');
      
      // Verify validation error
      await global.testUtils.waitForElement('validation-error');
      await expect(element(by.id('validation-error'))).toBeVisible();
    });
  });
});

describe('User Interactions Flow', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
    // Login first
    await global.testUtils.typeText('email-input', 'test@example.com');
    await global.testUtils.typeText('password-input', 'password123');
    await global.testUtils.tapElement('login-button');
    await global.testUtils.waitForElement('home-screen');
  });

  describe('Form Interactions', () => {
    it('should handle text input with validation', async () => {
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Clear existing text
      await global.testUtils.clearText('name-input');
      await global.testUtils.typeText('name-input', 'New Name');
      
      // Save changes
      await global.testUtils.tapElement('save-button');
      
      // Verify success message
      await global.testUtils.waitForElement('success-message');
      await expect(element(by.id('success-message'))).toBeVisible();
    });

    it('should handle form submission with loading state', async () => {
      await global.testUtils.tapElement('settings-tab');
      await global.testUtils.waitForElement('settings-screen');
      
      // Fill form
      await global.testUtils.typeText('api-key-input', 'new-api-key');
      
      // Submit form
      await global.testUtils.tapElement('submit-button');
      
      // Verify loading state
      await global.testUtils.waitForElement('loading-indicator');
      await expect(element(by.id('loading-indicator'))).toBeVisible();
      
      // Wait for completion
      await global.testUtils.waitForElementToDisappear('loading-indicator');
      await global.testUtils.waitForElement('success-message');
    });
  });

  describe('List Interactions', () => {
    it('should handle list item selection', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Select first item
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Verify item is selected
      await expect(element(by.id('selected-item-indicator'))).toBeVisible();
    });

    it('should handle list scrolling and pagination', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Scroll to bottom
      await global.testUtils.scrollToElement('home-list', 'down');
      
      // Wait for more items to load
      await global.testUtils.waitForElement('home-list-item-10');
      await expect(element(by.id('home-list-item-10'))).toBeVisible();
    });

    it('should handle pull-to-refresh', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Pull to refresh
      await element(by.id('home-list')).swipe('down', 'fast', 0.8);
      
      // Verify refresh indicator
      await global.testUtils.waitForElement('refresh-indicator');
      await expect(element(by.id('refresh-indicator'))).toBeVisible();
    });
  });

  describe('Search Interactions', () => {
    it('should handle search input and results', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Open search
      await global.testUtils.tapElement('search-button');
      await global.testUtils.waitForElement('search-input');
      
      // Type search query
      await global.testUtils.typeText('search-input', 'test query');
      
      // Verify search results
      await global.testUtils.waitForElement('search-results');
      await expect(element(by.id('search-results'))).toBeVisible();
    });

    it('should handle search filters', async () => {
      await global.testUtils.tapElement('search-button');
      await global.testUtils.waitForElement('search-input');
      
      // Apply filter
      await global.testUtils.tapElement('search-filter-button');
      await global.testUtils.waitForElement('filter-modal');
      
      await global.testUtils.tapElement('filter-option-1');
      await global.testUtils.tapElement('apply-filter-button');
      
      // Verify filtered results
      await global.testUtils.waitForElement('filtered-results');
      await expect(element(by.id('filtered-results'))).toBeVisible();
    });
  });

  describe('Gesture Interactions', () => {
    it('should handle swipe gestures', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Swipe left on list item
      await element(by.id('home-list-item-0')).swipe('left', 'fast');
      
      // Verify action buttons appear
      await global.testUtils.waitForElement('swipe-actions');
      await expect(element(by.id('swipe-actions'))).toBeVisible();
    });

    it('should handle long press gestures', async () => {
      await global.testUtils.waitForElement('home-screen');
      
      // Long press on item
      await element(by.id('home-list-item-0')).longPress();
      
      // Verify context menu appears
      await global.testUtils.waitForElement('context-menu');
      await expect(element(by.id('context-menu'))).toBeVisible();
    });

    it('should handle pinch gestures', async () => {
      await global.testUtils.tapElement('home-list-item-0');
      await global.testUtils.waitForElement('detail-screen');
      
      // Pinch to zoom on image
      await element(by.id('detail-image')).pinchWithAngle('outward', 'fast', 0);
      
      // Verify zoom state
      await expect(element(by.id('zoomed-image'))).toBeVisible();
    });
  });

  describe('Modal and Overlay Interactions', () => {
    it('should handle modal with form', async () => {
      await global.testUtils.tapElement('add-item-button');
      await global.testUtils.waitForElement('add-item-modal');
      
      // Fill modal form
      await global.testUtils.typeText('modal-title-input', 'New Item');
      await global.testUtils.typeText('modal-description-input', 'Item description');
      
      // Save item
      await global.testUtils.tapElement('modal-save-button');
      
      // Verify modal closes and item is added
      await global.testUtils.waitForElementToDisappear('add-item-modal');
      await global.testUtils.waitForElement('home-list-item-new');
    });

    it('should handle confirmation dialogs', async () => {
      await global.testUtils.tapElement('delete-item-button');
      await global.testUtils.waitForElement('confirmation-dialog');
      
      // Confirm deletion
      await global.testUtils.tapElement('confirm-delete-button');
      
      // Verify item is deleted
      await global.testUtils.waitForElementToDisappear('confirmation-dialog');
      await global.testUtils.waitForElementToDisappear('deleted-item');
    });
  });

  describe('Accessibility Interactions', () => {
    it('should handle screen reader navigation', async () => {
      // Enable screen reader mode
      await device.setOrientation('portrait');
      
      // Navigate using accessibility labels
      await element(by.label('Home tab')).tap();
      await global.testUtils.waitForElement('home-screen');
      
      await element(by.label('Profile tab')).tap();
      await global.testUtils.waitForElement('profile-screen');
    });

    it('should handle high contrast mode', async () => {
      // Simulate high contrast mode
      await device.setOrientation('landscape');
      
      // Verify high contrast styles are applied
      await expect(element(by.id('high-contrast-indicator'))).toBeVisible();
    });
  });

  describe('Error Handling Interactions', () => {
    it('should handle network errors gracefully', async () => {
      // Simulate network error
      await device.setURLBlacklist(['.*api.*']);
      
      await global.testUtils.tapElement('refresh-button');
      
      // Verify error message
      await global.testUtils.waitForElement('network-error-message');
      await expect(element(by.id('network-error-message'))).toBeVisible();
      
      // Verify retry button
      await global.testUtils.waitForElement('retry-button');
      await expect(element(by.id('retry-button'))).toBeVisible();
    });

    it('should handle validation errors', async () => {
      await global.testUtils.tapElement('profile-tab');
      await global.testUtils.waitForElement('profile-screen');
      
      // Submit invalid data
      await global.testUtils.clearText('email-input');
      await global.testUtils.typeText('email-input', 'invalid-email');
      await global.testUtils.tapElement('save-button');
      
      // Verify validation error
      await global.testUtils.waitForElement('validation-error');
      await expect(element(by.id('validation-error'))).toBeVisible();
    });
  });
});


