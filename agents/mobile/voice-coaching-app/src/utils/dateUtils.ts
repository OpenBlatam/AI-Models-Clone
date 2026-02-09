// Date and time formatting utilities

/**
 * Format a timestamp to a human-readable date string
 */
export function formatDate(timestamp: number): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
        return `Today, ${formatTime(date)}`;
    } else if (days === 1) {
        return `Yesterday, ${formatTime(date)}`;
    } else if (days < 7) {
        return `${days} days ago`;
    } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
}

/**
 * Format a date to time string
 */
export function formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Format seconds to MM:SS format
 */
export function formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format seconds to MM:SS format with leading zeros on minutes
 */
export function formatRecordingTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
