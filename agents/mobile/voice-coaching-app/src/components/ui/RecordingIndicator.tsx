import React from "react";
import { Text, View } from "react-native";
/// <reference types="nativewind/types" />
import { Ionicons } from "@expo/vector-icons";
import { Card } from "./Card";

interface RecordingIndicatorProps {
    isRecording: boolean;
    recordingTime: number;
}

/**
 * Recording status indicator card
 */
export function RecordingIndicator({
    isRecording,
    recordingTime,
}: RecordingIndicatorProps) {
    if (!isRecording) return null;

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    };

    return (
        <Card variant="glass" className="mb-4">
            <View className="flex-row items-center space-x-3">
                <View className="w-3 h-3 rounded-full bg-red-500" />
                <Ionicons name="mic" size={18} color="#EF4444" />
                <Text className="text-white flex-1">Recording in progress</Text>
                <Text className="text-accent font-bold">{formatTime(recordingTime)}</Text>
            </View>
        </Card>
    );
}
