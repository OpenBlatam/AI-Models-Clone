'use client';

import { useState } from 'react';
import { SimulationPageLayout } from '@/components/layout/SimulationPageLayout';
import { StressForm } from '@/components/forms/SimulationForms';
import { StressChart } from '@/components/visualizations/Charts';
import { MetricCard, RecommendationCard } from '@/components/cards/ResultCard';
import { useStressSimulation } from '@/services/hooks/useSimulation';
import { Zap, Shield, Move } from 'lucide-react';
import type { StressRequest } from '@/types';

export default function StressPage() {
    const { run, isLoading, result, error } = useStressSimulation();
    const [hasRun, setHasRun] = useState(false);

    const handleSubmit = async (data: StressRequest) => {
        setHasRun(true);
        await run(data);
    };

    const stressData = result?.data as {
        max_principal_stress?: number;
        max_von_mises?: number;
        max_displacement?: number;
        safety_factor?: number;
        crack_risk_zones?: Array<{ location: string; risk: string }>;
    } | undefined;

    const safetyFactor = stressData?.safety_factor || 2.0;
    const isSafe = safetyFactor > 1.5;

    const results = result ? (
        <>
            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <MetricCard
                    label="Max Von Mises Stress"
                    value={stressData?.max_von_mises?.toFixed(1) || '0'}
                    unit="MPa"
                    icon={<Zap size={24} />}
                    color="var(--accent-orange)"
                />
                <MetricCard
                    label="Safety Factor"
                    value={safetyFactor.toFixed(2)}
                    icon={<Shield size={24} />}
                    color={isSafe ? 'var(--accent-green)' : 'var(--accent-red)'}
                />
            </div>

            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <MetricCard
                    label="Principal Stress"
                    value={stressData?.max_principal_stress?.toFixed(1) || '0'}
                    unit="MPa"
                    color="var(--accent-purple)"
                />
                <MetricCard
                    label="Max Displacement"
                    value={stressData?.max_displacement?.toFixed(3) || '0'}
                    unit="mm"
                    icon={<Move size={24} />}
                    color="var(--accent-cyan)"
                />
            </div>

            <StressChart
                maxStress={stressData?.max_von_mises || 85}
                yieldStrength={170}
                safetyFactor={safetyFactor}
            />

            {stressData?.crack_risk_zones && stressData.crack_risk_zones.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                    <RecommendationCard
                        title="Crack Risk Zones"
                        recommendations={stressData.crack_risk_zones.map(
                            zone => `${zone.location}: ${zone.risk} risk`
                        )}
                        severity="error"
                    />
                </div>
            )}

            <div style={{ marginTop: '24px' }}>
                <RecommendationCard
                    title="Recommendations"
                    recommendations={[
                        isSafe
                            ? 'Safety factor is acceptable for most applications'
                            : 'Consider stress relief heat treatment',
                        'Monitor critical zones during cooling',
                        'Verify constraints and boundary conditions',
                    ]}
                    severity={isSafe ? 'info' : 'warning'}
                />
            </div>
        </>
    ) : null;

    return (
        <SimulationPageLayout
            title="HOOKE - Stress Analysis"
            subtitle="Residual stress, deformation, and crack prediction"
            form={<StressForm onSubmit={handleSubmit} isLoading={isLoading} />}
            results={results}
            error={error}
            isLoading={isLoading}
            hasRun={hasRun}
            emptyStateIcon={Zap}
            emptyStateMessage="No Analysis Results"
            emptyStateDescription="Run a stress analysis to see mechanical stress and deformation predictions."
            loadingMessage="Running Analysis"
            loadingDescription="Calculating residual stresses and deformations..."
        />
    );
}
