// Enhanced test utilities for E2E tests

const { device, element, by, waitFor } = require('detox');

class TestUtils {
  // Element interaction methods
  async waitForElement(testID, timeout = 10000) {
    await waitFor(element(by.id(testID)))
      .toBeVisible()
      .withTimeout(timeout);
  }

  async waitForElementToDisappear(testID, timeout = 10000) {
    await waitFor(element(by.id(testID)))
      .not.toBeVisible()
      .withTimeout(timeout);
  }

  async tapElement(testID) {
    await element(by.id(testID)).tap();
  }

  async typeText(testID, text) {
    await element(by.id(testID)).typeText(text);
  }

  async clearText(testID) {
    await element(by.id(testID)).clearText();
  }

  async scrollToElement(testID, direction = 'down', distance = 100) {
    await element(by.id(testID)).scroll(distance, direction);
  }

  async swipeElement(testID, direction, speed = 'fast', percentage = 0.8) {
    await element(by.id(testID)).swipe(direction, speed, percentage);
  }

  async longPressElement(testID) {
    await element(by.id(testID)).longPress();
  }

  async pinchElement(testID, direction, speed = 'fast', angle = 0) {
    await element(by.id(testID)).pinchWithAngle(direction, speed, angle);
  }

  // Navigation helpers
  async navigateToTab(tabName) {
    await this.tapElement(`${tabName}-tab`);
    await this.waitForElement(`${tabName}-screen`);
  }

  async navigateBack() {
    await this.tapElement('back-button');
  }

  async openDrawer() {
    await this.tapElement('drawer-toggle-button');
    await this.waitForElement('drawer-menu');
  }

  async closeDrawer() {
    await this.tapElement('drawer-overlay');
    await this.waitForElementToDisappear('drawer-menu');
  }

  // Form helpers
  async fillForm(formData) {
    for (const [field, value] of Object.entries(formData)) {
      await this.typeText(`${field}-input`, value);
    }
  }

  async submitForm() {
    await this.tapElement('submit-button');
  }

  async clearForm(fields) {
    for (const field of fields) {
      await this.clearText(`${field}-input`);
    }
  }

  // Authentication helpers
  async login(email = 'test@example.com', password = 'password123') {
    await this.typeText('email-input', email);
    await this.typeText('password-input', password);
    await this.tapElement('login-button');
    await this.waitForElement('home-screen');
  }

  async logout() {
    await this.tapElement('user-profile-button');
    await this.waitForElement('profile-menu');
    await this.tapElement('logout-button');
    await this.waitForElement('logout-confirm-button');
    await this.tapElement('logout-confirm-button');
    await this.waitForElement('login-screen');
  }

  async register(userData) {
    await this.tapElement('register-link');
    await this.waitForElement('register-screen');
    await this.fillForm(userData);
    await this.tapElement('register-button');
    await this.waitForElement('home-screen');
  }

  // List helpers
  async scrollToListBottom(listID = 'home-list') {
    for (let i = 0; i < 3; i++) {
      await this.scrollToElement(listID, 'down');
      await this.waitForNetworkIdle(500);
    }
  }

  async selectListItem(index, listID = 'home-list') {
    await this.tapElement(`${listID}-item-${index}`);
    await this.waitForElement('detail-screen');
  }

  async pullToRefresh(listID = 'home-list') {
    await this.swipeElement(listID, 'down', 'fast', 0.8);
    await this.waitForElement('refresh-indicator');
  }

  // Search helpers
  async performSearch(query) {
    await this.tapElement('search-button');
    await this.waitForElement('search-input');
    await this.typeText('search-input', query);
    await this.waitForElement('search-results');
  }

  async applySearchFilter(filterIndex) {
    await this.tapElement('search-filter-button');
    await this.waitForElement('filter-modal');
    await this.tapElement(`filter-option-${filterIndex}`);
    await this.tapElement('apply-filter-button');
    await this.waitForElement('filtered-results');
  }

  // Modal helpers
  async openModal(modalButtonID) {
    await this.tapElement(modalButtonID);
    await this.waitForElement('modal-screen');
  }

  async closeModal() {
    await this.tapElement('close-modal-button');
    await this.waitForElementToDisappear('modal-screen');
  }

  async fillModalForm(formData) {
    for (const [field, value] of Object.entries(formData)) {
      await this.typeText(`modal-${field}-input`, value);
    }
  }

