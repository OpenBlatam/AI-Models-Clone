const { device, expect, element, by, waitFor } = require('detox');

beforeAll(async () => {
  await device.launchApp();
});

beforeEach(async () => {
  await device.reloadReactNative();
});

afterAll(async () => {
  await device.terminateApp();
});

// Global test utilities
global.testUtils = {
  // Wait for element to be visible
  waitForElement: async (testID, timeout = 10000) => {
    await waitFor(element(by.id(testID)))
      .toBeVisible()
      .withTimeout(timeout);
  },

  // Wait for element to be not visible
  waitForElementToDisappear: async (testID, timeout = 10000) => {
    await waitFor(element(by.id(testID)))
      .not.toBeVisible()
      .withTimeout(timeout);
  },

  // Tap element by testID
  tapElement: async (testID) => {
    await element(by.id(testID)).tap();
  },

  // Type text into input field
  typeText: async (testID, text) => {
    await element(by.id(testID)).typeText(text);
  },

  // Clear text from input field
  clearText: async (testID) => {
    await element(by.id(testID)).clearText();
  },

  // Scroll to element
  scrollToElement: async (testID, direction = 'down') => {
    await element(by.id(testID)).scroll(100, direction);
  },

  // Take screenshot
  takeScreenshot: async (name) => {
    await device.takeScreenshot(name);
  },

  // Wait for network requests to complete
  waitForNetworkIdle: async (timeout = 5000) => {
    await new Promise(resolve => setTimeout(resolve, timeout));
  }
};

beforeAll(async () => {
  await device.launchApp();
});

beforeEach(async () => {
  await device.reloadReactNative();
});

afterAll(async () => {
  await device.terminateApp();
});

// Global test utilities
global.testUtils = {
  // Wait for element to be visible
  waitForElement: async (testID, timeout = 10000) => {
    await waitFor(element(by.id(testID)))
      .toBeVisible()
      .withTimeout(timeout);
  },

  // Wait for element to be not visible
  waitForElementToDisappear: async (testID, timeout = 10000) => {
    await waitFor(element(by.id(testID)))
      .not.toBeVisible()
      .withTimeout(timeout);
  },

  // Tap element by testID
  tapElement: async (testID) => {
    await element(by.id(testID)).tap();
  },

  // Type text into input field
  typeText: async (testID, text) => {
    await element(by.id(testID)).typeText(text);
  },

  // Clear text from input field
  clearText: async (testID) => {
    await element(by.id(testID)).clearText();
  },

  // Scroll to element
  scrollToElement: async (testID, direction = 'down') => {
    await element(by.id(testID)).scroll(100, direction);
  },

  // Take screenshot
  takeScreenshot: async (name) => {
    await device.takeScreenshot(name);
  },

  // Wait for network requests to complete
  waitForNetworkIdle: async (timeout = 5000) => {
    await new Promise(resolve => setTimeout(resolve, timeout));
  }
};


