# E2E Testing with Detox

This directory contains end-to-end (E2E) tests for the Blaze AI Mobile application using Detox.

## Setup

### Prerequisites

1. **iOS Setup** (for iOS testing):
   ```bash
   # Install Xcode and iOS Simulator
   # Create a new iOS project in Xcode
   # Build the project to generate the .app file
   ```

2. **Android Setup** (for Android testing):
   ```bash
   # Install Android Studio and SDK
   # Create an Android Virtual Device (AVD)
   # Build the Android project
   ```

### Installation

1. Install Detox CLI globally:
   ```bash
   npm install -g detox-cli
   ```

2. Build the app for testing:
   ```bash
   # For iOS
   detox build --configuration ios.sim.debug
   
   # For Android
   detox build --configuration android.emu.debug
   ```

## Running Tests

### Run All Tests
```bash
npm run test:e2e
```

### Run Specific Test Suites
```bash
# Authentication tests
detox test --configuration ios.sim.debug e2e/flows/authentication.test.js

# Navigation tests
detox test --configuration ios.sim.debug e2e/flows/navigation.test.js

# User interaction tests
detox test --configuration ios.sim.debug e2e/flows/user-interactions.test.js

# Performance tests
detox test --configuration ios.sim.debug e2e/flows/performance.test.js
```

### Run Tests on Different Platforms
```bash
# iOS Simulator
detox test --configuration ios.sim.debug

# Android Emulator
detox test --configuration android.emu.debug

# Physical Android Device
detox test --configuration android.att.debug
```

## Test Structure

### Test Files

- **`authentication.test.js`** - Tests user authentication flows including login, registration, logout, and biometric authentication
- **`navigation.test.js`** - Tests navigation patterns including tab navigation, stack navigation, drawer navigation, deep linking, and modal navigation
- **`user-interactions.test.js`** - Tests user interactions including form handling, list interactions, search, gestures, and accessibility
- **`performance.test.js`** - Tests app performance including launch time, navigation speed, list rendering, image loading, and memory usage

### Helper Files

- **`test-data.js`** - Contains test data, selectors, timeouts, and mock API responses
- **`test-utils.js`** - Enhanced utility functions for common test operations
- **`setup.js`** - Global test setup and configuration

## Test Configuration

### Detox Configuration (`.detoxrc.js`)

The Detox configuration defines:
- Test runner settings (Jest)
- App configurations for different platforms
- Device configurations (simulators, emulators, physical devices)
- Build commands for iOS and Android

### Jest Configuration (`e2e/jest.config.js`)

Jest configuration for E2E tests includes:
- Test file patterns
- Setup files
- Transform ignore patterns
- Timeout settings

## Writing Tests

### Basic Test Structure

```javascript
describe('Feature Name', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
    // Setup code
  });

  it('should perform specific action', async () => {
    // Test implementation
    await global.testUtils.waitForElement('element-id');
    await global.testUtils.tapElement('button-id');
    await expect(element(by.id('result-id'))).toBeVisible();
  });
});
```

### Using Test Utilities

```javascript
// Wait for elements
await global.testUtils.waitForElement('login-screen');
await global.testUtils.waitForElementToDisappear('loading-indicator');

// Interact with elements
await global.testUtils.tapElement('login-button');
await global.testUtils.typeText('email-input', 'test@example.com');

// Navigation
await global.testUtils.navigateToTab('profile');
await global.testUtils.navigateBack();

// Forms
await global.testUtils.fillForm({
  email: 'test@example.com',
  password: 'password123'
});

// Authentication
await global.testUtils.login('test@example.com', 'password123');
await global.testUtils.logout();
```

### Best Practices

1. **Use descriptive test names** that clearly indicate what is being tested
2. **Group related tests** in describe blocks
3. **Use beforeEach/afterEach** for setup and cleanup
4. **Wait for elements** before interacting with them
5. **Use test utilities** for common operations
6. **Handle async operations** properly with await
7. **Clean up state** between tests
8. **Use meaningful selectors** that are stable and descriptive

## Debugging Tests

### Taking Screenshots
```javascript
await global.testUtils.takeScreenshot('test-step-1');
```

### Debugging Failed Tests
1. Check the test logs for error messages
2. Take screenshots at key points
3. Verify element selectors are correct
4. Check if the app is in the expected state
5. Use `detox test --loglevel trace` for detailed logging

### Common Issues

1. **Element not found**: Verify the testID exists in the component
2. **Timeout errors**: Increase timeout values or check if the element is actually visible
3. **Build failures**: Ensure the app builds successfully before running tests
4. **Simulator/Emulator issues**: Restart the simulator/emulator and rebuild the app

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: detox build --configuration ios.sim.debug
      - run: detox test --configuration ios.sim.debug
