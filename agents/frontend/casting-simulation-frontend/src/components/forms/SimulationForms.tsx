'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Play, Loader2 } from 'lucide-react';
import { MATERIALS, MOLD_MATERIALS } from '@/types';

// ========== Filling Form ==========

const fillingSchema = z.object({
    material: z.string().min(1, 'Select a material'),
    pouring_temperature: z.number().min(300).max(2000),
    mold_temperature: z.number().min(20).max(500),
    pouring_rate: z.number().min(0.1).max(100).optional(),
});

type FillingFormData = z.infer<typeof fillingSchema>;

interface FillingFormProps {
    onSubmit: (data: FillingFormData) => void;
    isLoading?: boolean;
}

export function FillingForm({ onSubmit, isLoading }: FillingFormProps) {
    const { register, handleSubmit, formState: { errors } } = useForm<FillingFormData>({
        resolver: zodResolver(fillingSchema),
        defaultValues: {
            material: 'aluminum_A356',
            pouring_temperature: 720,
            mold_temperature: 200,
            pouring_rate: 5,
        },
    });

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <div className="form-group">
                <label className="form-label">Material</label>
                <select {...register('material')} className="form-input form-select">
                    {Object.entries(MATERIALS).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                    ))}
                </select>
                {errors.material && (
                    <span style={{ color: 'var(--accent-red)', fontSize: '12px' }}>
                        {errors.material.message}
                    </span>
                )}
            </div>

            <div className="grid-2">
                <div className="form-group">
                    <label className="form-label">Pouring Temperature (°C)</label>
                    <input
                        type="number"
                        {...register('pouring_temperature', { valueAsNumber: true })}
                        className="form-input"
                    />
                    {errors.pouring_temperature && (
                        <span style={{ color: 'var(--accent-red)', fontSize: '12px' }}>
                            {errors.pouring_temperature.message}
                        </span>
                    )}
                </div>

                <div className="form-group">
                    <label className="form-label">Mold Temperature (°C)</label>
                    <input
                        type="number"
                        {...register('mold_temperature', { valueAsNumber: true })}
                        className="form-input"
                    />
                    {errors.mold_temperature && (
                        <span style={{ color: 'var(--accent-red)', fontSize: '12px' }}>
                            {errors.mold_temperature.message}
                        </span>
                    )}
                </div>
            </div>

            <div className="form-group">
                <label className="form-label">Pouring Rate (kg/s)</label>
                <input
                    type="number"
                    step="0.1"
                    {...register('pouring_rate', { valueAsNumber: true })}
                    className="form-input"
                />
            </div>

            <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '16px' }}
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <Loader2 size={18} className="spinner" style={{ animation: 'spin 0.8s linear infinite' }} />
                        Running Simulation...
                    </>
                ) : (
                    <>
                        <Play size={18} />
                        Run Filling Simulation
                    </>
                )}
            </button>
        </form>
    );
}

// ========== Solidification Form ==========

const solidificationSchema = z.object({
    material: z.string().min(1),
    mold_material: z.string().min(1),
    initial_temp: z.number().min(300).max(2000),
    ambient_temp: z.number().min(0).max(100),
});

type SolidificationFormData = z.infer<typeof solidificationSchema>;

interface SolidificationFormProps {
    onSubmit: (data: SolidificationFormData) => void;
    isLoading?: boolean;
}

