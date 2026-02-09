// Theme constants for Voice Coaching App
export const COLORS = {
    primary: '#4F46E5',
    secondary: '#7C3AED',
    accent: '#06B6D4',
    background: '#0F172A',
    surface: '#1E293B',
    text: {
        primary: '#F1F5F9',
        secondary: '#94A3B8',
        muted: '#64748B',
    },
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    white: '#FFFFFF',
} as const;

export const SPACING = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
} as const;

export const FONT_SIZES = {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 32,
    title: 40,
} as const;

export const BORDER_RADIUS = {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    full: 9999,
} as const;

// Voice coaching related constants
export const VOICE_GOALS = [
    { id: 'public-speaking', label: 'Public Speaking', icon: '🎤' },
    { id: 'presentations', label: 'Presentations', icon: '📊' },
    { id: 'singing', label: 'Singing', icon: '🎵' },
    { id: 'podcasting', label: 'Podcasting', icon: '🎙️' },
    { id: 'interviews', label: 'Interviews', icon: '💼' },
    { id: 'general', label: 'General Improvement', icon: '✨' },
] as const;

export const EXPERIENCE_LEVELS = [
    { id: 'beginner', label: 'Beginner', desc: 'Just starting out' },
    { id: 'intermediate', label: 'Intermediate', desc: 'Some experience' },
    { id: 'advanced', label: 'Advanced', desc: 'Looking to perfect' },
] as const;

export const VOICE_TIPS = {
    breathing: [
        'Practice diaphragmatic breathing for better control',
        'Take deep breaths before speaking to reduce tension',
        'Use breath pauses strategically for emphasis',
    ],
    clarity: [
        'Articulate consonants clearly, especially at the end of words',
        'Slow down when presenting complex information',
        'Record yourself and listen for mumbled words',
    ],
    tone: [
        'Vary your pitch to avoid monotone',
        'Match your tone to your message\'s emotion',
        'Practice speaking with a smile for warmth',
    ],
    confidence: [
        'Stand or sit up straight while speaking',
        'Make eye contact (or look at the camera)',
        'Embrace pauses instead of filler words',
    ],
    pace: [
        'Aim for 120-150 words per minute',
        'Slow down for important points',
        'Use pauses to let ideas sink in',
    ],
} as const;

// Score grading
export function getScoreGrade(score: number): { label: string; color: string } {
    if (score >= 90) return { label: 'Excellent!', color: 'bg-green-500' };
    if (score >= 80) return { label: 'Great!', color: 'bg-primary' };
    if (score >= 70) return { label: 'Good', color: 'bg-accent' };
    if (score >= 60) return { label: 'Fair', color: 'bg-yellow-500' };
    return { label: 'Needs Work', color: 'bg-orange-500' };
}

export function getScoreTextColor(score: number): string {
    if (score >= 90) return 'text-green-400';
    if (score >= 75) return 'text-accent';
    if (score >= 60) return 'text-yellow-400';
    return 'text-orange-400';
}
