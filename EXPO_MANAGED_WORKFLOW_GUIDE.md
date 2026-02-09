# Expo Managed Workflow Guide

## Overview

The Expo Managed Workflow provides a streamlined development and deployment experience for React Native applications. This guide covers the comprehensive system for managing Expo projects from initialization to production deployment.

## Key Features

### 1. Project Management
- **Automated Initialization**: Create new Expo projects with templates
- **Dependency Management**: Automated installation and configuration
- **Configuration Management**: Centralized app.json and eas.json management

### 2. Development Workflow
- **Development Server**: Hot reloading and debugging
- **Development Builds**: Native builds for testing
- **Testing Integration**: Automated test execution

### 3. Deployment Workflow
- **EAS Builds**: Cloud-based builds for iOS and Android
- **Store Submission**: Automated app store deployment
- **Over-the-Air Updates**: Instant updates without store approval

### 4. Service Integration
- **Push Notifications**: Expo Notifications integration
- **Analytics**: Built-in analytics and monitoring
- **Updates**: Seamless update management

## Installation

### Prerequisites
```bash
# Install Node.js and npm
node --version  # Should be >= 16.0.0
npm --version   # Should be >= 8.0.0

# Install Expo CLI globally
npm install -g @expo/cli

# Install EAS CLI
npm install -g eas-cli
```

### Project Setup
```bash
# Create new Expo project
npx create-expo-app@latest my-app --template blank

# Navigate to project
cd my-app

# Install dependencies
npm install
```

## Basic Usage

### 1. Initialize Project

```python
from expo_managed_workflow import ExpoManagedWorkflow

# Initialize workflow
workflow = ExpoManagedWorkflow("./my-app")

# Create new project
workflow.initialize_project("my-app", "blank")
```

### 2. Install Dependencies

```python
# Install core dependencies
dependencies = [
    "expo",
    "react-native",
    "expo-dev-client",
    "expo-updates",
    "expo-notifications"
]

workflow.install_dependencies(dependencies)
```

### 3. Start Development

```python
# Start development server
workflow.start_development_server(8081)

# Build development build
workflow.build_development_build("ios")
workflow.build_development_build("android")
```

## Advanced Usage

### 1. Development Workflow

```python
from expo_managed_workflow import ExpoDevelopmentWorkflow

# Initialize development workflow
dev_workflow = ExpoDevelopmentWorkflow("./my-app")

# Setup complete development environment
dev_workflow.setup_development_environment()

# Start development
dev_workflow.start_development(8081)

# Build and test
dev_workflow.build_and_test("ios")
```

### 2. Deployment Workflow

```python
from expo_managed_workflow import ExpoDeploymentWorkflow

# Initialize deployment workflow
deploy_workflow = ExpoDeploymentWorkflow("./my-app")

# Prepare production build
deploy_workflow.prepare_production_build("ios")

# Deploy to app store
deploy_workflow.deploy_to_store("ios")

# Publish over-the-air update
deploy_workflow.publish_update("Bug fixes and improvements")
```

### 3. Configuration Management

```python
# Load current configuration
config = workflow.config
print(f"App name: {config.name}")
print(f"Version: {config.version}")
print(f"Platforms: {config.platform}")

# Update configuration
config_data = workflow._load_app_json()
config_data['expo']['version'] = '1.1.0'
workflow._save_app_json(config_data)
```

## Configuration Files

### 1. app.json
```json
{
  "expo": {
    "name": "MyApp",
    "slug": "my-app",
    "version": "1.0.0",
    "platforms": ["ios", "android"],
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "updates": {
      "enabled": true,
      "fallbackToCacheTimeout": 0,
      "url": "https://u.expo.dev/your-project-id"
    },
    "runtimeVersion": "1.0.0",
    "jsEngine": "hermes",
    "notification": {
      "icon": "./assets/notification-icon.png",
      "color": "#000000",
      "iosDisplayInForeground": true
    }
  }
}
```