export function SolidificationForm({ onSubmit, isLoading }: SolidificationFormProps) {
    const { register, handleSubmit, formState: { errors } } = useForm<SolidificationFormData>({
        resolver: zodResolver(solidificationSchema),
        defaultValues: {
            material: 'aluminum_A356',
            mold_material: 'sand',
            initial_temp: 720,
            ambient_temp: 25,
        },
    });

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <div className="grid-2">
                <div className="form-group">
                    <label className="form-label">Metal Material</label>
                    <select {...register('material')} className="form-input form-select">
                        {Object.entries(MATERIALS).map(([value, label]) => (
                            <option key={value} value={value}>{label}</option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Mold Material</label>
                    <select {...register('mold_material')} className="form-input form-select">
                        {Object.entries(MOLD_MATERIALS).map(([value, label]) => (
                            <option key={value} value={value}>{label}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="grid-2">
                <div className="form-group">
                    <label className="form-label">Initial Temperature (°C)</label>
                    <input
                        type="number"
                        {...register('initial_temp', { valueAsNumber: true })}
                        className="form-input"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Ambient Temperature (°C)</label>
                    <input
                        type="number"
                        {...register('ambient_temp', { valueAsNumber: true })}
                        className="form-input"
                    />
                </div>
            </div>

            <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '16px' }}
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <Loader2 size={18} style={{ animation: 'spin 0.8s linear infinite' }} />
                        Running Simulation...
                    </>
                ) : (
                    <>
                        <Play size={18} />
                        Run Solidification Simulation
                    </>
                )}
            </button>
        </form>
    );
}

// ========== Stress Form ==========

const stressSchema = z.object({
    material: z.string().min(1),
});

type StressFormData = z.infer<typeof stressSchema>;

interface StressFormProps {
    onSubmit: (data: StressFormData) => void;
    isLoading?: boolean;
}

export function StressForm({ onSubmit, isLoading }: StressFormProps) {
    const { register, handleSubmit } = useForm<StressFormData>({
        resolver: zodResolver(stressSchema),
        defaultValues: {
            material: 'aluminum_A356',
        },
    });

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <div className="form-group">
                <label className="form-label">Material</label>
                <select {...register('material')} className="form-input form-select">
                    {Object.entries(MATERIALS).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                    ))}
                </select>
            </div>

            <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '16px' }}
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <Loader2 size={18} style={{ animation: 'spin 0.8s linear infinite' }} />
                        Analyzing...
                    </>
                ) : (
                    <>
                        <Play size={18} />
                        Run Stress Analysis
                    </>
                )}
            </button>
        </form>
    );
}

// ========== Mesh Form ==========

const meshSchema = z.object({
    model_format: z.string(),
    mesh_density: z.string(),
    element_type: z.string(),
});

type MeshFormData = z.infer<typeof meshSchema>;

interface MeshFormProps {
    onSubmit: (data: MeshFormData) => void;
    isLoading?: boolean;
}

export function MeshForm({ onSubmit, isLoading }: MeshFormProps) {
    const { register, handleSubmit } = useForm<MeshFormData>({
        resolver: zodResolver(meshSchema),
        defaultValues: {
            model_format: 'STEP',
            mesh_density: 'adaptive',
            element_type: 'tetrahedral',
        },
    });

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <div className="form-group">
                <label className="form-label">CAD Format</label>
                <select {...register('model_format')} className="form-input form-select">
                    <option value="STEP">STEP</option>
                    <option value="IGES">IGES</option>
                </select>
            </div>

            <div className="grid-2">
                <div className="form-group">
                    <label className="form-label">Mesh Density</label>
                    <select {...register('mesh_density')} className="form-input form-select">
                        <option value="coarse">Coarse</option>
                        <option value="medium">Medium</option>
                        <option value="fine">Fine</option>
                        <option value="adaptive">Adaptive</option>
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Element Type</label>
                    <select {...register('element_type')} className="form-input form-select">
                        <option value="tetrahedral">Tetrahedral</option>
                        <option value="prismatic">Prismatic</option>
                        <option value="hybrid">Hybrid</option>
                    </select>
                </div>
            </div>

            <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '16px' }}
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <Loader2 size={18} style={{ animation: 'spin 0.8s linear infinite' }} />
                        Generating Mesh...
                    </>
                ) : (
                    <>
                        <Play size={18} />
                        Generate Mesh
                    </>
                )}
            </button>
        </form>
    );
}
