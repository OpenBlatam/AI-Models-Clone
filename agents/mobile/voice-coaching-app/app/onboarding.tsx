import { Text, View, Animated, TextInput } from "react-native";
/// <reference types="nativewind/types" />
import { useRouter } from "expo-router";
import { useState, useRef, useEffect } from "react";
import { ScreenLayout } from "../src/components/layout/ScreenLayout";
import { Button } from "../src/components/ui/Button";
import { Card } from "../src/components/ui/Card";
import { useUserStore } from "../src/store/useUserStore";
import { VOICE_GOALS, EXPERIENCE_LEVELS } from "../src/constants";
import { haptics } from "../src/utils/haptics";

type Step = "welcome" | "goal" | "level" | "name";

function StepIndicator({ currentStep }: { currentStep: Step }) {
    const steps: Step[] = ["welcome", "goal", "level", "name"];
    const currentIndex = steps.indexOf(currentStep);

    return (
        <View className="flex-row space-x-2 justify-center">
            {steps.map((s, i) => (
                <View
                    key={s}
                    className={`w-3 h-3 rounded-full ${i <= currentIndex ? "bg-primary" : "bg-surface"
                        }`}
                />
            ))}
        </View>
    );
}

export default function Onboarding() {
    const router = useRouter();
    const { setProfile } = useUserStore();
    const [step, setStep] = useState<Step>("welcome");
    const [name, setName] = useState("");
    const [goal, setGoal] = useState("");
    const [level, setLevel] = useState<"beginner" | "intermediate" | "advanced">("beginner");

    const fadeAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 400,
            useNativeDriver: true,
        }).start();
    }, [step, fadeAnim]);

    const handleNext = async () => {
        await haptics.light();

        Animated.timing(fadeAnim, {
            toValue: 0,
            duration: 200,
            useNativeDriver: true,
        }).start(() => {
            if (step === "welcome") setStep("goal");
            else if (step === "goal") setStep("level");
            else if (step === "level") setStep("name");
            else {
                setProfile({
                    name: name.trim() || "Voice Coach User",
                    voiceGoal: goal,
                    level,
                    hasCompletedOnboarding: true,
                });
                haptics.success();
                router.replace("/");
            }
        });
    };

    const renderContent = () => {
        switch (step) {
            case "welcome":
                return (
                    <View className="items-center space-y-6">
                        <Text className="text-6xl">🎙️</Text>
                        <Text className="text-3xl font-bold text-white text-center">
                            Welcome to VoiceCoach AI
                        </Text>
                        <Text className="text-text-secondary text-center text-lg px-4">
                            Your personal AI-powered voice coach to help you master your vocal skills.
                        </Text>
                    </View>
                );

            case "goal":
                return (
                    <View className="space-y-6">
                        <Text className="text-2xl font-bold text-white text-center">
                            What's your voice goal?
                        </Text>
                        <View className="flex-row flex-wrap justify-center gap-3">
                            {VOICE_GOALS.map((g) => (
                                <Card
                                    key={g.id}
                                    variant={goal === g.id ? "default" : "glass"}
                                    className={`w-[45%] items-center p-4 ${goal === g.id ? "border-2 border-primary" : ""}`}
                                    onTouchEnd={() => {
                                        haptics.selection();
                                        setGoal(g.id);
                                    }}
                                >
                                    <Text className="text-3xl mb-2">{g.icon}</Text>
                                    <Text className="text-white text-center font-medium">{g.label}</Text>
                                </Card>
                            ))}
                        </View>
                    </View>
                );

            case "level":
                return (
                    <View className="space-y-6">
                        <Text className="text-2xl font-bold text-white text-center">
                            What's your experience level?
                        </Text>
                        <View className="space-y-4">
                            {EXPERIENCE_LEVELS.map((l) => (
                                <Card
                                    key={l.id}
                                    variant={level === l.id ? "default" : "glass"}
                                    className={`p-4 ${level === l.id ? "border-2 border-primary" : ""}`}
                                    onTouchEnd={() => {
                                        haptics.selection();
                                        setLevel(l.id as typeof level);
                                    }}
                                >
                                    <Text className="text-white text-lg font-medium">{l.label}</Text>
                                    <Text className="text-text-secondary">{l.desc}</Text>
                                </Card>
                            ))}
                        </View>
                    </View>
                );

            case "name":
                return (
                    <View className="space-y-6">
                        <Text className="text-2xl font-bold text-white text-center">
                            What should we call you?
                        </Text>
                        <Card>
                            <Text className="text-text-secondary mb-2">Your Name</Text>
                            <TextInput
                                value={name}
                                onChangeText={setName}
                                placeholder="Enter your name"
                                placeholderTextColor="#64748B"
                                className="text-white text-xl border-b-2 border-primary pb-2"
                            />
                        </Card>
                        <Text className="text-text-muted text-center text-sm">
                            You can change this later in settings
                        </Text>
                    </View>
                );
        }
    };

    return (
        <ScreenLayout>
            <View className="flex-1 justify-between py-8">
                <StepIndicator currentStep={step} />

                <Animated.View style={{ opacity: fadeAnim }} className="flex-1 justify-center px-4">
                    {renderContent()}
                </Animated.View>

                <Button
                    title={step === "name" ? "Get Started 🚀" : "Continue"}
                    onPress={handleNext}
                    size="lg"
                    disabled={step === "goal" && !goal}
                />
            </View>
        </ScreenLayout>
    );
}
