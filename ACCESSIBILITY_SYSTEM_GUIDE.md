# Accessibility System Guide

## Overview

The Accessibility System provides comprehensive support for text scaling, font adjustments, and accessibility features in React Native applications. It ensures your app is accessible to users with different abilities and preferences.

## Key Features

### 1. Text Scaling and Font Adjustments
- **Dynamic Font Scaling**: Automatically adjusts font sizes based on user's system preferences
- **Font Weight Management**: Handles bold text preferences
- **Minimum/Maximum Font Size Limits**: Prevents text from becoming too small or too large
- **Platform-Specific Support**: Optimized for iOS and Android

### 2. Accessibility Components
- **AccessibleText**: Enhanced Text component with built-in accessibility features
- **AccessibleButton**: Touchable button with proper accessibility labels and states
- **AccessibleView**: Container component with accessibility support

### 3. Accessibility Utilities
- **Contrast Ratio Calculation**: WCAG-compliant contrast checking
- **Color Accessibility**: Automatic accessible color selection
- **Touch Target Sizing**: Ensures minimum 44pt touch targets

### 4. System Integration
- **Screen Reader Support**: VoiceOver (iOS) and TalkBack (Android)
- **Reduce Motion**: Respects user's motion preferences
- **High Contrast Mode**: Supports high contrast display settings

## Installation

```bash
# Install dependencies
npm install react-native-accessibility expo-font @expo-google-fonts/inter

# For testing
npm install @testing-library/react-native @testing-library/jest-native
```

## Basic Usage

### 1. Initialize Accessibility Manager

```javascript
import { AccessibilityManager } from './accessibility_system';

const accessibilityManager = new AccessibilityManager();
accessibilityManager.initialize_accessibility();
```

### 2. Use Accessible Components

```javascript
import { AccessibleText, AccessibleButton, AccessibleView } from './accessibility_system';

// Accessible Text Component
<AccessibleText
  style={{ fontSize: 16 }}
  accessibilityLabel="Important information"
  accessibilityHint="This text contains important details"
>
  This text will scale with user preferences
</AccessibleText>

// Accessible Button Component
<AccessibleButton
  title="Submit"
  onPress={handleSubmit}
  accessibilityLabel="Submit form"
  accessibilityHint="Double tap to submit the form"
/>

// Accessible View Component
<AccessibleView
  accessibilityLabel="Blog post container"
  accessibilityRole="article"
>
  <AccessibleText>Blog content here</AccessibleText>
</AccessibleView>
```

### 3. Use Accessibility Hooks

```javascript
import { useAccessibility, useScaledFontSize } from './accessibility_system';

function MyComponent() {
  const { 
    fontScale, 
    isBoldTextEnabled, 
    isReduceMotionEnabled, 
    isScreenReaderEnabled 
  } = useAccessibility();
  
  const scaledFontSize = useScaledFontSize(16);
  
  return (
    <Text style={{ fontSize: scaledFontSize }}>
      Adaptive text size
    </Text>
  );
}
```

## Advanced Usage

### 1. Custom Accessibility Components

```javascript
class CustomAccessibleComponent extends React.Component {
  constructor(props) {
    super(props);
    this.accessibilityManager = new AccessibilityManager();
  }
  
  render() {
    const { title, content, onPress } = this.props;
    
    return (
      <AccessibleView
        style={accessibility_styles.container}
        accessibilityLabel={`${title} card`}
        accessibilityHint="Double tap to open details"
      >
        <AccessibleText
          style={[accessibility_styles.typography.title2, accessibility_styles.title]}
          accessibilityRole="header"
        >
          {title}
        </AccessibleText>
        
        <AccessibleText
          style={[accessibility_styles.typography.body, accessibility_styles.content]}
          numberOfLines={this.accessibilityManager.is_screen_reader_active() ? undefined : 3}
        >
          {content}
        </AccessibleText>
        
        <AccessibleButton
          title="Read More"
          onPress={onPress}
          style={accessibility_styles.button}
        />
      </AccessibleView>
    );
  }
}
```