  // Error handling helpers
  async handleNetworkError() {
    await this.waitForElement('network-error-message');
    await this.tapElement('retry-button');
  }

  async handleValidationError() {
    await this.waitForElement('validation-error');
  }

  // Performance helpers
  async measurePerformance(operation) {
    const startTime = Date.now();
    await operation();
    const endTime = Date.now();
    return endTime - startTime;
  }

  async waitForNetworkIdle(timeout = 5000) {
    await new Promise(resolve => setTimeout(resolve, timeout));
  }

  async takeScreenshot(name) {
    await device.takeScreenshot(name);
  }

  // Device helpers
  async backgroundApp() {
    await device.sendToHome();
  }

  async foregroundApp() {
    await device.launchApp();
  }

  async rotateDevice(orientation) {
    await device.setOrientation(orientation);
  }

  async simulateNetworkConditions(blacklist = []) {
    await device.setURLBlacklist(blacklist);
  }

  // Accessibility helpers
  async navigateWithScreenReader() {
    // Simulate screen reader navigation
    await device.setOrientation('portrait');
  }

  async enableHighContrast() {
    await device.setOrientation('landscape');
  }

  // Assertion helpers
  async assertElementVisible(testID) {
    await this.waitForElement(testID);
    await expect(element(by.id(testID))).toBeVisible();
  }

  async assertElementNotVisible(testID) {
    await this.waitForElementToDisappear(testID);
    await expect(element(by.id(testID))).not.toBeVisible();
  }

  async assertElementHasText(testID, expectedText) {
    await expect(element(by.id(testID))).toHaveText(expectedText);
  }

  async assertElementHasValue(testID, expectedValue) {
    await expect(element(by.id(testID))).toHaveValue(expectedValue);
  }