### 2. eas.json
```json
{
  "cli": {
    "version": ">= 3.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "resourceClass": "m-medium"
      },
      "android": {
        "buildType": "apk"
      }
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "resourceClass": "m-medium"
      },
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "ios": {
        "resourceClass": "m-medium"
      },
      "android": {
        "buildType": "app-bundle"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@example.com",
        "ascAppId": "your-app-store-connect-app-id",
        "appleTeamId": "your-apple-team-id"
      },
      "android": {
        "serviceAccountKeyPath": "./path/to/service-account.json",
        "track": "production"
      }
    }
  }
}
```

### 3. package.json
```json
{
  "name": "my-app",
  "version": "1.0.0",
  "main": "expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "test": "jest",
    "build:ios": "eas build --platform ios",
    "build:android": "eas build --platform android",
    "submit:ios": "eas submit --platform ios",
    "submit:android": "eas submit --platform android"
  },
  "dependencies": {
    "expo": "~49.0.0",
    "expo-status-bar": "~1.6.0",
    "react": "18.2.0",
    "react-native": "0.72.0",
    "expo-dev-client": "~2.4.0",
    "expo-updates": "~0.18.0",
    "expo-notifications": "~0.20.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.14",
    "@types/react-native": "~0.72.0",
    "jest": "^29.2.1",
    "typescript": "^5.1.3"
  }
}
```

## Development Workflow

### 1. Local Development
```bash
# Start development server
npx expo start

# Start with specific port
npx expo start --port 8081

# Start with tunnel
npx expo start --tunnel

# Start for specific platform
npx expo start --ios
npx expo start --android
```

### 2. Development Builds
```bash
# Build for iOS
npx expo run:ios

# Build for Android
npx expo run:android

# Build with specific device
npx expo run:ios --device "iPhone 14"
```

### 3. Testing
```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## Deployment Workflow

### 1. EAS Build Configuration
```bash
# Initialize EAS
npx eas init

# Configure build profiles
npx eas build:configure
```

### 2. Building for Production
```bash
# Build for iOS
npx eas build --platform ios --profile production

# Build for Android
npx eas build --platform android --profile production

# Build for both platforms
npx eas build --platform all --profile production
```

### 3. Submitting to App Stores
```bash
# Submit to iOS App Store
npx eas submit --platform ios --profile production

# Submit to Google Play Store
npx eas submit --platform android --profile production

# Submit to both stores
npx eas submit --platform all --profile production
```

### 4. Over-the-Air Updates
```bash
# Publish update
npx expo publish --message "Bug fixes and improvements"

# Publish to specific channel
npx expo publish --release-channel production
```

## Service Integration

### 1. Push Notifications
```python
# Configure notifications
workflow.configure_notifications()

# In your React Native app
import * as Notifications from 'expo-notifications';

// Request permissions
const { status } = await Notifications.requestPermissionsAsync();

// Schedule notification
await Notifications.scheduleNotificationAsync({
  content: {
    title: "Hello!",
    body: "This is a notification",
  },
  trigger: { seconds: 2 },
});
```

### 2. Analytics
```python
# Configure analytics
workflow.configure_analytics()

# In your React Native app
import { Analytics } from 'expo-analytics';

// Track events
Analytics.track('button_pressed', {
  button_name: 'submit',
  screen: 'home'
});
```

### 3. Updates
```python
# Configure updates
workflow.configure_updates("production")

# In your React Native app
import * as Updates from 'expo-updates';

// Check for updates
const update = await Updates.checkForUpdateAsync();
if (update.isAvailable) {
  await Updates.fetchUpdateAsync();
  await Updates.reloadAsync();
}
```

## Best Practices

### 1. Project Structure
```
my-app/
├── app.json              # Expo configuration
├── eas.json              # EAS build configuration
├── package.json          # Dependencies
├── App.js               # Main app component
├── assets/              # Static assets
│   ├── icon.png
│   ├── splash.png
│   └── notification-icon.png
├── src/                 # Source code
│   ├── components/
│   ├── screens/
│   ├── navigation/
│   └── utils/
├── __tests__/           # Test files
└── docs/               # Documentation
```

### 2. Environment Configuration
```python
# Environment-specific configuration
import os

