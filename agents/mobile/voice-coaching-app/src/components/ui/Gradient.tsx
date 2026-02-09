import React from "react";
import { View, ViewProps, ColorValue } from "react-native";
/// <reference types="nativewind/types" />
import { LinearGradient } from "expo-linear-gradient";
import { COLORS } from "../../constants";

interface GradientCardProps extends ViewProps {
    children: React.ReactNode;
    colors?: [string, string, ...string[]];
    className?: string;
}

/**
 * Card component with gradient background
 */
export function GradientCard({
    children,
    colors = [COLORS.primary, COLORS.secondary],
    className = "",
    ...props
}: GradientCardProps) {
    return (
        <LinearGradient
            colors={colors as readonly [ColorValue, ColorValue, ...ColorValue[]]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={{ borderRadius: 16 }}
        >
            <View className={`p-4 ${className}`} {...props}>
                {children}
            </View>
        </LinearGradient>
    );
}

interface BackgroundGradientProps {
    children: React.ReactNode;
    colors?: [string, string, ...string[]];
}

/**
 * Full screen gradient background
 */
export function BackgroundGradient({
    children,
    colors = [COLORS.background, "#1a1a2e", COLORS.background],
}: BackgroundGradientProps) {
    return (
        <LinearGradient
            colors={colors as readonly [ColorValue, ColorValue, ...ColorValue[]]}
            style={{ flex: 1 }}
        >
            {children}
        </LinearGradient>
    );
}
