import { Text, View, ScrollView } from "react-native";
/// <reference types="nativewind/types" />
import { ScreenLayout } from "../src/components/layout/ScreenLayout";
import { Card } from "../src/components/ui/Card";
import { Button } from "../src/components/ui/Button";
import { Header } from "../src/components/ui/Header";
import { IconButton } from "../src/components/ui/IconButton";
import { Divider } from "../src/components/ui/Divider";
import { useRouter } from "expo-router";
import { VOICE_TIPS } from "../src/constants";

const TIP_SECTIONS = [
    { category: "Breathing", icon: "🌬️", key: "breathing" as const },
    { category: "Clarity", icon: "💬", key: "clarity" as const },
    { category: "Tone", icon: "🎵", key: "tone" as const },
    { category: "Confidence", icon: "💪", key: "confidence" as const },
    { category: "Pace", icon: "⏱️", key: "pace" as const },
];

export default function Tips() {
    const router = useRouter();

    return (
        <ScreenLayout>
            <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
                <View className="py-6 space-y-6">
                    {/* Header */}
                    <View className="flex-row items-center justify-between">
                        <Header title="Voice Tips" subtitle="Expert recommendations" />
                        <IconButton
                            icon="close"
                            onPress={() => router.back()}
                            variant="ghost"
                        />
                    </View>

                    {/* Tips by Category */}
                    {TIP_SECTIONS.map((section, idx) => (
                        <Card key={section.key} variant="glass">
                            <View className="flex-row items-center space-x-2 mb-4">
                                <Text className="text-2xl">{section.icon}</Text>
                                <Text className="text-xl font-semibold text-white">{section.category}</Text>
                            </View>
                            <View className="space-y-3">
                                {VOICE_TIPS[section.key].map((tip, tipIdx) => (
                                    <View key={tipIdx} className="flex-row space-x-3">
                                        <Text className="text-accent">•</Text>
                                        <Text className="text-text-primary flex-1">{tip}</Text>
                                    </View>
                                ))}
                            </View>
                        </Card>
                    ))}

                    {/* CTA */}
                    <Button
                        title="Start Practicing"
                        onPress={() => router.push("/recording")}
                        size="lg"
                    />
                </View>
            </ScrollView>
        </ScreenLayout>
    );
}
