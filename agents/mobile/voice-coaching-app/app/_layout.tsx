import "../global.css";
import { Stack, useRouter, useSegments } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { useUserStore } from "../src/store/useUserStore";
import { ErrorBoundary } from "../src/components/layout/ErrorBoundary";
import { useEffect } from "react";

/**
 * Root layout component for the Voice Coaching App
 * Handles navigation structure, onboarding check, and error boundary
 */
export default function Layout() {
    const router = useRouter();
    const segments = useSegments();
    const { profile } = useUserStore();

    useEffect(() => {
        const inOnboarding = segments[0] === "onboarding";

        // If no profile and not in onboarding, redirect to onboarding
        if (!profile?.hasCompletedOnboarding && !inOnboarding) {
            router.replace("/onboarding");
        }
    }, [profile, segments, router]);

    return (
        <ErrorBoundary>
            <SafeAreaProvider>
                <StatusBar style="light" />
                <Stack screenOptions={{ headerShown: false }}>
                    <Stack.Screen name="onboarding" options={{ gestureEnabled: false }} />
                    <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                    <Stack.Screen name="recording" options={{ presentation: "modal" }} />
                    <Stack.Screen name="analysis/[id]" />
                    <Stack.Screen name="tips" />
                </Stack>
            </SafeAreaProvider>
        </ErrorBoundary>
    );
}