class EnvironmentConfig:
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.api_url = os.getenv("API_URL", "https://api.example.com")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def get_config(self):
        if self.environment == "production":
            return {
                "updates": {"enabled": True},
                "analytics": {"enabled": True},
                "notifications": {"enabled": True}
            }
        else:
            return {
                "updates": {"enabled": False},
                "analytics": {"enabled": False},
                "notifications": {"enabled": False}
            }
```

### 3. Error Handling
```python
# Comprehensive error handling
import logging

logger = logging.getLogger(__name__)

def safe_expo_operation(operation_name: str, operation_func):
    """Safely execute Expo operations with error handling."""
    try:
        return operation_func()
    except subprocess.CalledProcessError as e:
        logger.error(f"Expo operation '{operation_name}' failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in '{operation_name}': {e}")
        return False

# Usage
result = safe_expo_operation("build", lambda: workflow.build_development_build("ios"))
```

### 4. Performance Optimization
```python
# Performance monitoring
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.start_memory = None
    
    def start_operation(self):
        self.start_time = time.time()
        self.start_memory = psutil.virtual_memory().used
    
    def end_operation(self, operation_name: str):
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        duration = end_time - self.start_time
        memory_used = end_memory - self.start_memory
        
        logger.info(f"{operation_name} completed in {duration:.2f}s, memory: {memory_used} bytes")
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Clear cache
   npx expo start --clear
   
   # Reset Metro cache
   npx expo start --reset-cache
   
   # Clean and rebuild
   npx expo run:ios --clear
   ```

2. **Dependency Issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   
   # Remove node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **EAS Build Issues**
   ```bash
   # Check EAS status
   npx eas build:list
   
   # View build logs
   npx eas build:view
   
   # Cancel build
   npx eas build:cancel
   ```

### Debug Tools
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check system requirements
def check_system_requirements():
    """Check if system meets requirements."""
    import subprocess
    
    try:
        # Check Node.js version
        node_version = subprocess.check_output(['node', '--version']).decode().strip()
        print(f"Node.js version: {node_version}")
        
        # Check npm version
        npm_version = subprocess.check_output(['npm', '--version']).decode().strip()
        print(f"npm version: {npm_version}")
        
        # Check Expo CLI version
        expo_version = subprocess.check_output(['npx', 'expo', '--version']).decode().strip()
        print(f"Expo CLI version: {expo_version}")
        
        return True
    except Exception as e:
        print(f"System check failed: {e}")
        return False
```

## Security Considerations

### 1. Environment Variables
```bash
# Use .env files for sensitive data
EXPO_PUBLIC_API_URL=https://api.example.com
EXPO_PUBLIC_ANALYTICS_KEY=your-analytics-key
```

### 2. App Signing
```python
# Secure app signing configuration
def configure_app_signing():
    """Configure secure app signing."""
    eas_config = {
        "build": {
            "production": {
                "ios": {
                    "credentialsSource": "remote"
                },
                "android": {
                    "credentialsSource": "remote"
                }
            }
        }
    }
    
    with open("eas.json", "w") as f:
        json.dump(eas_config, f, indent=2)
```

### 3. Update Security
```python
# Secure update configuration
def configure_secure_updates():
    """Configure secure over-the-air updates."""
    config_data = workflow._load_app_json()
    
    config_data['expo']['updates'] = {
        "enabled": True,
        "fallbackToCacheTimeout": 0,
        "url": "https://u.expo.dev/your-project-id",
        "codeSigningCertificate": "./code-signing/certificate.pem",
        "codeSigningMetadata": {
            "keyid": "main",
            "alg": "rsa-v1_5-sha256"
        }
    }
    
    workflow._save_app_json(config_data)
```

## Future Enhancements

### Planned Features
- **Automated Testing**: CI/CD integration with automated testing
- **Performance Monitoring**: Real-time performance metrics
- **Advanced Analytics**: User behavior and crash reporting
- **Multi-Platform Support**: Web and desktop support

### Integration Opportunities
- **Firebase Integration**: Analytics, crash reporting, and messaging
- **AWS Integration**: Cloud storage and backend services
- **GitHub Actions**: Automated deployment pipelines
- **Slack Integration**: Build notifications and alerts

This Expo Managed Workflow system provides a comprehensive solution for streamlined React Native development and deployment, ensuring efficient project management from development to production. 