### 2. Color Accessibility

```javascript
import { AccessibilityUtils } from './accessibility_system';

// Check contrast ratio
const contrastRatio = AccessibilityUtils.get_contrast_ratio('#000000', '#ffffff');
const isAccessible = AccessibilityUtils.is_high_contrast('#000000', '#ffffff');

// Get accessible text color for background
const textColor = AccessibilityUtils.get_accessible_text_color('#808080');
```

### 3. Dynamic Style Adjustments

```javascript
function AdaptiveComponent() {
  const { isBoldTextEnabled, isReduceMotionEnabled } = useAccessibility();
  
  const adaptiveStyle = {
    fontWeight: isBoldTextEnabled ? 'bold' : 'normal',
    transform: isReduceMotionEnabled ? [] : [{ scale: 1.1 }],
  };
  
  return (
    <Animated.View style={[baseStyle, adaptiveStyle]}>
      <AccessibleText>Adaptive content</AccessibleText>
    </Animated.View>
  );
}
```

## Configuration

### 1. Accessibility Styles

```javascript
import { accessibility_styles } from './accessibility_system';

// Use predefined styles
const styles = {
  container: {
    ...accessibility_styles.touch_target,
    padding: accessibility_styles.spacing.md,
    borderRadius: accessibility_styles.borderRadius.md,
  },
  title: {
    ...accessibility_styles.typography.title1,
    color: accessibility_styles.colors.text,
  },
  button: {
    ...accessibility_styles.touch_target,
    backgroundColor: accessibility_styles.colors.primary,
  },
};
```

### 2. Accessibility Configuration

```javascript
import { accessibility_config } from './accessibility_system';

// Customize accessibility settings
const customConfig = {
  ...accessibility_config,
  maxFontSizeMultiplier: 2.5, // Allow larger text scaling
  minTouchTargetSize: 48, // Larger touch targets
};
```

## Testing

### 1. Unit Tests

```javascript
import { render, screen } from '@testing-library/react-native';
import { AccessibleText, AccessibleButton } from './accessibility_system';

describe('AccessibleText', () => {
  it('should render with accessibility props', () => {
    const { getByText } = render(
      <AccessibleText
        accessibilityLabel="Test label"
        accessibilityHint="Test hint"
      >
        Test content
      </AccessibleText>
    );
    
    const textElement = getByText('Test content');
    expect(textElement.props.accessibilityLabel).toBe('Test label');
    expect(textElement.props.accessibilityHint).toBe('Test hint');
  });
});
```

### 2. Integration Tests

```javascript
describe('Accessibility Integration', () => {
  it('should handle screen reader mode', () => {
    const mockPost = {
      id: 1,
      title: 'Test Post',
      content: 'Test content'
    };
    
    const { getByLabelText } = render(
      <AccessibleBlogPost post={mockPost} navigation={{ navigate: jest.fn() }} />
    );
    
    const labeledElement = getByLabelText('Blog post titled Test Post');
    expect(labeledElement).toBeTruthy();
  });
});
```

### 3. Performance Tests

```javascript
describe('Accessibility Performance', () => {
  it('should scale fonts efficiently', () => {
    const manager = new AccessibilityManager();
    const startTime = Date.now();
    
    for (let i = 0; i < 1000; i++) {
      manager.get_scaled_font_size(16);
    }
    
    const endTime = Date.now();
    expect(endTime - startTime).toBeLessThan(100); // Should complete in < 100ms
  });
});
```

## Best Practices

### 1. Text Scaling
- Always use `AccessibleText` component for text content
- Set reasonable `maxFontSizeMultiplier` (2.0-3.0)
- Test with different font scale settings
- Ensure text remains readable at all sizes

### 2. Touch Targets
- Use minimum 44pt touch targets
- Apply `accessibility_styles.touch_target` to interactive elements
- Test touch targets on different screen sizes

