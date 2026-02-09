import { Text, View, Switch } from "react-native";
/// <reference types="nativewind/types" />
import { ScreenLayout } from "../src/components/layout/ScreenLayout";
import { Card } from "../src/components/ui/Card";
import { Button } from "../src/components/ui/Button";

export default function Settings() {
    return (
        <ScreenLayout>
            <View className="py-6 space-y-6">
                <Text className="text-3xl font-bold text-white">Settings</Text>

                <Card className="space-y-6">
                    <View className="flex-row items-center justify-between">
                        <Text className="text-white text-lg">Dark Mode</Text>
                        <Switch value={true} trackColor={{ true: "#4F46E5" }} />
                    </View>

                    <View className="h-[1px] bg-white/10" />

                    <View className="flex-row items-center justify-between">
                        <Text className="text-white text-lg">Notifications</Text>
                        <Switch value={false} trackColor={{ true: "#4F46E5" }} />
                    </View>

                    <View className="h-[1px] bg-white/10" />

                    <View className="flex-row items-center justify-between">
                        <Text className="text-white text-lg">High Quality Audio</Text>
                        <Switch value={true} trackColor={{ true: "#4F46E5" }} />
                    </View>
                </Card>

                <Button title="Sign Out" variant="outline" className="mt-8" />

                <Text className="text-center text-text-muted">Version 1.0.0</Text>
            </View>
        </ScreenLayout>
    );
}
