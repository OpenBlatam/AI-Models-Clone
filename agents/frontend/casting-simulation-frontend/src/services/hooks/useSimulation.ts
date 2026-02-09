/**
 * Custom hooks for simulation operations
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import useSWR from 'swr';
import { useSimulationStore } from '@/services/store/simulationStore';
import * as api from '@/services/api/client';
import type { TaskStatusResponse, SimulationResponse } from '@/types';

// ========== Health Check Hook ==========

export function useHealthCheck() {
    const { setConnected } = useSimulationStore();

    const { data, error, isLoading } = useSWR(
        'health',
        () => api.checkHealth(),
        {
            refreshInterval: 30000, // Check every 30 seconds
            onSuccess: () => setConnected(true),
            onError: () => setConnected(false),
        }
    );

    return {
        health: data,
        isConnected: !error && !!data,
        isLoading,
        error,
    };
}

// ========== Generic Simulation Hook ==========

interface UseSimulationOptions<TRequest, TResponse> {
    runFn: (data: TRequest) => Promise<SimulationResponse>;
    createTaskFn?: (data: TRequest) => Promise<{ task_id: string }>;
    simulationType: string;
}

export function useSimulation<TRequest>({
    runFn,
    createTaskFn,
    simulationType,
}: UseSimulationOptions<TRequest, SimulationResponse>) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<SimulationResponse | null>(null);
    const { addTask, updateTask, completeTask, failTask } = useSimulationStore();

    const run = useCallback(async (data: TRequest): Promise<SimulationResponse | null> => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await runFn(data);
            setResult(response);
            return response;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [runFn]);

    const runAsync = useCallback(async (data: TRequest): Promise<string | null> => {
        if (!createTaskFn) {
            setError('Async not supported');
            return null;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await createTaskFn(data);
            addTask(response.task_id, simulationType);
            return response.task_id;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [createTaskFn, addTask, simulationType]);

    return {
        run,
        runAsync,
        isLoading,
        error,
        result,
        clearError: () => setError(null),
        clearResult: () => setResult(null),
    };
}

// ========== Task Polling Hook ==========

export function useTaskPolling(taskId: string | null, enabled: boolean = true) {
    const [status, setStatus] = useState<TaskStatusResponse | null>(null);
    const [result, setResult] = useState<SimulationResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isPolling, setIsPolling] = useState(false);
    const { updateTask, completeTask, failTask } = useSimulationStore();

    useEffect(() => {
        if (!taskId || !enabled) return;

        let cancelled = false;
        let timeoutId: NodeJS.Timeout;

        const poll = async () => {
            if (cancelled) return;
            setIsPolling(true);

            try {
                const taskStatus = await api.getTaskStatus(taskId);
                if (cancelled) return;

                setStatus(taskStatus);
                updateTask(taskId, { status: taskStatus.status });

                if (taskStatus.status === 'completed') {
                    const taskResult = await api.getTaskResult(taskId);
                    if (!cancelled) {
                        setResult(taskResult);
                        completeTask(taskId, taskResult);
                        setIsPolling(false);
                    }
                } else if (taskStatus.status === 'failed') {
                    if (!cancelled) {
                        setError('Task failed');
                        failTask(taskId, 'Task failed');
                        setIsPolling(false);
                    }
                } else {
                    // Still pending or running, continue polling
                    timeoutId = setTimeout(poll, 2000);
                }
            } catch (err) {
                if (!cancelled) {
                    const message = err instanceof Error ? err.message : 'Polling error';
                    setError(message);
                    failTask(taskId, message);
                    setIsPolling(false);
                }
            }
        };

        poll();

        return () => {
            cancelled = true;
            if (timeoutId) clearTimeout(timeoutId);
        };
    }, [taskId, enabled, updateTask, completeTask, failTask]);

    return {
        status,
        result,
        error,
        isPolling,
    };
}

// ========== Specialized Hooks ==========

export function useMeshSimulation() {
    return useSimulation({
        runFn: api.runMeshAnalysis,
        createTaskFn: api.createMeshTask,
        simulationType: 'mesh',
    });
}

export function useFillingSimulation() {
    return useSimulation({
        runFn: api.runFillingSimulation,
        createTaskFn: api.createFillingTask,
        simulationType: 'filling',
    });
}

export function useSolidificationSimulation() {
    return useSimulation({
        runFn: api.runSolidificationSimulation,
        createTaskFn: api.createSolidificationTask,
        simulationType: 'solidification',
    });
}

export function useStressSimulation() {
    return useSimulation({
        runFn: api.runStressAnalysis,
        createTaskFn: api.createStressTask,
        simulationType: 'stress',
    });
}

export function useHeatTreatmentSimulation() {
    return useSimulation({
        runFn: api.runHeatTreatment,
        createTaskFn: api.createHeatTreatmentTask,
        simulationType: 'heat-treatment',
    });
}
