import React from "react";
import { View, StatusBar, ViewProps } from "react-native";
/// <reference types="nativewind/types" />
import { SafeAreaView } from "react-native-safe-area-context";
import { clsx } from "clsx";

interface ScreenLayoutProps extends ViewProps {
    children: React.ReactNode;
    className?: string;
    safeArea?: boolean;
}

const CHECK_COLOR = "#0F172A"; // Matches tailwind.config.js background color

export function ScreenLayout({ children, className, safeArea = true, ...props }: ScreenLayoutProps) {
    const Container = safeArea ? SafeAreaView : View;

    return (
        <Container className={clsx("flex-1 bg-background", className)} {...props}>
            <StatusBar barStyle="light-content" backgroundColor={CHECK_COLOR} />
            <View className="flex-1 px-4">{children}</View>
        </Container>
    );
}
