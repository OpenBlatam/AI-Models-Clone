/**
 * @fileoverview React hook for AI operations
 * @author Blaze AI Team
 */

import { useCallback, useEffect, useState, useMemo } from 'react';
import { aiManager } from '../../lib/ai/ai-manager';
import {
  AIModel,
  AIRequestUnion,
  AIResponseUnion,
  AITask,
  AIWorkflowExecution,
  AIEvent,
  AISystemConfig,
  AIUserPreferences,
} from '../../lib/ai/ai-types';

// ============================================================================
// HOOK STATE INTERFACE
// ============================================================================

interface AIHookState {
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  models: AIModel[];
  activeTasks: AITask[];
  activeExecutions: AIWorkflowExecution[];
  recentEvents: AIEvent[];
  systemConfig: AISystemConfig | null;
}

// ============================================================================
// HOOK ACTIONS INTERFACE
// ============================================================================

interface AIHookActions {
  initialize: (config?: Partial<AISystemConfig>) => Promise<void>;
  processRequest: (request: AIRequestUnion) => Promise<AIResponseUnion>;
  executeWorkflow: (workflowId: string, input: Record<string, unknown>, userId: string) => Promise<string>;
  addModel: (model: Omit<AIModel, 'id' | 'createdAt' | 'updatedAt'>) => Promise<string>;
  updateModel: (modelId: string, updates: Partial<AIModel>) => Promise<void>;
  removeModel: (modelId: string) => Promise<void>;
  updateSystemConfig: (config: Partial<AISystemConfig>) => Promise<void>;
  updateUserPreferences: (userId: string, preferences: Partial<AIUserPreferences>) => Promise<void>;
  getUserPreferences: (userId: string) => AIUserPreferences | undefined;
  cleanup: () => Promise<void>;
  refreshData: () => Promise<void>;
}

// ============================================================================
// HOOK RETURN TYPE
// ============================================================================

type UseAIHook = AIHookState & AIHookActions;

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

/**
 * React hook for AI operations
 * Provides a convenient interface for components to interact with the AI manager
 */
