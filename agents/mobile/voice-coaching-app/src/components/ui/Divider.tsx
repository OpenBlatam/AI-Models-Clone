import React from "react";
import { View } from "react-native";
/// <reference types="nativewind/types" />

interface DividerProps {
    className?: string;
}

export function Divider({ className = "" }: DividerProps) {
    return <View className={`h-[1px] bg-white/10 ${className}`} />;
}
