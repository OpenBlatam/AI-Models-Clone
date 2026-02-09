import React from "react";
import { View, ViewProps } from "react-native";
/// <reference types="nativewind/types" />
import { clsx } from "clsx";

interface CardProps extends ViewProps {
    children: React.ReactNode;
    variant?: "default" | "glass";
}

export function Card({ children, className, variant = "default", ...props }: CardProps) {
    const variants = {
        default: "bg-surface border border-white/5",
        glass: "bg-white/5 border border-white/10 backdrop-blur-lg",
    };

    return (
        <View
            className={clsx("rounded-2xl p-4 shadow-sm", variants[variant], className)}
            {...props}
        >
            {children}
        </View>
    );
}
