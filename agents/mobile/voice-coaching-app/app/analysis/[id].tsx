import { Text, View, ScrollView } from "react-native";
/// <reference types="nativewind/types" />
import { useLocalSearchParams, useRouter } from "expo-router";
import { ScreenLayout } from "../../src/components/layout/ScreenLayout";
import { Card } from "../../src/components/ui/Card";
import { Button } from "../../src/components/ui/Button";
import { ProgressBar } from "../../src/components/ui/ProgressBar";
import { Header } from "../../src/components/ui/Header";
import { IconButton } from "../../src/components/ui/IconButton";
import { useVoiceStore } from "../../src/store/useVoiceStore";
import { getScoreGrade, generateMetrics, formatDuration } from "../../src/utils";

export default function AnalysisResult() {
    const { id } = useLocalSearchParams<{ id: string }>();
    const router = useRouter();
    const { analyses, currentAnalysis } = useVoiceStore();

    const analysis = analyses.find((a) => a.id === id) || currentAnalysis;

    if (!analysis) {
        return (
            <ScreenLayout>
                <View className="flex-1 justify-center items-center">
                    <Text className="text-5xl mb-4">🔍</Text>
                    <Text className="text-white text-xl font-medium">Analysis not found</Text>
                    <Button
                        title="Go Home"
                        onPress={() => router.replace("/")}
                        className="mt-6"
                    />
                </View>
            </ScreenLayout>
        );
    }

    const grade = getScoreGrade(analysis.score);
    const metrics = generateMetrics(analysis.score);

    return (
        <ScreenLayout>
            <ScrollView
                className="flex-1"
                contentContainerStyle={{ paddingBottom: 32 }}
                showsVerticalScrollIndicator={false}
            >
                {/* Back Button */}
                <View className="flex-row items-center mb-4">
                    <IconButton
                        icon="arrow-back"
                        onPress={() => router.back()}
                        variant="ghost"
                    />
                    <Text className="text-white text-lg ml-2">Back</Text>
                </View>

                {/* Score Display */}
                <View className="items-center py-8 space-y-4">
                    <Text className="text-text-secondary">Your Score</Text>
                    <View
                        className={`w-36 h-36 rounded-full ${grade.color} items-center justify-center shadow-lg`}
                    >
                        <Text className="text-5xl font-bold text-white">{analysis.score}</Text>
                    </View>
                    <Text className="text-2xl font-bold text-white">{grade.label}</Text>
                    <Text className="text-text-muted">
                        Duration: {formatDuration(analysis.duration)}
                    </Text>
                </View>

                <View className="space-y-6">
                    {/* Metrics */}
                    <Card>
                        <Text className="text-xl font-semibold text-white mb-4">
                            Performance Breakdown
                        </Text>
                        <View className="space-y-4">
                            {metrics.map((metric) => (
                                <ProgressBar
                                    key={metric.name}
                                    label={metric.name}
                                    value={metric.value}
                                    showValue
                                />
                            ))}
                        </View>
                    </Card>

                    {/* AI Feedback */}
                    <Card variant="glass">
                        <View className="flex-row items-center mb-4 space-x-2">
                            <Text className="text-2xl">🤖</Text>
                            <Text className="text-xl font-semibold text-white">AI Feedback</Text>
                        </View>
                        <View className="space-y-3">
                            {analysis.feedback.map((item, index) => (
                                <View key={index} className="flex-row space-x-3">
                                    <Text className="text-accent text-lg">✓</Text>
                                    <Text className="text-text-primary flex-1 leading-6">{item}</Text>
                                </View>
                            ))}
                        </View>
                    </Card>

                    {/* Actions */}
                    <View className="space-y-3 pt-4">
                        <Button
                            title="🎙️  Record Again"
                            onPress={() => router.replace("/recording")}
                            size="lg"
                        />
                        <Button
                            title="Back to Home"
                            variant="secondary"
                            onPress={() => router.replace("/")}
                        />
                    </View>
                </View>
            </ScrollView>
        </ScreenLayout>
    );
}
