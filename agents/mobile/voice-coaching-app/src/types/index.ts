// Type definitions for Voice Coaching App

export interface VoiceAnalysis {
    id: string;
    timestamp: number;
    duration: number;
    score: number;
    feedback: string[];
    audioUri?: string;
}

export interface UserProfile {
    name: string;
    voiceGoal: string;
    level: 'beginner' | 'intermediate' | 'advanced';
    hasCompletedOnboarding: boolean;
}

export interface VoiceMetric {
    name: string;
    value: number;
    description?: string;
}

export interface VoiceTipCategory {
    category: string;
    icon: string;
    tips: string[];
}

// Store types
export interface VoiceState {
    analyses: VoiceAnalysis[];
    currentAnalysis: VoiceAnalysis | null;
    isRecording: boolean;
    addAnalysis: (analysis: VoiceAnalysis) => void;
    setCurrentAnalysis: (analysis: VoiceAnalysis | null) => void;
    setIsRecording: (isRecording: boolean) => void;
    clearAnalyses: () => void;
}

export interface UserState {
    profile: UserProfile | null;
    setProfile: (profile: UserProfile) => void;
    updateProfile: (updates: Partial<UserProfile>) => void;
    completeOnboarding: () => void;
    resetProfile: () => void;
}

// Recording types
export interface RecordingResult {
    uri: string;
    duration: number;
}

export interface UseRecordingReturn {
    isRecording: boolean;
    isPreparing: boolean;
    isAnalyzing: boolean;
    recordingTime: number;
    hasPermission: boolean;
    start: () => Promise<void>;
    stop: () => Promise<VoiceAnalysis | null>;
    requestPermission: () => Promise<boolean>;
}
