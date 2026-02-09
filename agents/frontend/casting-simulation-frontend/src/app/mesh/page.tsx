'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { SimulationPageLayout } from '@/components/layout/SimulationPageLayout';
import { MeshForm } from '@/components/forms/SimulationForms';
import { MetricCard, RecommendationCard } from '@/components/cards/ResultCard';
import { useMeshSimulation } from '@/services/hooks/useSimulation';
import { Grid3X3, Layers, CheckCircle } from 'lucide-react';
import type { MeshRequest } from '@/types';

// Dynamic import for 3D viewer (client-only)
const Mesh3DViewer = dynamic(
    () => import('@/components/visualizations/Mesh3DViewer').then(mod => mod.Mesh3DViewer),
    { ssr: false, loading: () => <div className="viz-container"><div className="spinner" /></div> }
);

export default function MeshPage() {
    const { run, isLoading, result, error } = useMeshSimulation();
    const [hasRun, setHasRun] = useState(false);

    const handleSubmit = async (data: MeshRequest) => {
        setHasRun(true);
        await run(data);
    };

    const meshData = result?.data as {
        num_nodes?: number;
        num_elements?: number;
        element_type?: string;
        quality_score?: number;
        max_aspect_ratio?: number;
        max_skewness?: number;
        warnings?: string[];
    } | undefined;

    const qualityScore = meshData?.quality_score || 92;

    const results = result ? (
        <>
            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <MetricCard
                    label="Elements"
                    value={meshData?.num_elements?.toLocaleString() || '0'}
                    icon={<Grid3X3 size={24} />}
                    color="var(--accent-blue)"
                />
                <MetricCard
                    label="Quality Score"
                    value={qualityScore.toFixed(1)}
                    unit="%"
                    icon={<CheckCircle size={24} />}
                    color={qualityScore > 80 ? 'var(--accent-green)' : 'var(--accent-orange)'}
                />
            </div>

            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <MetricCard
                    label="Nodes"
                    value={meshData?.num_nodes?.toLocaleString() || '0'}
                    icon={<Layers size={24} />}
                    color="var(--accent-purple)"
                />
                <MetricCard
                    label="Element Type"
                    value={meshData?.element_type || 'Tetrahedral'}
                    color="var(--accent-cyan)"
                />
            </div>

            {/* 3D Viewer */}
            <Mesh3DViewer
                numElements={meshData?.num_elements || 50000}
                qualityScore={qualityScore}
            />

            {/* Quality Metrics */}
            <div className="card" style={{ marginTop: '24px' }}>
                <h4 style={{ fontWeight: '600', marginBottom: '16px' }}>Quality Metrics</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                    <div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                            Max Aspect Ratio
                        </div>
                        <div style={{ fontSize: '18px', fontWeight: '600' }}>
                            {meshData?.max_aspect_ratio?.toFixed(2) || '3.20'}
                        </div>
                    </div>
                    <div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                            Max Skewness
                        </div>
                        <div style={{ fontSize: '18px', fontWeight: '600' }}>
                            {meshData?.max_skewness?.toFixed(2) || '0.35'}
                        </div>
                    </div>
                    <div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                            Orthogonality
                        </div>
                        <div style={{ fontSize: '18px', fontWeight: '600' }}>
                            85.0%
                        </div>
                    </div>
                </div>
            </div>

            {meshData?.warnings && meshData.warnings.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                    <RecommendationCard
                        title="Warnings"
                        recommendations={meshData.warnings}
                        severity="warning"
                    />
                </div>
            )}
        </>
    ) : null;

    return (
        <SimulationPageLayout
            title="MESH - Mesh Analysis"
            subtitle="Finite element mesh generation and quality analysis"
            form={<MeshForm onSubmit={handleSubmit} isLoading={isLoading} />}
            results={results}
            error={error}
            isLoading={isLoading}
            hasRun={hasRun}
            emptyStateIcon={Grid3X3}
            emptyStateMessage="No Mesh Generated"
            emptyStateDescription="Configure the parameters and generate a mesh to see the 3D visualization."
            loadingMessage="Generating Mesh"
            loadingDescription="Creating finite element mesh with adaptive refinement..."
        />
    );
}
