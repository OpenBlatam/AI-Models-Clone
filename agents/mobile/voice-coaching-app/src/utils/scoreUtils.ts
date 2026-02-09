// Score and analysis utilities

import { getScoreGrade, getScoreTextColor } from '../constants';

/**
 * Calculate average score from an array of scores
 */
export function calculateAverageScore(scores: number[]): number {
    if (scores.length === 0) return 0;
    return Math.round(scores.reduce((sum, s) => sum + s, 0) / scores.length);
}

/**
 * Get the best score from an array
 */
export function getBestScore(scores: number[]): number {
    if (scores.length === 0) return 0;
    return Math.max(...scores);
}

/**
 * Generate random metrics based on overall score
 */
export function generateMetrics(overallScore: number): Array<{ name: string; value: number }> {
    const metrics = ['Clarity', 'Pace', 'Tone', 'Confidence'];
    return metrics.map((name) => ({
        name,
        value: Math.min(100, Math.max(0, overallScore + Math.floor(Math.random() * 20) - 10)),
    }));
}

// Re-export theme utilities
export { getScoreGrade, getScoreTextColor };
