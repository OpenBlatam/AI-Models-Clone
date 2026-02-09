import React from "react";
import { View, Text } from "react-native";
/// <reference types="nativewind/types" />

interface HeaderProps {
    title: string;
    subtitle?: string;
    rightElement?: React.ReactNode;
}

/**
 * Screen header component
 */
export function Header({ title, subtitle, rightElement }: HeaderProps) {
    return (
        <View className="flex-row items-center justify-between mb-6" accessibilityRole="header">
            <View className="flex-1">
                <Text className="text-3xl font-bold text-white">{title}</Text>
                {subtitle && (
                    <Text className="text-text-secondary mt-1">{subtitle}</Text>
                )}
            </View>
            {rightElement && <View>{rightElement}</View>}
        </View>
    );
}
