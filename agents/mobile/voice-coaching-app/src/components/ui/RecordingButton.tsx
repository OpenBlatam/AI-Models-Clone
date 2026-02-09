import React, { useRef, useEffect } from "react";
import { Animated, View, Text, TouchableOpacity } from "react-native";
/// <reference types="nativewind/types" />
import { haptics } from "../../utils/haptics";
import { COLORS } from "../../constants";

interface PulsingCircleProps {
    isActive: boolean;
    size?: number;
    color?: string;
}

/**
 * Animated pulsing circle for recording indicator
 */
export function PulsingCircle({
    isActive,
    size = 256,
    color = COLORS.primary,
}: PulsingCircleProps) {
    const scaleAnim = useRef(new Animated.Value(1)).current;
    const opacityAnim = useRef(new Animated.Value(0.5)).current;

    useEffect(() => {
        if (isActive) {
            Animated.loop(
                Animated.parallel([
                    Animated.sequence([
                        Animated.timing(scaleAnim, {
                            toValue: 1.3,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                        Animated.timing(scaleAnim, {
                            toValue: 1,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                    ]),
                    Animated.sequence([
                        Animated.timing(opacityAnim, {
                            toValue: 0.2,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                        Animated.timing(opacityAnim, {
                            toValue: 0.5,
                            duration: 1000,
                            useNativeDriver: true,
                        }),
                    ]),
                ])
            ).start();
        } else {
            scaleAnim.setValue(1);
            opacityAnim.setValue(0.5);
        }
    }, [isActive, scaleAnim, opacityAnim]);

    return (
        <Animated.View
            style={{
                position: "absolute",
                width: size,
                height: size,
                borderRadius: size / 2,
                backgroundColor: color,
                transform: [{ scale: scaleAnim }],
                opacity: opacityAnim,
            }}
        />
    );
}

interface RecordingButtonProps {
    isRecording: boolean;
    recordingTime: number;
    onPress: () => void;
    disabled?: boolean;
}

/**
 * Large circular recording button
 */
export function RecordingButton({
    isRecording,
    recordingTime,
    onPress,
    disabled = false,
}: RecordingButtonProps) {
    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    };

    const handlePress = async () => {
        await haptics.medium();
        onPress();
    };

    return (
        <View className="relative items-center justify-center">
            <PulsingCircle isActive={isRecording} />
            <TouchableOpacity
                onPress={handlePress}
                disabled={disabled}
                activeOpacity={0.8}
                className={`w-48 h-48 rounded-full items-center justify-center z-10 ${isRecording ? "bg-secondary" : "bg-primary"
                    }`}
            >
                {isRecording ? (
                    <View className="items-center">
                        <Text className="text-5xl">🎙️</Text>
                        <Text className="text-white text-2xl font-bold mt-2">
                            {formatTime(recordingTime)}
                        </Text>
                    </View>
                ) : (
                    <View className="items-center">
                        <Text className="text-5xl">🎤</Text>
                        <Text className="text-white text-lg font-semibold mt-2">
                            Tap to Start
                        </Text>
                    </View>
                )}
            </TouchableOpacity>
        </View>
    );
}
