import React from "react";
import { View, Text } from "react-native";
/// <reference types="nativewind/types" />

interface EmptyStateProps {
    icon: string;
    title: string;
    description?: string;
    children?: React.ReactNode;
}

export function EmptyState({ icon, title, description, children }: EmptyStateProps) {
    return (
        <View className="items-center py-8 px-4">
            <Text className="text-5xl mb-4">{icon}</Text>
            <Text className="text-white text-lg font-medium text-center">{title}</Text>
            {description && (
                <Text className="text-text-secondary text-center mt-2">{description}</Text>
            )}
            {children && <View className="mt-4">{children}</View>}
        </View>
    );
}
