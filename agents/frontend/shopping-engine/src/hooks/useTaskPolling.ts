'use client';

import { useState, useEffect, useCallback } from 'react';
import apiClient from '@/src/api/client';
import type { TaskStatusResponse } from '@/src/types/api';

interface UseTaskPollingOptions {
    pollingInterval?: number;
    maxAttempts?: number;
    onComplete?: <T>(result: T) => void;
    onError?: (error: string) => void;
}

interface UseTaskPollingReturn<T> {
    status: TaskStatusResponse | null;
    result: T | null;
    isPolling: boolean;
    error: string | null;
    startPolling: (taskId: string) => void;
    stopPolling: () => void;
}

export const useTaskPolling = <T>(
    options: UseTaskPollingOptions = {}
): UseTaskPollingReturn<T> => {
    const {
        pollingInterval = 2000,
        maxAttempts = 60,
        onComplete,
        onError,
    } = options;

    const [taskId, setTaskId] = useState<string | null>(null);
    const [status, setStatus] = useState<TaskStatusResponse | null>(null);
    const [result, setResult] = useState<T | null>(null);
    const [isPolling, setIsPolling] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [attempts, setAttempts] = useState(0);

    const stopPolling = useCallback(() => {
        setIsPolling(false);
        setTaskId(null);
        setAttempts(0);
    }, []);

    const startPolling = useCallback((newTaskId: string) => {
        setTaskId(newTaskId);
        setIsPolling(true);
        setError(null);
        setResult(null);
        setStatus(null);
        setAttempts(0);
    }, []);

    useEffect(() => {
        if (!isPolling || !taskId) {
            return;
        }

        const pollStatus = async () => {
            try {
                const statusResponse = await apiClient.getTaskStatus(taskId);
                setStatus(statusResponse);

                if (statusResponse.status === 'completed') {
                    const taskResult = await apiClient.getTaskResult<T>(taskId);
                    setResult(taskResult);
                    stopPolling();
                    onComplete?.(taskResult);
                    return;
                }

                if (statusResponse.status === 'failed') {
                    const errorMessage = statusResponse.error || 'Task failed';
                    setError(errorMessage);
                    stopPolling();
                    onError?.(errorMessage);
                    return;
                }

                setAttempts((prev) => prev + 1);
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Polling failed';
                setError(errorMessage);
                stopPolling();
                onError?.(errorMessage);
            }
        };

        if (attempts >= maxAttempts) {
            const timeoutError = 'Task polling timeout';
            setError(timeoutError);
            stopPolling();
            onError?.(timeoutError);
            return;
        }

        const timeoutId = setTimeout(pollStatus, attempts === 0 ? 0 : pollingInterval);

        return () => clearTimeout(timeoutId);
    }, [isPolling, taskId, attempts, pollingInterval, maxAttempts, stopPolling, onComplete, onError]);

    return {
        status,
        result,
        isPolling,
        error,
        startPolling,
        stopPolling,
    };
};

export default useTaskPolling;
