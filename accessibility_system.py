import React from 'react';
import { 
  Text, 
  View, 
  TouchableOpacity, 
  ScrollView, 
  AccessibilityInfo,
  Platform,
  Dimensions,
  PixelRatio
} from 'react-native';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';

# Accessibility System for React Native
# Comprehensive text scaling, font adjustments, and accessibility features

class AccessibilityManager:
    def __init__(self):
        self.font_scale = 1.0
        self.is_bold_text_enabled = False
        self.is_reduce_motion_enabled = False
        self.is_screen_reader_enabled = False
        self.color_scheme = 'light'
        
    def initialize_accessibility(self):
        """Initialize accessibility settings and listeners"""
        if not self._validate_platform():
            return False
            
        self._setup_accessibility_listeners()
        self._load_user_preferences()
        return True
    
    def _validate_platform(self):
        """Validate platform support"""
        if Platform.OS not in ['ios', 'android']:
            print("Accessibility not supported on this platform")
            return False
        return True
    
    def _setup_accessibility_listeners(self):
        """Setup accessibility change listeners"""
        AccessibilityInfo.addEventListener(
            'boldTextChanged',
            self._handle_bold_text_changed
        )
        AccessibilityInfo.addEventListener(
            'reduceMotionChanged',
            self._handle_reduce_motion_changed
        )
        AccessibilityInfo.addEventListener(
            'screenReaderChanged',
            self._handle_screen_reader_changed
        )
    
    def _handle_bold_text_changed(self, is_bold_text_enabled):
        """Handle bold text preference changes"""
        self.is_bold_text_enabled = is_bold_text_enabled
        self._update_font_weights()
    
    def _handle_reduce_motion_changed(self, is_reduce_motion_enabled):
        """Handle reduce motion preference changes"""
        self.is_reduce_motion_enabled = is_reduce_motion_enabled
        self._update_animations()
    
    def _handle_screen_reader_changed(self, is_screen_reader_enabled):
        """Handle screen reader preference changes"""
        self.is_screen_reader_enabled = is_screen_reader_enabled
        self._update_accessibility_labels()
    
    def get_scaled_font_size(self, base_size: float) -> float:
        """Get font size adjusted for user's text scaling preference"""
        if not self._validate_font_size(base_size):
            return base_size
            
        scaled_size = base_size * self.font_scale
        return self._clamp_font_size(scaled_size)
    
    def _validate_font_size(self, size: float) -> bool:
        """Validate font size input"""
        if not isinstance(size, (int, float)):
            return False
        if size <= 0:
            return False
        return True
    
    def _clamp_font_size(self, size: float) -> float:
        """Clamp font size to reasonable bounds"""
        min_size = 8.0
        max_size = 72.0
        return max(min_size, min(size, max_size))
    
    def get_font_weight(self, base_weight: str = 'normal') -> str:
        """Get font weight adjusted for user's bold text preference"""
        if self.is_bold_text_enabled:
            return self._get_bold_weight(base_weight)
        return base_weight
    
    def _get_bold_weight(self, base_weight: str) -> str:
        """Convert base weight to bold weight"""
        weight_mapping = {
            'normal': 'bold',
            '300': '600',
            '400': '600',
            '500': '700',
            '600': '700',
            '700': '800',
            '800': '900',
            '900': '900'
        }
        return weight_mapping.get(base_weight, 'bold')
    
    def should_reduce_motion(self) -> bool:
        """Check if motion should be reduced"""
        return self.is_reduce_motion_enabled
    
    def is_screen_reader_active(self) -> bool:
        """Check if screen reader is active"""
        return self.is_screen_reader_enabled

# Accessibility Components

class AccessibleText(React.Component):
    def __init__(self, props):
        super().__init__(props)
        self.accessibility_manager = AccessibilityManager()
    
    def render(self):
        const { 
            children, 
            style, 
            accessibilityLabel, 
            accessibilityHint,
            accessibilityRole = 'text',
            ...props 
        } = this.props
        
        const scaled_style = this._get_scaled_style(style)
        
        return (
            <Text
                style={scaled_style}
                accessibilityLabel={accessibilityLabel}
                accessibilityHint={accessibilityHint}
                accessibilityRole={accessibilityRole}
                allowFontScaling={true}
                maxFontSizeMultiplier={2.0}
                {...props}
            >
                {children}
            </Text>
        )
    
    def _get_scaled_style(self, style):
        """Get style with accessibility adjustments"""
        if not style:
            return {}
            
        const base_font_size = style.fontSize || 16
        const scaled_font_size = this.accessibility_manager.get_scaled_font_size(base_font_size)
        const font_weight = this.accessibility_manager.get_font_weight(style.fontWeight)
        
        return {
            ...style,
            fontSize: scaled_font_size,
            fontWeight: font_weight,
        }

