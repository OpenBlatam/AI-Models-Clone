import React from "react";
import { TouchableOpacity, TouchableOpacityProps } from "react-native";
/// <reference types="nativewind/types" />
import { clsx } from "clsx";
import { Icon } from "./Icon";
import { haptics } from "../../utils/haptics";

interface IconButtonProps extends TouchableOpacityProps {
    icon: string;
    size?: "sm" | "md" | "lg";
    variant?: "primary" | "secondary" | "ghost";
    iconColor?: string;
    hapticFeedback?: boolean;
    className?: string;
}

const sizeMap = {
    sm: { button: "w-10 h-10", icon: 18 },
    md: { button: "w-12 h-12", icon: 24 },
    lg: { button: "w-16 h-16", icon: 32 },
};

const variantMap = {
    primary: "bg-primary",
    secondary: "bg-surface",
    ghost: "bg-transparent",
};

export function IconButton({
    icon,
    size = "md",
    variant = "ghost",
    iconColor = "#fff",
    hapticFeedback = true,
    disabled,
    onPress,
    className = "",
    ...props
}: IconButtonProps) {
    const handlePress = async (event: any) => {
        if (hapticFeedback && !disabled) {
            await haptics.light();
        }
        onPress?.(event);
    };

    return (
        <TouchableOpacity
            {...props}
            onPress={handlePress}
            disabled={disabled}
            activeOpacity={0.7}
            className={clsx(
                "rounded-full items-center justify-center",
                sizeMap[size].button,
                variantMap[variant],
                disabled && "opacity-50",
                className
            )}
        >
            <Icon name={icon} size={sizeMap[size].icon} color={iconColor} />
        </TouchableOpacity>
    );
}
