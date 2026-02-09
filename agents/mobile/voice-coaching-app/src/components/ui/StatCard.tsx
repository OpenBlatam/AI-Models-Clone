import React from "react";
import { Text, View } from "react-native";
/// <reference types="nativewind/types" />
import { Card } from "./Card";

interface StatCardProps {
    label: string;
    value: string | number;
    suffix?: string;
}

export function StatCard({ label, value, suffix = "" }: StatCardProps) {
    return (
        <Card variant="glass" className="flex-1 items-center p-4">
            <Text className="text-3xl font-bold text-accent">
                {value}
                {suffix}
            </Text>
            <Text className="text-text-secondary text-sm mt-1">{label}</Text>
        </Card>
    );
}
