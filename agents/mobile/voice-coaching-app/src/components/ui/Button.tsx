import React from "react";
import { TouchableOpacity, Text, TouchableOpacityProps, ActivityIndicator, View } from "react-native";
/// <reference types="nativewind/types" />
import { clsx } from "clsx";
import { haptics } from "../../utils/haptics";

interface ButtonProps extends TouchableOpacityProps {
    title: string;
    variant?: "primary" | "secondary" | "outline" | "ghost";
    size?: "sm" | "md" | "lg";
    loading?: boolean;
    icon?: React.ReactNode;
    iconPosition?: "left" | "right";
    hapticFeedback?: boolean;
    className?: string;
}

const variants = {
    primary: "bg-primary",
    secondary: "bg-secondary",
    outline: "border-2 border-primary bg-transparent",
    ghost: "bg-transparent",
};

const sizes = {
    sm: "py-2 px-4",
    md: "py-3 px-6",
    lg: "py-4 px-8",
};

const textVariants = {
    primary: "text-white",
    secondary: "text-white",
    outline: "text-primary",
    ghost: "text-text-secondary",
};

const textSizes = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg",
};

export function Button({
    title,
    variant = "primary",
    size = "md",
    loading = false,
    icon,
    iconPosition = "left",
    hapticFeedback = true,
    disabled,
    onPress,
    className = "",
    ...props
}: ButtonProps) {
    const handlePress = async (event: any) => {
        if (hapticFeedback && !disabled && !loading) {
            await haptics.light();
        }
        onPress?.(event);
    };

    return (
        <TouchableOpacity
            {...props}
            onPress={handlePress}
            disabled={disabled || loading}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel={title}
            className={clsx(
                "rounded-xl items-center justify-center flex-row",
                variants[variant],
                sizes[size],
                disabled && "opacity-50",
                className
            )}
        >
            {loading ? (
                <ActivityIndicator color="#fff" />
            ) : (
                <View className="flex-row items-center space-x-2">
                    {icon && iconPosition === "left" && icon}
                    <Text
                        className={clsx(
                            "font-semibold",
                            textVariants[variant],
                            textSizes[size]
                        )}
                    >
                        {title}
                    </Text>
                    {icon && iconPosition === "right" && icon}
                </View>
            )}
        </TouchableOpacity>
    );
}
