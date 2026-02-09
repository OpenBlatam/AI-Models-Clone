import { useState, useCallback, useRef, useEffect } from 'react';
import { Audio } from 'expo-av';
import {
    getRecordingPermission,
    startRecording,
    stopRecording,
    analyzeVoice,
} from '../services/voiceService';
import { useVoiceStore } from '../store/useVoiceStore';
import { VoiceAnalysis, UseRecordingReturn } from '../types';

/**
 * Custom hook for managing voice recording
 * Handles permissions, recording state, timer, and analysis
 */
export function useRecording(): UseRecordingReturn {
    const [isRecording, setIsRecording] = useState(false);
    const [isPreparing, setIsPreparing] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [hasPermission, setHasPermission] = useState(false);

    const recordingRef = useRef<Audio.Recording | null>(null);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    const { addAnalysis, setCurrentAnalysis } = useVoiceStore();

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
            // Cleanup any active recording
            if (recordingRef.current) {
                recordingRef.current.stopAndUnloadAsync().catch(() => { });
            }
        };
    }, []);

    const requestPermission = useCallback(async (): Promise<boolean> => {
        const granted = await getRecordingPermission();
        setHasPermission(granted);
        return granted;
    }, []);

    const start = useCallback(async (): Promise<void> => {
        // Request permission if not granted
        if (!hasPermission) {
            const granted = await requestPermission();
            if (!granted) {
                console.warn('[useRecording] Microphone permission denied');
                return;
            }
        }

        setIsPreparing(true);

        try {
            const recording = await startRecording();
            if (recording) {
                recordingRef.current = recording;
                setIsRecording(true);
                setRecordingTime(0);

                // Start timer
                timerRef.current = setInterval(() => {
                    setRecordingTime((prev) => prev + 1);
                }, 1000);
            }
        } finally {
            setIsPreparing(false);
        }
    }, [hasPermission, requestPermission]);

    const stop = useCallback(async (): Promise<VoiceAnalysis | null> => {
        if (!recordingRef.current) {
            console.warn('[useRecording] No active recording to stop');
            return null;
        }

        // Stop timer
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }

        setIsRecording(false);
        setIsAnalyzing(true);

        try {
            const result = await stopRecording(recordingRef.current);
            recordingRef.current = null;

            if (result) {
                const analysis = await analyzeVoice(result.uri, result.duration);
                addAnalysis(analysis);
                setCurrentAnalysis(analysis);
                return analysis;
            }
            return null;
        } finally {
            setIsAnalyzing(false);
        }
    }, [addAnalysis, setCurrentAnalysis]);

    return {
        isRecording,
        isPreparing,
        isAnalyzing,
        recordingTime,
        hasPermission,
        start,
        stop,
        requestPermission,
    };
}
