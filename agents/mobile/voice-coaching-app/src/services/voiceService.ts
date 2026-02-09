import { Audio } from 'expo-av';
import { VoiceAnalysis, RecordingResult } from '../types';
import { VOICE_TIPS } from '../constants';

// ============================================================================
// Mock Analysis
// ============================================================================

const FEEDBACK_POOL = [
    "Great articulation and clarity throughout your speech.",
    "Your pace was consistent and easy to follow.",
    "Try varying your tone to emphasize key points.",
    "Excellent projection and voice volume.",
    "Consider adding more pauses for dramatic effect.",
    "Your confidence comes through clearly in your voice.",
    "Work on breathing techniques for longer phrases.",
    "Good use of emphasis on important words.",
    "Try to eliminate filler words like 'um' and 'uh'.",
    "Your enunciation was clear and precise.",
];

function generateMockAnalysis(audioUri: string, duration: number): VoiceAnalysis {
    const id = Date.now().toString();
    const score = Math.floor(Math.random() * 30) + 70; // 70-100

    // Select 3-4 random feedback items
    const shuffled = [...FEEDBACK_POOL].sort(() => Math.random() - 0.5);
    const feedback = shuffled.slice(0, Math.floor(Math.random() * 2) + 3);

    return {
        id,
        timestamp: Date.now(),
        duration,
        score,
        feedback,
        audioUri,
    };
}

// ============================================================================
// Recording Functions
// ============================================================================

/**
 * Request microphone permission
 */
export async function getRecordingPermission(): Promise<boolean> {
    try {
        const { status } = await Audio.requestPermissionsAsync();
        return status === 'granted';
    } catch (error) {
        console.error('[VoiceService] Failed to request permission:', error);
        return false;
    }
}

/**
 * Start a new audio recording
 */
export async function startRecording(): Promise<Audio.Recording | null> {
    try {
        await Audio.setAudioModeAsync({
            allowsRecordingIOS: true,
            playsInSilentModeIOS: true,
        });

        const recording = new Audio.Recording();
        await recording.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
        await recording.startAsync();

        console.log('[VoiceService] Recording started');
        return recording;
    } catch (error) {
        console.error('[VoiceService] Failed to start recording:', error);
        return null;
    }
}

/**
 * Stop an active recording and get the result
 */
export async function stopRecording(
    recording: Audio.Recording
): Promise<RecordingResult | null> {
    try {
        await recording.stopAndUnloadAsync();
        const uri = recording.getURI();
        const status = await recording.getStatusAsync();

        if (uri && status.durationMillis) {
            console.log('[VoiceService] Recording stopped:', uri);
            return {
                uri,
                duration: Math.round(status.durationMillis / 1000),
            };
        }
        return null;
    } catch (error) {
        console.error('[VoiceService] Failed to stop recording:', error);
        return null;
    }
}

// ============================================================================
// Analysis Functions
// ============================================================================

/**
 * Analyze a voice recording (mock implementation)
 */
export async function analyzeVoice(
    audioUri: string,
    duration: number
): Promise<VoiceAnalysis> {
    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return generateMockAnalysis(audioUri, duration);
}

/**
 * Get a random tip from a category
 */
export function getRandomTip(
    category: keyof typeof VOICE_TIPS
): string {
    const tips = VOICE_TIPS[category];
    return tips[Math.floor(Math.random() * tips.length)];
}
