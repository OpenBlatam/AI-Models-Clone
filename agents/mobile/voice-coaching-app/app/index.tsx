import { Text, View } from "react-native";
/// <reference types="nativewind/types" />
import { Link, useRouter } from "expo-router";
import { ScreenLayout } from "../src/components/layout/ScreenLayout";
import { Button } from "../src/components/ui/Button";
import { Card } from "../src/components/ui/Card";

export default function Home() {
    const router = useRouter();

    return (
        <ScreenLayout>
            <View className="flex-1 justify-center items-center space-y-8">
                <View className="items-center space-y-2">
                    <Text className="text-4xl font-bold text-white text-center">
                        Voice<Text className="text-primary">Coach</Text> AI
                    </Text>
                    <Text className="text-text-secondary text-center text-lg">
                        Master your voice with AI-powered feedback
                    </Text>
                </View>

                <Card className="w-full space-y-4 p-6">
                    <Text className="text-xl font-semibold text-white mb-2">
                        Quick Actions
                    </Text>
                    <Button
                        title="Start New Recording"
                        onPress={() => router.push("/recording")}
                        size="lg"
                    />
                    <Button
                        title="View History"
                        variant="secondary"
                        onPress={() => { }}
                    />
                </Card>

                <View className="w-full">
                    <Text className="text-text-muted text-center text-sm">
                        Powered by Blatam AI
                    </Text>
                </View>
            </View>
        </ScreenLayout>
    );
}

