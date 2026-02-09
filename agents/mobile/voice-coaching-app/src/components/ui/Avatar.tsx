import React from "react";
import { View, Text } from "react-native";
/// <reference types="nativewind/types" />

interface AvatarProps {
    name?: string;
    size?: "sm" | "md" | "lg";
}

const sizeClasses = {
    sm: "w-10 h-10",
    md: "w-16 h-16",
    lg: "w-24 h-24",
};

const textSizeClasses = {
    sm: "text-sm",
    md: "text-2xl",
    lg: "text-4xl",
};

export function Avatar({ name = "?", size = "md" }: AvatarProps) {
    const initial = name.charAt(0).toUpperCase();

    return (
        <View
            className={`${sizeClasses[size]} rounded-full bg-primary items-center justify-center`}
        >
            <Text className={`${textSizeClasses[size]} text-white font-bold`}>
                {initial}
            </Text>
        </View>
    );
}
