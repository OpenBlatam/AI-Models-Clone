import * as Haptics from "expo-haptics";

/**
 * Haptic feedback utilities
 */
export const haptics = {
    /**
     * Light impact - for button presses
     */
    light: () => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light),

    /**
     * Medium impact - for selections
     */
    medium: () => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium),

    /**
     * Heavy impact - for significant actions
     */
    heavy: () => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy),

    /**
     * Success notification
     */
    success: () => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success),

    /**
     * Warning notification
     */
    warning: () => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning),

    /**
     * Error notification
     */
    error: () => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error),

    /**
     * Selection changed
     */
    selection: () => Haptics.selectionAsync(),
};