export function useAI(): UseAIHook {
  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================

  const [state, setState] = useState<AIHookState>({
    isInitialized: false,
    isLoading: false,
    error: null,
    models: [],
    activeTasks: [],
    activeExecutions: [],
    recentEvents: [],
    systemConfig: null,
  });

  // ============================================================================
  // MEMOIZED VALUES
  // ============================================================================

  const memoizedState = useMemo(() => state, [state]);

  // ============================================================================
  // STATE UPDATE HELPERS
  // ============================================================================

  const updateState = useCallback((updates: Partial<AIHookState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    updateState({ isLoading: loading });
  }, [updateState]);

  const setError = useCallback((error: string | null) => {
    updateState({ error });
  }, [updateState]);

  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  // ============================================================================
  // DATA REFRESH FUNCTIONS
  // ============================================================================

  const refreshModels = useCallback(async () => {
    try {
      const models = aiManager.getModels();
      updateState({ models });
    } catch (error) {
      console.error('Failed to refresh models:', error);
    }
  }, [updateState]);

  const refreshActiveTasks = useCallback(async () => {
    try {
      const activeTasks = aiManager.getActiveTasks();
      updateState({ activeTasks });
    } catch (error) {
      console.error('Failed to refresh active tasks:', error);
    }
  }, [updateState]);

  const refreshActiveExecutions = useCallback(async () => {
    try {
      const activeExecutions = aiManager.getActiveExecutions();
      updateState({ activeExecutions });
    } catch (error) {
      console.error('Failed to refresh active executions:', error);
    }
  }, [updateState]);

  const refreshRecentEvents = useCallback(async () => {
    try {
      const recentEvents = aiManager.getRecentEvents(50);
      updateState({ recentEvents });
    } catch (error) {
      console.error('Failed to refresh recent events:', error);
    }
  }, [updateState]);

  const refreshSystemConfig = useCallback(async () => {
    try {
      const systemConfig = aiManager.getSystemConfig();
      updateState({ systemConfig });
    } catch (error) {
      console.error('Failed to refresh system config:', error);
    }
  }, [updateState]);

  // ============================================================================
  // CORE AI OPERATIONS
  // ============================================================================

  const initialize = useCallback(async (config?: Partial<AISystemConfig>) => {
    try {
      setLoading(true);
      clearError();

      await aiManager.initialize(config);
      
      // Refresh all data after initialization
      await Promise.all([
        refreshModels(),
        refreshActiveTasks(),
        refreshActiveExecutions(),
        refreshRecentEvents(),
        refreshSystemConfig(),
      ]);

      updateState({ isInitialized: true });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to initialize AI manager';
      setError(errorMessage);
      console.error('AI initialization failed:', error);
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshModels,
    refreshActiveTasks,
    refreshActiveExecutions,
    refreshRecentEvents,
    refreshSystemConfig,
    updateState,
  ]);

  const processRequest = useCallback(async (request: AIRequestUnion): Promise<AIResponseUnion> => {
    try {
      setLoading(true);
      clearError();

      const response = await aiManager.processRequest(request);
      
      // Refresh relevant data
      await Promise.all([
        refreshActiveTasks(),
        refreshRecentEvents(),
      ]);

      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to process AI request';
      setError(errorMessage);
      console.error('AI request processing failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshActiveTasks,
    refreshRecentEvents,
  ]);

  const executeWorkflow = useCallback(async (
    workflowId: string,
    input: Record<string, unknown>,
    userId: string
  ): Promise<string> => {
    try {
      setLoading(true);
      clearError();

      const executionId = await aiManager.executeWorkflow(workflowId, input, userId);
      
      // Refresh relevant data
      await Promise.all([
        refreshActiveExecutions(),
        refreshRecentEvents(),
      ]);

      return executionId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to execute workflow';
      setError(errorMessage);
      console.error('Workflow execution failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshActiveExecutions,
    refreshRecentEvents,
  ]);

  // ============================================================================
  // MODEL MANAGEMENT
  // ============================================================================

  const addModel = useCallback(async (model: Omit<AIModel, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> => {
    try {
      setLoading(true);
      clearError();

      const modelId = await aiManager.addModel(model);
      
      // Refresh models
      await refreshModels();
      
      return modelId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to add model';
      setError(errorMessage);
      console.error('Model addition failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshModels]);

  const updateModel = useCallback(async (modelId: string, updates: Partial<AIModel>): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.updateModel(modelId, updates);
      
      // Refresh models
      await refreshModels();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update model';
      setError(errorMessage);
      console.error('Model update failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshModels]);

  const removeModel = useCallback(async (modelId: string): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.removeModel(modelId);
      
      // Refresh models
      await refreshModels();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to remove model';
      setError(errorMessage);
      console.error('Model removal failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshModels]);

  // ============================================================================
  // CONFIGURATION MANAGEMENT
  // ============================================================================

  const updateSystemConfig = useCallback(async (config: Partial<AISystemConfig>): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.updateSystemConfig(config);
      
      // Refresh system config
      await refreshSystemConfig();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update system configuration';
      setError(errorMessage);
      console.error('System config update failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshSystemConfig]);

  const updateUserPreferences = useCallback(async (
    userId: string,
    preferences: Partial<AIUserPreferences>
  ): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.updateUserPreferences(userId, preferences);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update user preferences';
      setError(errorMessage);
      console.error('User preferences update failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError]);

  const getUserPreferences = useCallback((userId: string): AIUserPreferences | undefined => {
    return aiManager.getUserPreferences(userId);
  }, []);

  // ============================================================================
  // UTILITY OPERATIONS
  // ============================================================================

  const cleanup = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.cleanup();
      
      // Refresh data after cleanup
      await Promise.all([
        refreshActiveTasks(),
        refreshActiveExecutions(),
        refreshRecentEvents(),
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to cleanup';
      setError(errorMessage);
      console.error('Cleanup failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshActiveTasks,
    refreshActiveExecutions,
    refreshRecentEvents,
  ]);

  const refreshData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await Promise.all([
        refreshModels(),
        refreshActiveTasks(),
        refreshActiveExecutions(),
        refreshRecentEvents(),
        refreshSystemConfig(),
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to refresh data';
      setError(errorMessage);
      console.error('Data refresh failed:', error);
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshModels,
    refreshActiveTasks,
    refreshActiveExecutions,
    refreshRecentEvents,
    refreshSystemConfig,
  ]);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Auto-refresh data every 30 seconds when initialized
  useEffect(() => {
    if (!state.isInitialized) return;

    const interval = setInterval(() => {
      refreshData();
    }, 30000);

    return () => clearInterval(interval);
  }, [state.isInitialized, refreshData]);

  // ============================================================================
  // RETURN VALUE
  // ============================================================================

  return {
    ...memoizedState,
    initialize,
    processRequest,
    executeWorkflow,
    addModel,
    updateModel,
    removeModel,
    updateSystemConfig,
    updateUserPreferences,
    getUserPreferences,
    cleanup,
    refreshData,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default useAI;
 * @fileoverview React hook for AI operations
 * @author Blaze AI Team
 */

import { useCallback, useEffect, useState, useMemo } from 'react';
import { aiManager } from '../../lib/ai/ai-manager';
import {
  AIModel,
  AIRequestUnion,
  AIResponseUnion,
  AITask,
  AIWorkflowExecution,
  AIEvent,
  AISystemConfig,
  AIUserPreferences,
} from '../../lib/ai/ai-types';

// ============================================================================
// HOOK STATE INTERFACE
// ============================================================================

interface AIHookState {
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  models: AIModel[];
  activeTasks: AITask[];
  activeExecutions: AIWorkflowExecution[];
  recentEvents: AIEvent[];
  systemConfig: AISystemConfig | null;
}

// ============================================================================
// HOOK ACTIONS INTERFACE
// ============================================================================

interface AIHookActions {
  initialize: (config?: Partial<AISystemConfig>) => Promise<void>;
  processRequest: (request: AIRequestUnion) => Promise<AIResponseUnion>;
  executeWorkflow: (workflowId: string, input: Record<string, unknown>, userId: string) => Promise<string>;
  addModel: (model: Omit<AIModel, 'id' | 'createdAt' | 'updatedAt'>) => Promise<string>;
  updateModel: (modelId: string, updates: Partial<AIModel>) => Promise<void>;
  removeModel: (modelId: string) => Promise<void>;
  updateSystemConfig: (config: Partial<AISystemConfig>) => Promise<void>;
  updateUserPreferences: (userId: string, preferences: Partial<AIUserPreferences>) => Promise<void>;
  getUserPreferences: (userId: string) => AIUserPreferences | undefined;
  cleanup: () => Promise<void>;
  refreshData: () => Promise<void>;
}

// ============================================================================
// HOOK RETURN TYPE
// ============================================================================

type UseAIHook = AIHookState & AIHookActions;

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

/**
 * React hook for AI operations
 * Provides a convenient interface for components to interact with the AI manager
 */
export function useAI(): UseAIHook {
  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================

  const [state, setState] = useState<AIHookState>({
    isInitialized: false,
    isLoading: false,
    error: null,
    models: [],
    activeTasks: [],
    activeExecutions: [],
    recentEvents: [],
    systemConfig: null,
  });

  // ============================================================================
  // MEMOIZED VALUES
  // ============================================================================

  const memoizedState = useMemo(() => state, [state]);

  // ============================================================================
  // STATE UPDATE HELPERS
  // ============================================================================

  const updateState = useCallback((updates: Partial<AIHookState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    updateState({ isLoading: loading });
  }, [updateState]);

  const setError = useCallback((error: string | null) => {
    updateState({ error });
  }, [updateState]);

  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  // ============================================================================
  // DATA REFRESH FUNCTIONS
  // ============================================================================

  const refreshModels = useCallback(async () => {
    try {
      const models = aiManager.getModels();
      updateState({ models });
    } catch (error) {
      console.error('Failed to refresh models:', error);
    }
  }, [updateState]);

  const refreshActiveTasks = useCallback(async () => {
    try {
      const activeTasks = aiManager.getActiveTasks();
      updateState({ activeTasks });
    } catch (error) {
      console.error('Failed to refresh active tasks:', error);
    }
  }, [updateState]);

  const refreshActiveExecutions = useCallback(async () => {
    try {
      const activeExecutions = aiManager.getActiveExecutions();
      updateState({ activeExecutions });
    } catch (error) {
      console.error('Failed to refresh active executions:', error);
    }
  }, [updateState]);

  const refreshRecentEvents = useCallback(async () => {
    try {
      const recentEvents = aiManager.getRecentEvents(50);
      updateState({ recentEvents });
    } catch (error) {
      console.error('Failed to refresh recent events:', error);
    }
  }, [updateState]);

  const refreshSystemConfig = useCallback(async () => {
    try {
      const systemConfig = aiManager.getSystemConfig();
      updateState({ systemConfig });
    } catch (error) {
      console.error('Failed to refresh system config:', error);
    }
  }, [updateState]);

  // ============================================================================
  // CORE AI OPERATIONS
  // ============================================================================

  const initialize = useCallback(async (config?: Partial<AISystemConfig>) => {
    try {
      setLoading(true);
      clearError();

      await aiManager.initialize(config);
      
      // Refresh all data after initialization
      await Promise.all([
        refreshModels(),
        refreshActiveTasks(),
        refreshActiveExecutions(),
        refreshRecentEvents(),
        refreshSystemConfig(),
      ]);

      updateState({ isInitialized: true });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to initialize AI manager';
      setError(errorMessage);
      console.error('AI initialization failed:', error);
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshModels,
    refreshActiveTasks,
    refreshActiveExecutions,
    refreshRecentEvents,
    refreshSystemConfig,
    updateState,
  ]);

  const processRequest = useCallback(async (request: AIRequestUnion): Promise<AIResponseUnion> => {
    try {
      setLoading(true);
      clearError();

      const response = await aiManager.processRequest(request);
      
      // Refresh relevant data
      await Promise.all([
        refreshActiveTasks(),
        refreshRecentEvents(),
      ]);

      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to process AI request';
      setError(errorMessage);
      console.error('AI request processing failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshActiveTasks,
    refreshRecentEvents,
  ]);

  const executeWorkflow = useCallback(async (
    workflowId: string,
    input: Record<string, unknown>,
    userId: string
  ): Promise<string> => {
    try {
      setLoading(true);
      clearError();

      const executionId = await aiManager.executeWorkflow(workflowId, input, userId);
      
      // Refresh relevant data
      await Promise.all([
        refreshActiveExecutions(),
        refreshRecentEvents(),
      ]);

      return executionId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to execute workflow';
      setError(errorMessage);
      console.error('Workflow execution failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshActiveExecutions,
    refreshRecentEvents,
  ]);

  // ============================================================================
  // MODEL MANAGEMENT
  // ============================================================================

  const addModel = useCallback(async (model: Omit<AIModel, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> => {
    try {
      setLoading(true);
      clearError();

      const modelId = await aiManager.addModel(model);
      
      // Refresh models
      await refreshModels();
      
      return modelId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to add model';
      setError(errorMessage);
      console.error('Model addition failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshModels]);

  const updateModel = useCallback(async (modelId: string, updates: Partial<AIModel>): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.updateModel(modelId, updates);
      
      // Refresh models
      await refreshModels();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update model';
      setError(errorMessage);
      console.error('Model update failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshModels]);

  const removeModel = useCallback(async (modelId: string): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.removeModel(modelId);
      
      // Refresh models
      await refreshModels();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to remove model';
      setError(errorMessage);
      console.error('Model removal failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshModels]);

  // ============================================================================
  // CONFIGURATION MANAGEMENT
  // ============================================================================

  const updateSystemConfig = useCallback(async (config: Partial<AISystemConfig>): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.updateSystemConfig(config);
      
      // Refresh system config
      await refreshSystemConfig();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update system configuration';
      setError(errorMessage);
      console.error('System config update failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, refreshSystemConfig]);

  const updateUserPreferences = useCallback(async (
    userId: string,
    preferences: Partial<AIUserPreferences>
  ): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.updateUserPreferences(userId, preferences);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update user preferences';
      setError(errorMessage);
      console.error('User preferences update failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError]);

  const getUserPreferences = useCallback((userId: string): AIUserPreferences | undefined => {
    return aiManager.getUserPreferences(userId);
  }, []);

  // ============================================================================
  // UTILITY OPERATIONS
  // ============================================================================

  const cleanup = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await aiManager.cleanup();
      
      // Refresh data after cleanup
      await Promise.all([
        refreshActiveTasks(),
        refreshActiveExecutions(),
        refreshRecentEvents(),
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to cleanup';
      setError(errorMessage);
      console.error('Cleanup failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshActiveTasks,
    refreshActiveExecutions,
    refreshRecentEvents,
  ]);

  const refreshData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      clearError();

      await Promise.all([
        refreshModels(),
        refreshActiveTasks(),
        refreshActiveExecutions(),
        refreshRecentEvents(),
        refreshSystemConfig(),
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to refresh data';
      setError(errorMessage);
      console.error('Data refresh failed:', error);
    } finally {
      setLoading(false);
    }
  }, [
    setLoading,
    clearError,
    refreshModels,
    refreshActiveTasks,
    refreshActiveExecutions,
    refreshRecentEvents,
    refreshSystemConfig,
  ]);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Auto-refresh data every 30 seconds when initialized
  useEffect(() => {
    if (!state.isInitialized) return;

    const interval = setInterval(() => {
      refreshData();
    }, 30000);

    return () => clearInterval(interval);
  }, [state.isInitialized, refreshData]);

  // ============================================================================
  // RETURN VALUE
  // ============================================================================

  return {
    ...memoizedState,
    initialize,
    processRequest,
    executeWorkflow,
    addModel,
    updateModel,
    removeModel,
    updateSystemConfig,
    updateUserPreferences,
    getUserPreferences,
    cleanup,
    refreshData,
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default useAI;


