/**
 * Zustand store for simulation state management
 */

import { create } from 'zustand';
import type { TaskStatusResponse, SimulationResponse } from '@/types';

interface ActiveTask {
    id: string;
    type: string;
    status: TaskStatusResponse['status'];
    startedAt: Date;
    result?: SimulationResponse;
    error?: string;
}

interface SimulationState {
    // Active tasks being polled
    activeTasks: Map<string, ActiveTask>;

    // Completed simulation history
    history: SimulationResponse[];

    // API connection status
    isConnected: boolean;

    // Actions
    addTask: (taskId: string, type: string) => void;
    updateTask: (taskId: string, update: Partial<ActiveTask>) => void;
    completeTask: (taskId: string, result: SimulationResponse) => void;
    failTask: (taskId: string, error: string) => void;
    removeTask: (taskId: string) => void;
    setConnected: (connected: boolean) => void;
    clearHistory: () => void;
}

export const useSimulationStore = create<SimulationState>((set) => ({
    activeTasks: new Map(),
    history: [],
    isConnected: false,

    addTask: (taskId, type) =>
        set((state) => {
            const tasks = new Map(state.activeTasks);
            tasks.set(taskId, {
                id: taskId,
                type,
                status: 'pending',
                startedAt: new Date(),
            });
            return { activeTasks: tasks };
        }),

    updateTask: (taskId, update) =>
        set((state) => {
            const tasks = new Map(state.activeTasks);
            const existing = tasks.get(taskId);
            if (existing) {
                tasks.set(taskId, { ...existing, ...update });
            }
            return { activeTasks: tasks };
        }),

    completeTask: (taskId, result) =>
        set((state) => {
            const tasks = new Map(state.activeTasks);
            const task = tasks.get(taskId);
            if (task) {
                task.status = 'completed';
                task.result = result;
                tasks.set(taskId, task);
            }
            return {
                activeTasks: tasks,
                history: [result, ...state.history].slice(0, 50), // Keep last 50
            };
        }),

    failTask: (taskId, error) =>
        set((state) => {
            const tasks = new Map(state.activeTasks);
            const task = tasks.get(taskId);
            if (task) {
                task.status = 'failed';
                task.error = error;
                tasks.set(taskId, task);
            }
            return { activeTasks: tasks };
        }),

    removeTask: (taskId) =>
        set((state) => {
            const tasks = new Map(state.activeTasks);
            tasks.delete(taskId);
            return { activeTasks: tasks };
        }),

    setConnected: (connected) => set({ isConnected: connected }),

    clearHistory: () => set({ history: [] }),
}));
