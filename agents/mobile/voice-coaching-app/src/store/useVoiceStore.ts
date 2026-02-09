import { create } from 'zustand';
import { VoiceAnalysis, VoiceState } from '../types';

export const useVoiceStore = create<VoiceState>((set) => ({
    analyses: [],
    currentAnalysis: null,
    isRecording: false,

    addAnalysis: (analysis: VoiceAnalysis) =>
        set((state) => ({
            analyses: [analysis, ...state.analyses],
        })),

    setCurrentAnalysis: (analysis: VoiceAnalysis | null) =>
        set({ currentAnalysis: analysis }),

    setIsRecording: (isRecording: boolean) => set({ isRecording }),

    clearAnalyses: () => set({ analyses: [], currentAnalysis: null }),
}));