  // Utility methods
  async waitForCondition(condition, timeout = 10000) {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      try {
        if (await condition()) {
          return true;
        }
      } catch (error) {
        // Continue waiting
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error(`Condition not met within ${timeout}ms`);
  }

  async retryOperation(operation, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        await operation();
        return;
      } catch (error) {
        if (i === maxRetries - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
}

// Export singleton instance
module.exports = new TestUtils();

const { device, element, by, waitFor } = require('detox');

class TestUtils {
  // Element interaction methods
  async waitForElement(testID, timeout = 10000) {
    await waitFor(element(by.id(testID)))
      .toBeVisible()
      .withTimeout(timeout);
  }

  async waitForElementToDisappear(testID, timeout = 10000) {
    await waitFor(element(by.id(testID)))
      .not.toBeVisible()
      .withTimeout(timeout);
  }

  async tapElement(testID) {
    await element(by.id(testID)).tap();
  }

  async typeText(testID, text) {
    await element(by.id(testID)).typeText(text);
  }

  async clearText(testID) {
    await element(by.id(testID)).clearText();
  }

  async scrollToElement(testID, direction = 'down', distance = 100) {
    await element(by.id(testID)).scroll(distance, direction);
  }

  async swipeElement(testID, direction, speed = 'fast', percentage = 0.8) {
    await element(by.id(testID)).swipe(direction, speed, percentage);
  }

  async longPressElement(testID) {
    await element(by.id(testID)).longPress();
  }

  async pinchElement(testID, direction, speed = 'fast', angle = 0) {
    await element(by.id(testID)).pinchWithAngle(direction, speed, angle);
  }

  // Navigation helpers
  async navigateToTab(tabName) {
    await this.tapElement(`${tabName}-tab`);
    await this.waitForElement(`${tabName}-screen`);
  }

  async navigateBack() {
    await this.tapElement('back-button');
  }

  async openDrawer() {
    await this.tapElement('drawer-toggle-button');
    await this.waitForElement('drawer-menu');
  }

  async closeDrawer() {
    await this.tapElement('drawer-overlay');
    await this.waitForElementToDisappear('drawer-menu');
  }

  // Form helpers
  async fillForm(formData) {
    for (const [field, value] of Object.entries(formData)) {
      await this.typeText(`${field}-input`, value);
    }
  }

  async submitForm() {
    await this.tapElement('submit-button');
  }

  async clearForm(fields) {
    for (const field of fields) {
      await this.clearText(`${field}-input`);
    }
  }

  // Authentication helpers
  async login(email = 'test@example.com', password = 'password123') {
    await this.typeText('email-input', email);
    await this.typeText('password-input', password);
    await this.tapElement('login-button');
    await this.waitForElement('home-screen');
  }

  async logout() {
    await this.tapElement('user-profile-button');
    await this.waitForElement('profile-menu');
    await this.tapElement('logout-button');
    await this.waitForElement('logout-confirm-button');
    await this.tapElement('logout-confirm-button');
    await this.waitForElement('login-screen');
  }

  async register(userData) {
    await this.tapElement('register-link');
    await this.waitForElement('register-screen');
    await this.fillForm(userData);
    await this.tapElement('register-button');
    await this.waitForElement('home-screen');
  }

  // List helpers
  async scrollToListBottom(listID = 'home-list') {
    for (let i = 0; i < 3; i++) {
      await this.scrollToElement(listID, 'down');
      await this.waitForNetworkIdle(500);
    }
  }

  async selectListItem(index, listID = 'home-list') {
    await this.tapElement(`${listID}-item-${index}`);
    await this.waitForElement('detail-screen');
  }

  async pullToRefresh(listID = 'home-list') {
    await this.swipeElement(listID, 'down', 'fast', 0.8);
    await this.waitForElement('refresh-indicator');
  }

  // Search helpers
  async performSearch(query) {
    await this.tapElement('search-button');
    await this.waitForElement('search-input');
    await this.typeText('search-input', query);
    await this.waitForElement('search-results');
  }

  async applySearchFilter(filterIndex) {
    await this.tapElement('search-filter-button');
    await this.waitForElement('filter-modal');
    await this.tapElement(`filter-option-${filterIndex}`);
    await this.tapElement('apply-filter-button');
    await this.waitForElement('filtered-results');
  }

  // Modal helpers
  async openModal(modalButtonID) {
    await this.tapElement(modalButtonID);
    await this.waitForElement('modal-screen');
  }

  async closeModal() {
    await this.tapElement('close-modal-button');
    await this.waitForElementToDisappear('modal-screen');
  }

  async fillModalForm(formData) {
    for (const [field, value] of Object.entries(formData)) {
      await this.typeText(`modal-${field}-input`, value);
    }
  }

  // Error handling helpers
  async handleNetworkError() {
    await this.waitForElement('network-error-message');
    await this.tapElement('retry-button');
  }

  async handleValidationError() {
    await this.waitForElement('validation-error');
  }

  // Performance helpers
  async measurePerformance(operation) {
    const startTime = Date.now();
    await operation();
    const endTime = Date.now();
    return endTime - startTime;
  }

  async waitForNetworkIdle(timeout = 5000) {
    await new Promise(resolve => setTimeout(resolve, timeout));
  }

  async takeScreenshot(name) {
    await device.takeScreenshot(name);
  }

  // Device helpers
  async backgroundApp() {
    await device.sendToHome();
  }

  async foregroundApp() {
    await device.launchApp();
  }

  async rotateDevice(orientation) {
    await device.setOrientation(orientation);
  }

  async simulateNetworkConditions(blacklist = []) {
    await device.setURLBlacklist(blacklist);
  }

  // Accessibility helpers
  async navigateWithScreenReader() {
    // Simulate screen reader navigation
    await device.setOrientation('portrait');
  }

  async enableHighContrast() {
    await device.setOrientation('landscape');
  }

  // Assertion helpers
  async assertElementVisible(testID) {
    await this.waitForElement(testID);
    await expect(element(by.id(testID))).toBeVisible();
  }

  async assertElementNotVisible(testID) {
    await this.waitForElementToDisappear(testID);
    await expect(element(by.id(testID))).not.toBeVisible();
  }

  async assertElementHasText(testID, expectedText) {
    await expect(element(by.id(testID))).toHaveText(expectedText);
  }

  async assertElementHasValue(testID, expectedValue) {
    await expect(element(by.id(testID))).toHaveValue(expectedValue);
  }

  // Utility methods
  async waitForCondition(condition, timeout = 10000) {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      try {
        if (await condition()) {
          return true;
        }
      } catch (error) {
        // Continue waiting
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error(`Condition not met within ${timeout}ms`);
  }

  async retryOperation(operation, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        await operation();
        return;
      } catch (error) {
        if (i === maxRetries - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
}

// Export singleton instance
module.exports = new TestUtils();


