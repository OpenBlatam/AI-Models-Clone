import { Text, View, Switch, TextInput, TouchableOpacity, Alert, ScrollView } from "react-native";
/// <reference types="nativewind/types" />
import { ScreenLayout } from "../../src/components/layout/ScreenLayout";
import { Card } from "../../src/components/ui/Card";
import { Button } from "../../src/components/ui/Button";
import { Avatar } from "../../src/components/ui/Avatar";
import { Divider } from "../../src/components/ui/Divider";
import { Header } from "../../src/components/ui/Header";
import { StatCard } from "../../src/components/ui/StatCard";
import { useUserStore } from "../../src/store/useUserStore";
import { useVoiceStore } from "../../src/store/useVoiceStore";
import { calculateAverageScore, getBestScore } from "../../src/utils";
import { useState } from "react";
import { useRouter } from "expo-router";

interface SettingRowProps {
    label: string;
    value: boolean;
    onToggle: () => void;
}

function SettingRow({ label, value, onToggle }: SettingRowProps) {
    return (
        <View className="flex-row items-center justify-between py-3">
            <Text className="text-white text-lg">{label}</Text>
            <Switch value={value} onValueChange={onToggle} trackColor={{ true: "#4F46E5" }} />
        </View>
    );
}

export default function Settings() {
    const router = useRouter();
    const { profile, updateProfile, resetProfile } = useUserStore();
    const { analyses, clearAnalyses } = useVoiceStore();
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState(profile?.name || "");

    const [darkMode, setDarkMode] = useState(true);
    const [notifications, setNotifications] = useState(false);
    const [highQuality, setHighQuality] = useState(true);

    const stats = {
        sessions: analyses.length,
        avgScore: calculateAverageScore(analyses.map((a) => a.score)),
        bestScore: getBestScore(analyses.map((a) => a.score)),
    };

    const handleSaveName = () => {
        if (editName.trim()) {
            updateProfile({ name: editName.trim() });
        }
        setIsEditing(false);
    };

    const handleReset = () => {
        Alert.alert(
            "Reset App",
            "This will clear all your data. Are you sure?",
            [
                { text: "Cancel", style: "cancel" },
                {
                    text: "Reset",
                    style: "destructive",
                    onPress: () => {
                        clearAnalyses();
                        resetProfile();
                        router.replace("/onboarding");
                    },
                },
            ]
        );
    };

    return (
        <ScreenLayout>
            <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
                <View className="py-6 space-y-6">
                    <Header title="Settings" />

                    {/* Profile */}
                    <Card>
                        <View className="flex-row items-center space-x-4 mb-4">
                            <Avatar name={profile?.name} size="lg" />
                            <View className="flex-1">
                                {isEditing ? (
                                    <TextInput
                                        value={editName}
                                        onChangeText={setEditName}
                                        onBlur={handleSaveName}
                                        onSubmitEditing={handleSaveName}
                                        autoFocus
                                        className="text-white text-xl font-semibold border-b border-primary pb-1"
                                        placeholderTextColor="#64748B"
                                    />
                                ) : (
                                    <TouchableOpacity onPress={() => setIsEditing(true)}>
                                        <Text className="text-white text-xl font-semibold">
                                            {profile?.name || "Set your name"}
                                        </Text>
                                        <Text className="text-text-muted text-sm">Tap to edit</Text>
                                    </TouchableOpacity>
                                )}
                            </View>
                        </View>

                        <Divider className="my-4" />

                        <View className="flex-row justify-around">
                            <View className="items-center">
                                <Text className="text-accent text-xl font-bold">{stats.sessions}</Text>
                                <Text className="text-text-muted text-sm">Sessions</Text>
                            </View>
                            <View className="items-center">
                                <Text className="text-accent text-xl font-bold">{stats.avgScore}</Text>
                                <Text className="text-text-muted text-sm">Avg Score</Text>
                            </View>
                            <View className="items-center">
                                <Text className="text-accent text-xl font-bold">{stats.bestScore}</Text>
                                <Text className="text-text-muted text-sm">Best</Text>
                            </View>
                        </View>
                    </Card>

                    {/* Preferences */}
                    <Card>
                        <Text className="text-lg font-semibold text-white mb-2">Preferences</Text>
                        <SettingRow label="Dark Mode" value={darkMode} onToggle={() => setDarkMode(!darkMode)} />
                        <Divider />
                        <SettingRow label="Notifications" value={notifications} onToggle={() => setNotifications(!notifications)} />
                        <Divider />
                        <SettingRow label="High Quality Audio" value={highQuality} onToggle={() => setHighQuality(!highQuality)} />
                    </Card>

                    {/* About */}
                    <Card variant="glass">
                        <Text className="text-lg font-semibold text-white mb-4">About</Text>
                        <View className="space-y-3">
                            <View className="flex-row justify-between">
                                <Text className="text-text-secondary">Version</Text>
                                <Text className="text-white">1.0.0</Text>
                            </View>
                            <View className="flex-row justify-between">
                                <Text className="text-text-secondary">Developer</Text>
                                <Text className="text-white">Blatam AI</Text>
                            </View>
                            <View className="flex-row justify-between">
                                <Text className="text-text-secondary">Components</Text>
                                <Text className="text-white">17</Text>
                            </View>
                        </View>
                    </Card>

                    {/* Actions */}
                    <Button title="Reset App Data" variant="outline" onPress={handleReset} />
                </View>
            </ScrollView>
        </ScreenLayout>
    );
}
