import React from "react";
import { View, Text } from "react-native";
/// <reference types="nativewind/types" />

interface ProgressBarProps {
    value: number; // 0-100
    label?: string;
    showValue?: boolean;
    color?: string;
}

export function ProgressBar({
    value,
    label,
    showValue = true,
    color = "bg-accent",
}: ProgressBarProps) {
    const clampedValue = Math.min(100, Math.max(0, value));

    return (
        <View className="space-y-2">
            {(label || showValue) && (
                <View className="flex-row justify-between">
                    {label && <Text className="text-text-secondary">{label}</Text>}
                    {showValue && (
                        <Text className="text-white font-medium">{clampedValue}%</Text>
                    )}
                </View>
            )}
            <View className="h-2 bg-surface rounded-full overflow-hidden">
                <View
                    className={`h-full ${color} rounded-full`}
                    style={{ width: `${clampedValue}%` }}
                />
            </View>
        </View>
    );
}
