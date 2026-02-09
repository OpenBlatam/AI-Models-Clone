import { View, FlatList } from "react-native";
/// <reference types="nativewind/types" />
import { useRouter } from "expo-router";
import { ScreenLayout } from "../../src/components/layout/ScreenLayout";
import { Header } from "../../src/components/ui/Header";
import { Button } from "../../src/components/ui/Button";
import { EmptyState } from "../../src/components/ui/EmptyState";
import { AnalysisCard } from "../../src/components/ui/AnalysisCard";
import { useVoiceStore } from "../../src/store/useVoiceStore";

export default function History() {
    const router = useRouter();
    const { analyses } = useVoiceStore();

    if (analyses.length === 0) {
        return (
            <ScreenLayout>
                <View className="flex-1 justify-center">
                    <EmptyState
                        icon="📂"
                        title="No recordings yet"
                        description="Complete a voice coaching session to see your history here."
                    >
                        <Button
                            title="Start Recording"
                            onPress={() => router.push("/recording")}
                        />
                    </EmptyState>
                </View>
            </ScreenLayout>
        );
    }

    return (
        <ScreenLayout>
            <View className="py-6 flex-1">
                <Header
                    title="History"
                    subtitle={`${analyses.length} recording${analyses.length !== 1 ? "s" : ""}`}
                />

                <FlatList
                    data={analyses}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={{ gap: 12 }}
                    showsVerticalScrollIndicator={false}
                    renderItem={({ item }) => (
                        <AnalysisCard
                            analysis={item}
                            onPress={() => router.push(`/analysis/${item.id}`)}
                        />
                    )}
                />
            </View>
        </ScreenLayout>
    );
}