class AccessibleButton(React.Component):
    def __init__(self, props):
        super().__init__(props)
        self.accessibility_manager = AccessibilityManager()
    
    def render(self):
        const { 
            title, 
            onPress, 
            style, 
            disabled = false,
            accessibilityLabel,
            accessibilityHint,
            ...props 
        } = this.props
        
        const button_style = this._get_button_style(style, disabled)
        const label = accessibilityLabel || title
        
        return (
            <TouchableOpacity
                style={button_style}
                onPress={onPress}
                disabled={disabled}
                accessibilityLabel={label}
                accessibilityHint={accessibilityHint}
                accessibilityRole="button"
                accessibilityState={{ disabled }}
                activeOpacity={0.7}
                {...props}
            >
                <AccessibleText style={button_style.text}>
                    {title}
                </AccessibleText>
            </TouchableOpacity>
        )
    
    def _get_button_style(self, style, disabled):
        """Get button style with accessibility adjustments"""
        const base_style = {
            padding: 12,
            borderRadius: 8,
            backgroundColor: disabled ? '#cccccc' : '#007AFF',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 44, // Minimum touch target size
            ...style
        }
        
        const text_style = {
            color: disabled ? '#666666' : '#ffffff',
            fontSize: this.accessibility_manager.get_scaled_font_size(16),
            fontWeight: this.accessibility_manager.get_font_weight('600'),
            textAlign: 'center',
        }
        
        return {
            ...base_style,
            text: text_style
        }

class AccessibleView(React.Component):
    def __init__(self, props):
        super().__init__(props)
        self.accessibility_manager = AccessibilityManager()
    
    def render(self):
        const { 
            children, 
            style, 
            accessibilityLabel,
            accessibilityHint,
            accessibilityRole = 'none',
            ...props 
        } = this.props
        
        return (
            <View
                style={style}
                accessibilityLabel={accessibilityLabel}
                accessibilityHint={accessibilityHint}
                accessibilityRole={accessibilityRole}
                {...props}
            >
                {children}
            </View>
        )

# Accessibility Hooks

def useAccessibility():
    """Custom hook for accessibility features"""
    const [fontScale, setFontScale] = React.useState(1.0)
    const [isBoldTextEnabled, setIsBoldTextEnabled] = React.useState(False)
    const [isReduceMotionEnabled, setIsReduceMotionEnabled] = React.useState(False)
    const [isScreenReaderEnabled, setIsScreenReaderEnabled] = React.useState(False)
    
    React.useEffect(() => {
        const accessibility_manager = AccessibilityManager()
        
        # Get initial values
        accessibility_manager._get_font_scale().then(setFontScale)
        accessibility_manager._is_bold_text_enabled().then(setIsBoldTextEnabled)
        accessibility_manager._is_reduce_motion_enabled().then(setIsReduceMotionEnabled)
        accessibility_manager._is_screen_reader_enabled().then(setIsScreenReaderEnabled)
        
        # Setup listeners
        const bold_text_listener = AccessibilityInfo.addEventListener(
            'boldTextChanged',
            setIsBoldTextEnabled
        )
        
        const reduce_motion_listener = AccessibilityInfo.addEventListener(
            'reduceMotionChanged',
            setIsReduceMotionEnabled
        )
        
        const screen_reader_listener = AccessibilityInfo.addEventListener(
            'screenReaderChanged',
            setIsScreenReaderEnabled
        )
        
        return () => {
            bold_text_listener?.remove()
            reduce_motion_listener?.remove()
            screen_reader_listener?.remove()
        }
    }, [])
    
    return {
        fontScale,
        isBoldTextEnabled,
        isReduceMotionEnabled,
        isScreenReaderEnabled,
    }

def useScaledFontSize(baseSize: float) -> float:
    """Hook for scaled font size"""
    const { fontScale } = useAccessibility()
    const accessibility_manager = AccessibilityManager()
    return accessibility_manager.get_scaled_font_size(baseSize * fontScale)

# Accessibility Utilities

