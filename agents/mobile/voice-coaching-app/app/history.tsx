import { Text, View, FlatList, TouchableOpacity } from "react-native";
/// <reference types="nativewind/types" />
import { useRouter } from "expo-router";
import { ScreenLayout } from "../src/components/layout/ScreenLayout";
import { Card } from "../src/components/ui/Card";

export default function History() {
    const router = useRouter();

    // Mock data
    const history = [
        { id: "1", date: "Today, 10:30 AM", score: 85, duration: "2:30" },
        { id: "2", date: "Yesterday, 4:15 PM", score: 78, duration: "1:45" },
        { id: "3", date: "Dec 24, 9:00 AM", score: 92, duration: "3:10" },
    ];

    return (
        <ScreenLayout>
            <View className="py-6">
                <Text className="text-3xl font-bold text-white mb-6">History</Text>

                <FlatList
                    data={history}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={{ gap: 16 }}
                    renderItem={({ item }) => (
                        <TouchableOpacity onPress={() => router.push(`/analysis/${item.id}`)}>
                            <Card className="flex-row items-center justify-between">
                                <View>
                                    <Text className="text-white font-semibold text-lg">{item.date}</Text>
                                    <Text className="text-text-secondary">Duration: {item.duration}</Text>
                                </View>
                                <View className="items-end">
                                    <Text className="text-2xl font-bold text-accent">{item.score}</Text>
                                    <Text className="text-text-muted text-xs">Score</Text>
                                </View>
                            </Card>
                        </TouchableOpacity>
                    )}
                />
            </View>
        </ScreenLayout>
    );
}