```

## Maintenance

### Updating Tests

1. **When adding new features**: Add corresponding E2E tests
2. **When changing UI**: Update test selectors and expectations
3. **When modifying navigation**: Update navigation test flows
4. **When changing authentication**: Update authentication test flows

### Test Data Management

- Keep test data in `test-data.js` for easy maintenance
- Use realistic but non-sensitive test data
- Update test data when API contracts change

### Performance Monitoring

- Monitor test execution time
- Optimize slow tests
- Use parallel execution where possible
- Keep tests focused and fast

## Resources

- [Detox Documentation](https://github.com/wix/Detox)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Native Testing](https://reactnative.dev/docs/testing-overview)
- [Expo Testing](https://docs.expo.dev/guides/testing-with-jest/)

This directory contains end-to-end (E2E) tests for the Blaze AI Mobile application using Detox.

## Setup

### Prerequisites

1. **iOS Setup** (for iOS testing):
   ```bash
   # Install Xcode and iOS Simulator
   # Create a new iOS project in Xcode
   # Build the project to generate the .app file
   ```

2. **Android Setup** (for Android testing):
   ```bash
   # Install Android Studio and SDK
   # Create an Android Virtual Device (AVD)
   # Build the Android project
   ```

### Installation

1. Install Detox CLI globally:
   ```bash
   npm install -g detox-cli
   ```

2. Build the app for testing:
   ```bash
   # For iOS
   detox build --configuration ios.sim.debug
   
   # For Android
   detox build --configuration android.emu.debug
   ```

## Running Tests

### Run All Tests
```bash
npm run test:e2e
```

### Run Specific Test Suites
```bash
# Authentication tests
detox test --configuration ios.sim.debug e2e/flows/authentication.test.js

# Navigation tests
detox test --configuration ios.sim.debug e2e/flows/navigation.test.js

# User interaction tests
detox test --configuration ios.sim.debug e2e/flows/user-interactions.test.js

# Performance tests
detox test --configuration ios.sim.debug e2e/flows/performance.test.js
```

### Run Tests on Different Platforms
```bash
# iOS Simulator
detox test --configuration ios.sim.debug

# Android Emulator
detox test --configuration android.emu.debug

# Physical Android Device
detox test --configuration android.att.debug
```

## Test Structure

### Test Files

- **`authentication.test.js`** - Tests user authentication flows including login, registration, logout, and biometric authentication
- **`navigation.test.js`** - Tests navigation patterns including tab navigation, stack navigation, drawer navigation, deep linking, and modal navigation
- **`user-interactions.test.js`** - Tests user interactions including form handling, list interactions, search, gestures, and accessibility
- **`performance.test.js`** - Tests app performance including launch time, navigation speed, list rendering, image loading, and memory usage

### Helper Files

- **`test-data.js`** - Contains test data, selectors, timeouts, and mock API responses
- **`test-utils.js`** - Enhanced utility functions for common test operations
- **`setup.js`** - Global test setup and configuration

## Test Configuration

### Detox Configuration (`.detoxrc.js`)

The Detox configuration defines:
- Test runner settings (Jest)
- App configurations for different platforms
- Device configurations (simulators, emulators, physical devices)
- Build commands for iOS and Android

### Jest Configuration (`e2e/jest.config.js`)

Jest configuration for E2E tests includes:
- Test file patterns
- Setup files
- Transform ignore patterns
- Timeout settings

## Writing Tests

### Basic Test Structure

```javascript
describe('Feature Name', () => {
  beforeEach(async () => {
    await device.reloadReactNative();
    // Setup code
  });

  it('should perform specific action', async () => {
    // Test implementation
    await global.testUtils.waitForElement('element-id');
    await global.testUtils.tapElement('button-id');
    await expect(element(by.id('result-id'))).toBeVisible();
  });
});
```

### Using Test Utilities

```javascript
// Wait for elements
await global.testUtils.waitForElement('login-screen');
await global.testUtils.waitForElementToDisappear('loading-indicator');

// Interact with elements
await global.testUtils.tapElement('login-button');
await global.testUtils.typeText('email-input', 'test@example.com');

// Navigation
await global.testUtils.navigateToTab('profile');
await global.testUtils.navigateBack();

// Forms
await global.testUtils.fillForm({
  email: 'test@example.com',
  password: 'password123'
});

// Authentication
await global.testUtils.login('test@example.com', 'password123');
await global.testUtils.logout();
```

### Best Practices

1. **Use descriptive test names** that clearly indicate what is being tested
2. **Group related tests** in describe blocks
3. **Use beforeEach/afterEach** for setup and cleanup
4. **Wait for elements** before interacting with them
5. **Use test utilities** for common operations
6. **Handle async operations** properly with await
7. **Clean up state** between tests
8. **Use meaningful selectors** that are stable and descriptive

## Debugging Tests

### Taking Screenshots
```javascript
await global.testUtils.takeScreenshot('test-step-1');
```

### Debugging Failed Tests
1. Check the test logs for error messages
2. Take screenshots at key points
3. Verify element selectors are correct
4. Check if the app is in the expected state
5. Use `detox test --loglevel trace` for detailed logging

### Common Issues

1. **Element not found**: Verify the testID exists in the component
2. **Timeout errors**: Increase timeout values or check if the element is actually visible
3. **Build failures**: Ensure the app builds successfully before running tests
4. **Simulator/Emulator issues**: Restart the simulator/emulator and rebuild the app

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: detox build --configuration ios.sim.debug
      - run: detox test --configuration ios.sim.debug
```

## Maintenance

### Updating Tests

1. **When adding new features**: Add corresponding E2E tests
2. **When changing UI**: Update test selectors and expectations
3. **When modifying navigation**: Update navigation test flows
4. **When changing authentication**: Update authentication test flows

### Test Data Management

- Keep test data in `test-data.js` for easy maintenance
- Use realistic but non-sensitive test data
- Update test data when API contracts change

### Performance Monitoring

- Monitor test execution time
- Optimize slow tests
- Use parallel execution where possible
- Keep tests focused and fast

## Resources

- [Detox Documentation](https://github.com/wix/Detox)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Native Testing](https://reactnative.dev/docs/testing-overview)
- [Expo Testing](https://docs.expo.dev/guides/testing-with-jest/)