class AccessibilityUtils:
    @staticmethod
    def get_contrast_ratio(color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors"""
        if not color1 or not color2:
            return 0.0
            
        const luminance1 = AccessibilityUtils._get_luminance(color1)
        const luminance2 = AccessibilityUtils._get_luminance(color2)
        
        const lighter = max(luminance1, luminance2)
        const darker = min(luminance1, luminance2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def _get_luminance(color: str) -> float:
        """Calculate relative luminance of a color"""
        const rgb = AccessibilityUtils._hex_to_rgb(color)
        if not rgb:
            return 0.0
            
        const [r, g, b] = rgb.map(c => c / 255)
        
        const rs = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4)
        const gs = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4)
        const bs = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4)
        
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
    
    @staticmethod
    def _hex_to_rgb(hex: str) -> list:
        """Convert hex color to RGB values"""
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
        if not result:
            return None
        return [
            parseInt(result[1], 16),
            parseInt(result[2], 16),
            parseInt(result[3], 16)
        ]
    
    @staticmethod
    def is_high_contrast(color1: str, color2: str) -> bool:
        """Check if contrast ratio meets WCAG AA standards"""
        const ratio = AccessibilityUtils.get_contrast_ratio(color1, color2)
        return ratio >= 4.5  # WCAG AA standard for normal text
    
    @staticmethod
    def get_accessible_text_color(background_color: str) -> str:
        """Get accessible text color for given background"""
        const white_contrast = AccessibilityUtils.get_contrast_ratio(background_color, '#ffffff')
        const black_contrast = AccessibilityUtils.get_contrast_ratio(background_color, '#000000')
        
        return '#ffffff' if white_contrast > black_contrast else '#000000'

# Accessibility Styles

const accessibility_styles = {
    // Minimum touch target sizes
    touch_target: {
        minHeight: 44,
        minWidth: 44,
    },
    
    // High contrast colors
    colors: {
        primary: '#007AFF',
        secondary: '#5856D6',
        success: '#34C759',
        warning: '#FF9500',
        error: '#FF3B30',
        background: '#ffffff',
        surface: '#f2f2f7',
        text: '#000000',
        textSecondary: '#8e8e93',
    },
    
    // Typography with accessibility considerations
    typography: {
        largeTitle: {
            fontSize: 34,
            fontWeight: '700',
            lineHeight: 41,
        },
        title1: {
            fontSize: 28,
            fontWeight: '600',
            lineHeight: 34,
        },
        title2: {
            fontSize: 22,
            fontWeight: '600',
            lineHeight: 28,
        },
        title3: {
            fontSize: 20,
            fontWeight: '600',
            lineHeight: 24,
        },
        headline: {
            fontSize: 17,
            fontWeight: '600',
            lineHeight: 22,
        },
        body: {
            fontSize: 17,
            fontWeight: '400',
            lineHeight: 22,
        },
        callout: {
            fontSize: 16,
            fontWeight: '400',
            lineHeight: 21,
        },
        subhead: {
            fontSize: 15,
            fontWeight: '400',
            lineHeight: 20,
        },
        footnote: {
            fontSize: 13,
            fontWeight: '400',
            lineHeight: 18,
        },
        caption1: {
            fontSize: 12,
            fontWeight: '400',
            lineHeight: 16,
        },
        caption2: {
            fontSize: 11,
            fontWeight: '400',
            lineHeight: 13,
        },
    },
    
    // Spacing for accessibility
    spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
        xxl: 48,
    },
    
    // Border radius for consistency
    borderRadius: {
        sm: 4,
        md: 8,
        lg: 12,
        xl: 16,
        round: 999,
    },
}

# Example Usage Component

class AccessibleBlogPost(React.Component):
    def __init__(self, props):
        super().__init__(props)
        self.accessibility_manager = AccessibilityManager()
    
    def render(self):
        const { post } = this.props
        const { isScreenReaderEnabled } = useAccessibility()
        
        return (
            <AccessibleView
                style={accessibility_styles.container}
                accessibilityLabel={`Blog post titled ${post.title}`}
                accessibilityHint="Double tap to read the full post"
            >
                <AccessibleText
                    style={[accessibility_styles.typography.title2, accessibility_styles.title]}
                    accessibilityRole="header"
                >
                    {post.title}
                </AccessibleText>
                
                <AccessibleText
                    style={[accessibility_styles.typography.body, accessibility_styles.content]}
                    numberOfLines={isScreenReaderEnabled ? undefined : 3}
                    accessibilityLabel={`Post content: ${post.content}`}
                >
                    {post.content}
                </AccessibleText>
                
                <AccessibleButton
                    title="Read More"
                    onPress={() => this._handle_read_more(post)}
                    style={accessibility_styles.button}
                    accessibilityHint="Opens the full blog post"
                />
            </AccessibleView>
        )
    
    def _handle_read_more(self, post):
        """Handle read more button press"""
        if not post or not post.id:
            return
            
        // Navigate to full post
        this.props.navigation.navigate('BlogPostDetail', { postId: post.id })

# Accessibility Configuration

const accessibility_config = {
    // Enable font scaling
    allowFontScaling: true,
    maxFontSizeMultiplier: 2.0,
    
    // Minimum touch target size
    minTouchTargetSize: 44,
    
    // High contrast mode support
    supportHighContrast: true,
    
    // Screen reader support
    supportScreenReader: true,
    
    // Reduce motion support
    supportReduceMotion: true,
    
    // VoiceOver/TalkBack support
    supportVoiceOver: true,
    
    // Dynamic Type support (iOS)
    supportDynamicType: true,
    
    // Large text support
    supportLargeText: true,
}

# Export components and utilities
export {
    AccessibilityManager,
    AccessibleText,
    AccessibleButton,
    AccessibleView,
    useAccessibility,
    useScaledFontSize,
    AccessibilityUtils,
    accessibility_styles,
    accessibility_config,
    AccessibleBlogPost,
} 