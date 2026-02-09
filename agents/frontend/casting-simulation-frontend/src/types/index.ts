/**
 * TypeScript types for Casting Simulation API
 * Mirrors backend schemas from casting_simulation_ai
 */

// ========== Request Types ==========

export interface MeshRequest {
    model_format?: string;
    mesh_density?: string;
    element_type?: string;
    critical_zones?: string[];
}

export interface MasterRequest {
    process_type?: string;
    material?: string;
    mold_material?: string;
    parameters?: Record<string, unknown>;
}

export interface FillingRequest {
    material?: string;
    pouring_temperature?: number;
    mold_temperature?: number;
    pouring_rate?: number;
    gate_design?: Record<string, unknown>;
}

export interface SolidificationRequest {
    material?: string;
    mold_material?: string;
    initial_temp?: number;
    ambient_temp?: number;
    cooling_conditions?: Record<string, unknown>;
}

export interface StressRequest {
    material?: string;
    process_conditions?: Record<string, unknown>;
    constraints?: Record<string, unknown>;
}

export interface StructureRequest {
    material?: string;
    chemical_composition?: Record<string, number>;
    cooling_rate?: number;
    nucleation_params?: Record<string, unknown>;
}

export interface HeatTreatmentRequest {
    material?: string;
    treatment_type?: string;
    temperature_profile?: Record<string, unknown>;
    target_properties?: Record<string, unknown>;
}

export interface MirageRequest {
    analysis_type?: string;
    data_description?: string;
    visualization_options?: Record<string, unknown>;
}

export interface CriterionRequest {
    criterion_type?: string;
    simulation_data?: Record<string, unknown>;
    thresholds?: Record<string, number>;
}

// ========== Response Types ==========

export interface TaskResponse {
    task_id: string;
    status: string;
    message: string;
}

export interface TaskStatusResponse {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    created_at?: string;
    started_at?: string;
    completed_at?: string;
}

export interface SimulationResponse {
    success: boolean;
    data: Record<string, unknown>;
    tokens_used: number;
    model: string;
    timestamp?: string;
    error?: string;
}

export interface HealthResponse {
    status: string;
    version: string;
    modules: string[];
}

// ========== Result Types ==========

export interface MeshResult {
    num_nodes: number;
    num_elements: number;
    element_type: string;
    quality_score: number;
    max_aspect_ratio: number;
    max_skewness: number;
    warnings: string[];
}

export interface QualityReport {
    overall_score: number;
    aspect_ratio_score: number;
    skewness_score: number;
    orthogonality_score: number;
    issues: string[];
    recommendations: string[];
}

export interface FillingResult {
    fill_time: number;
    max_velocity: number;
    min_temperature: number;
    fill_percentage: number;
    defects_detected: string[];
    hot_spots: HotSpot[];
}

export interface HotSpot {
    location: string;
    temperature?: number;
    size_mm?: number;
    severity?: string;
}

export interface VelocityAnalysis {
    max_velocity: number;
    avg_velocity: number;
    turbulent_zones: Zone[];
    stagnation_zones: Zone[];
}

export interface Zone {
    location: string;
    intensity?: string;
    risk?: string;
}

export interface SolidificationResult {
    total_time: number;
    hot_spots: HotSpot[];
    shrinkage_cavities: ShrinkageCavity[];
    porosity_zones: PorosityZone[];
    last_to_freeze: {
        location: string;
        time: number;
    };
}

export interface ShrinkageCavity {
    location: string;
    volume_fraction: number;
    type: string;
}

export interface PorosityZone {
    location: string;
    estimated_size_mm?: number;
    estimated_fraction?: number;
    type: string;
}

export interface PorosityPrediction {
    macro_porosity_zones: PorosityZone[];
    micro_porosity_zones: PorosityZone[];
    total_porosity_volume: number;
    quality_grade: string;
}

export interface StressResult {
    max_principal_stress: number;
    max_von_mises: number;
    max_displacement: number;
    safety_factor: number;
    crack_risk_zones: CrackRiskZone[];
}

export interface CrackRiskZone {
    location: string;
    stress: number;
    risk: string;
}

export interface WarpingPrediction {
    max_warping_mm: number;
    warping_x: number;
    warping_y: number;
    warping_z: number;
    affected_zones: string[];
}

export interface CrackPrediction {
    hot_tear_risk: CrackRisk[];
    cold_crack_risk: CrackRisk[];
    overall_risk: string;
    recommendations: string[];
}

export interface CrackRisk {
    location: string;
    stress_ratio: number;
    risk: string;
}

// ========== Material Types ==========

export const MATERIALS = {
    aluminum_A356: 'Aluminum A356',
    cast_iron: 'Cast Iron',
    steel_1045: 'Steel 1045',
} as const;

export const MOLD_MATERIALS = {
    sand: 'Sand',
    steel: 'Steel Die',
    ceramic: 'Ceramic',
} as const;

export const ELEMENT_TYPES = {
    tetrahedral: 'Tetrahedral',
    prismatic: 'Prismatic',
    hybrid: 'Hybrid',
} as const;

export const MESH_DENSITIES = {
    coarse: 'Coarse',
    medium: 'Medium',
    fine: 'Fine',
    adaptive: 'Adaptive',
} as const;

export const TREATMENT_TYPES = {
    quenching: 'Quenching',
    tempering: 'Tempering',
    annealing: 'Annealing',
    normalizing: 'Normalizing',
} as const;

// ========== Simulation Module Info ==========

export interface SimulationModule {
    id: string;
    name: string;
    description: string;
    icon: string;
    color: string;
    path: string;
}

export const SIMULATION_MODULES: SimulationModule[] = [
    {
        id: 'mesh',
        name: 'MESH',
        description: 'Finite element mesh generation and analysis',
        icon: 'Grid3X3',
        color: '#3B82F6',
        path: '/mesh',
    },
    {
        id: 'filling',
        name: 'EULER',
        description: 'Mold filling simulation',
        icon: 'Droplets',
        color: '#06B6D4',
        path: '/filling',
    },
    {
        id: 'solidification',
        name: 'FOURIER',
        description: 'Solidification and porosity analysis',
        icon: 'Snowflake',
        color: '#8B5CF6',
        path: '/solidification',
    },
    {
        id: 'stress',
        name: 'HOOKE',
        description: 'Stress and deformation analysis',
        icon: 'Zap',
        color: '#F59E0B',
        path: '/stress',
    },
    {
        id: 'structure',
        name: 'STRUCTURE',
        description: 'Grain structure analysis',
        icon: 'Microscope',
        color: '#10B981',
        path: '/structure',
    },
    {
        id: 'heat-treatment',
        name: 'HEAT TREATMENT',
        description: 'Heat treatment simulation',
        icon: 'Flame',
        color: '#EF4444',
        path: '/heat-treatment',
    },
];