### 3. Color and Contrast
- Use `AccessibilityUtils` to check contrast ratios
- Support high contrast mode
- Don't rely solely on color to convey information

### 4. Screen Reader Support
- Provide meaningful `accessibilityLabel` for all interactive elements
- Use `accessibilityHint` for complex interactions
- Test with VoiceOver (iOS) and TalkBack (Android)

### 5. Motion and Animation
- Respect `isReduceMotionEnabled` preference
- Provide alternative interactions for motion-sensitive users
- Use subtle animations that don't cause discomfort

## Platform-Specific Considerations

### iOS
- Support Dynamic Type
- Use system fonts when possible
- Implement VoiceOver gestures
- Support Switch Control

### Android
- Support large text mode
- Use Material Design touch targets
- Implement TalkBack navigation
- Support Switch Access

## Troubleshooting

### Common Issues

1. **Text not scaling properly**
   - Ensure `allowFontScaling={true}` is set
   - Check `maxFontSizeMultiplier` value
   - Verify font family supports scaling

2. **Touch targets too small**
   - Apply `accessibility_styles.touch_target`
   - Check minimum 44pt requirement
   - Test on different screen densities

3. **Poor contrast ratios**
   - Use `AccessibilityUtils.get_contrast_ratio()`
   - Test with high contrast mode
   - Ensure WCAG AA compliance (4.5:1 ratio)

4. **Screen reader issues**
   - Provide unique `accessibilityLabel`
   - Test navigation flow with screen reader
   - Ensure proper `accessibilityRole` values

### Debug Tools

```javascript
// Enable accessibility debugging
import { AccessibilityInfo } from 'react-native';

AccessibilityInfo.addEventListener('screenReaderChanged', (isEnabled) => {
  console.log('Screen reader enabled:', isEnabled);
});

// Check current accessibility settings
AccessibilityInfo.isBoldTextEnabled().then(console.log);
AccessibilityInfo.isReduceMotionEnabled().then(console.log);
AccessibilityInfo.isScreenReaderEnabled().then(console.log);
```

## Performance Optimization

### 1. Font Scaling
- Cache scaled font sizes
- Use `useScaledFontSize` hook for reactive updates
- Avoid recalculating font sizes in render

### 2. Contrast Calculation
- Memoize contrast calculations
- Use lookup tables for common color combinations
- Batch contrast checks when possible

### 3. Component Rendering
- Use `React.memo` for accessibility components
- Avoid unnecessary re-renders
- Optimize style calculations

## Security Considerations

### 1. Input Validation
- Validate all accessibility props
- Sanitize user-provided labels and hints
- Prevent XSS in accessibility content

### 2. Data Privacy
- Don't expose sensitive information in accessibility labels
- Use generic descriptions for private content
- Respect user privacy preferences

## Future Enhancements

### 1. Planned Features
- AI-powered accessibility suggestions
- Automated accessibility testing
- Advanced gesture recognition
- Voice command integration

### 2. Accessibility Standards
- WCAG 2.1 AA compliance
- Section 508 compliance
- EN 301 549 compliance
- Custom accessibility guidelines

## Support and Resources

### Documentation
- [React Native Accessibility](https://reactnative.dev/docs/accessibility)
- [iOS Accessibility](https://developer.apple.com/accessibility/)
- [Android Accessibility](https://developer.android.com/guide/topics/ui/accessibility)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Testing Tools
- [React Native Testing Library](https://callstack.github.io/react-native-testing-library/)
- [Accessibility Inspector (iOS)](https://developer.apple.com/xcode/)
- [Accessibility Scanner (Android)](https://play.google.com/store/apps/details?id=com.google.android.apps.accessibility.auditor)

### Community
- React Native Accessibility Working Group
- iOS Accessibility Developers
- Android Accessibility Community
- Web Accessibility Initiative (WAI)

This accessibility system ensures your React Native app is inclusive and accessible to all users, providing a better experience for everyone regardless of their abilities or preferences. 