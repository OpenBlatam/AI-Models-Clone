/**
 * API Client for Casting Simulation Backend
 */

import type {
    MeshRequest,
    FillingRequest,
    SolidificationRequest,
    StressRequest,
    StructureRequest,
    HeatTreatmentRequest,
    MirageRequest,
    CriterionRequest,
    MasterRequest,
    TaskResponse,
    TaskStatusResponse,
    SimulationResponse,
    HealthResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1/simulation';

class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function request<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new ApiError(response.status, error.detail || 'Request failed');
    }

    return response.json();
}

// ========== Health Check ==========

export async function checkHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/health');
}

// ========== Mesh Analysis ==========

export async function runMeshAnalysis(data: MeshRequest): Promise<SimulationResponse> {
    return request<SimulationResponse>('/mesh', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function createMeshTask(data: MeshRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/mesh/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Configuration (MASTER) ==========

export async function configureSimulation(data: MasterRequest): Promise<SimulationResponse> {
    return request<SimulationResponse>('/config', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Filling Simulation (EULER) ==========

export async function runFillingSimulation(data: FillingRequest): Promise<SimulationResponse> {
    return request<SimulationResponse>('/filling', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function createFillingTask(data: FillingRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/filling/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Solidification Simulation (FOURIER) ==========

export async function runSolidificationSimulation(data: SolidificationRequest): Promise<SimulationResponse> {
    return request<SimulationResponse>('/solidification', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function createSolidificationTask(data: SolidificationRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/solidification/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Stress Analysis (HOOKE) ==========

export async function runStressAnalysis(data: StressRequest): Promise<SimulationResponse> {
    return request<SimulationResponse>('/stress', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function createStressTask(data: StressRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/stress/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Heat Treatment ==========

export async function runHeatTreatment(data: HeatTreatmentRequest): Promise<SimulationResponse> {
    return request<SimulationResponse>('/heat-treatment', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function createHeatTreatmentTask(data: HeatTreatmentRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/heat-treatment/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Structure Analysis ==========

export async function createStructureTask(data: StructureRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/structure/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Visualization (MIRAGE) ==========

export async function createVisualizationTask(data: MirageRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/visualize/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Criterial Analysis (CRITERION) ==========

export async function createCriterionTask(data: CriterionRequest): Promise<TaskResponse> {
    return request<TaskResponse>('/criterion/task', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// ========== Task Status ==========

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    return request<TaskStatusResponse>(`/task/${taskId}`);
}

export async function getTaskResult(taskId: string): Promise<SimulationResponse> {
    return request<SimulationResponse>(`/task/${taskId}/result`);
}

// ========== Task Polling ==========

export async function pollTaskUntilComplete(
    taskId: string,
    onUpdate?: (status: TaskStatusResponse) => void,
    maxAttempts: number = 60,
    intervalMs: number = 2000
): Promise<SimulationResponse> {
    let attempts = 0;

    while (attempts < maxAttempts) {
        const status = await getTaskStatus(taskId);
        onUpdate?.(status);

        if (status.status === 'completed') {
            return getTaskResult(taskId);
        }

        if (status.status === 'failed') {
            throw new Error('Task failed');
        }

        await new Promise(resolve => setTimeout(resolve, intervalMs));
        attempts++;
    }

    throw new Error('Task polling timeout');
}

export { ApiError };
