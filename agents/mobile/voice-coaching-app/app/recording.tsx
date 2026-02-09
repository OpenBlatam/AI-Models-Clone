import { Text, View } from "react-native";
/// <reference types="nativewind/types" />
import { ScreenLayout } from "../src/components/layout/ScreenLayout";
import { Button } from "../src/components/ui/Button";
import { RecordingButton } from "../src/components/ui/RecordingButton";
import { RecordingIndicator } from "../src/components/ui/RecordingIndicator";
import { useRouter } from "expo-router";
import { useRecording } from "../src/hooks/useRecording";
import { haptics } from "../src/utils/haptics";

export default function Recording() {
    const router = useRouter();
    const {
        isRecording,
        isPreparing,
        isAnalyzing,
        recordingTime,
        start,
        stop,
    } = useRecording();

    const handleToggle = async () => {
        if (isRecording) {
            await haptics.success();
            const analysis = await stop();
            if (analysis) {
                router.replace(`/analysis/${analysis.id}`);
            }
        } else {
            await haptics.medium();
            await start();
        }
    };

    const getStatusText = () => {
        if (isPreparing) return "Preparing microphone...";
        if (isAnalyzing) return "🤖 Analyzing your voice...";
        if (isRecording) return "🔴 Recording...";
        return "Tap the button to start";
    };

    return (
        <ScreenLayout>
            <View className="flex-1 justify-between py-8">
                {/* Header */}
                <View className="items-center">
                    <Text className="text-2xl font-bold text-white mb-2">
                        Recording Session
                    </Text>
                    <Text className="text-text-secondary">{getStatusText()}</Text>
                </View>

                {/* Main Recording Button */}
                <View className="flex-1 justify-center items-center">
                    <RecordingButton
                        isRecording={isRecording}
                        recordingTime={recordingTime}
                        onPress={handleToggle}
                        disabled={isPreparing || isAnalyzing}
                    />
                </View>

                {/* Recording Status */}
                <RecordingIndicator
                    isRecording={isRecording}
                    recordingTime={recordingTime}
                />

                {/* Action Buttons */}
                <View className="space-y-4">
                    <Button
                        title={
                            isPreparing
                                ? "Preparing..."
                                : isAnalyzing
                                    ? "Analyzing..."
                                    : isRecording
                                        ? "Stop & Analyze"
                                        : "Start Recording"
                        }
                        variant={isRecording ? "secondary" : "primary"}
                        onPress={handleToggle}
                        loading={isPreparing || isAnalyzing}
                        size="lg"
                    />
                    <Button
                        title="Cancel"
                        variant="ghost"
                        onPress={() => router.back()}
                        disabled={isRecording || isAnalyzing}
                    />
                </View>
            </View>
        </ScreenLayout>
    );
}
