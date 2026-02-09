import React from "react";
import { View, ActivityIndicator, Text } from "react-native";
/// <reference types="nativewind/types" />
import { COLORS } from "../../constants";

interface LoadingProps {
    message?: string;
    size?: "small" | "large";
    fullScreen?: boolean;
}

/**
 * Loading indicator component
 */
export function Loading({
    message,
    size = "large",
    fullScreen = false,
}: LoadingProps) {
    const content = (
        <View className="items-center justify-center space-y-4">
            <ActivityIndicator size={size} color={COLORS.primary} />
            {message && (
                <Text className="text-text-secondary text-center">{message}</Text>
            )}
        </View>
    );

    if (fullScreen) {
        return (
            <View className="flex-1 items-center justify-center bg-background">
                {content}
            </View>
        );
    }

    return content;
}

/**
 * Full screen loading overlay
 */
export function LoadingOverlay({ message }: { message?: string }) {
    return (
        <View className="absolute inset-0 bg-background/80 items-center justify-center z-50">
            <View className="bg-surface p-6 rounded-2xl items-center space-y-4">
                <ActivityIndicator size="large" color={COLORS.primary} />
                {message && (
                    <Text className="text-text-secondary">{message}</Text>
                )}
            </View>
        </View>
    );
}
