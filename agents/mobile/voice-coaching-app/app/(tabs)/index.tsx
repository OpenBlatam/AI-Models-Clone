import { Text, View, ScrollView } from "react-native";
/// <reference types="nativewind/types" />
import { useRouter } from "expo-router";
import { ScreenLayout } from "../../src/components/layout/ScreenLayout";
import { Button } from "../../src/components/ui/Button";
import { Card } from "../../src/components/ui/Card";
import { StatCard } from "../../src/components/ui/StatCard";
import { EmptyState } from "../../src/components/ui/EmptyState";
import { AnalysisCard } from "../../src/components/ui/AnalysisCard";
import { useVoiceStore } from "../../src/store/useVoiceStore";
import { useUserStore } from "../../src/store/useUserStore";
import { calculateAverageScore, getBestScore } from "../../src/utils";

export default function Home() {
    const router = useRouter();
    const { analyses } = useVoiceStore();
    const { profile } = useUserStore();

    const totalRecordings = analyses.length;
    const averageScore = calculateAverageScore(analyses.map((a) => a.score));
    const bestScore = getBestScore(analyses.map((a) => a.score));

    return (
        <ScreenLayout>
            <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
                <View className="py-8 space-y-8">
                    {/* Greeting */}
                    <View className="items-center space-y-2">
                        <Text className="text-4xl font-bold text-white text-center">
                            {profile?.name ? `Hello, ${profile.name}!` : "VoiceCoach AI"}
                        </Text>
                        <Text className="text-text-secondary text-center text-lg">
                            Ready to improve your voice?
                        </Text>
                    </View>

                    {/* Stats */}
                    {totalRecordings > 0 && (
                        <View className="flex-row space-x-3">
                            <StatCard label="Sessions" value={totalRecordings} />
                            <StatCard label="Avg Score" value={averageScore} />
                            <StatCard label="Best" value={bestScore} />
                        </View>
                    )}

                    {/* Quick Actions */}
                    <Card className="space-y-4 p-6">
                        <Text className="text-xl font-semibold text-white mb-2">
                            Quick Actions
                        </Text>
                        <Button
                            title="🎙️  Start New Recording"
                            onPress={() => router.push("/recording")}
                            size="lg"
                        />
                        <Button
                            title="📊  View History"
                            variant="secondary"
                            onPress={() => router.push("/(tabs)/history")}
                        />
                        <Button
                            title="💡  Voice Tips"
                            variant="outline"
                            onPress={() => router.push("/tips")}
                        />
                    </Card>

                    {/* Recent Activity */}
                    {analyses.length > 0 && (
                        <View className="space-y-4">
                            <Text className="text-xl font-semibold text-white">
                                Recent Activity
                            </Text>
                            {analyses.slice(0, 3).map((analysis) => (
                                <AnalysisCard
                                    key={analysis.id}
                                    analysis={analysis}
                                    onPress={() => router.push(`/analysis/${analysis.id}`)}
                                />
                            ))}
                        </View>
                    )}

                    {/* Empty State */}
                    {analyses.length === 0 && (
                        <EmptyState
                            icon="🎯"
                            title="No recordings yet"
                            description="Start your first voice coaching session!"
                        />
                    )}

                    {/* Footer */}
                    <View className="items-center pt-4">
                        <Text className="text-text-muted text-sm">Powered by Blatam AI</Text>
                    </View>
                </View>
            </ScrollView>
        </ScreenLayout>
    );
}
