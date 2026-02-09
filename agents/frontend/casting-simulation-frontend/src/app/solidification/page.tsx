'use client';

import { useState } from 'react';
import { SimulationPageLayout } from '@/components/layout/SimulationPageLayout';
import { SolidificationForm } from '@/components/forms/SimulationForms';
import { TemperatureChart } from '@/components/visualizations/Charts';
import { MetricCard, RecommendationCard } from '@/components/cards/ResultCard';
import { useSolidificationSimulation } from '@/services/hooks/useSimulation';
import { Clock, Snowflake, Flame } from 'lucide-react';
import type { SolidificationRequest } from '@/types';

export default function SolidificationPage() {
    const { run, isLoading, result, error } = useSolidificationSimulation();
    const [hasRun, setHasRun] = useState(false);

    const handleSubmit = async (data: SolidificationRequest) => {
        setHasRun(true);
        await run(data);
    };

    const solidData = result?.data as {
        total_time?: number;
        hot_spots?: Array<{ location: string; severity: string }>;
        shrinkage_cavities?: Array<{ location: string; volume_fraction: number }>;
        last_to_freeze?: { location: string; time: number };
    } | undefined;

    const results = result ? (
        <>
            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <MetricCard
                    label="Total Solidification Time"
                    value={solidData?.total_time?.toFixed(1) || '0'}
                    unit="seconds"
                    icon={<Clock size={24} />}
                    color="var(--accent-purple)"
                />
                <MetricCard
                    label="Hot Spots Detected"
                    value={solidData?.hot_spots?.length || 0}
                    icon={<Flame size={24} />}
                    color="var(--accent-orange)"
                />
            </div>

            <TemperatureChart title="Solidification Progress" />

            {solidData?.hot_spots && solidData.hot_spots.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                    <RecommendationCard
                        title="Hot Spot Analysis"
                        recommendations={solidData.hot_spots.map(
                            hs => `${hs.location}: ${hs.severity} severity`
                        )}
                        severity="warning"
                    />
                </div>
            )}

            <div style={{ marginTop: '24px' }}>
                <RecommendationCard
                    title="Optimization Suggestions"
                    recommendations={[
                        'Add chill at hot spot locations',
                        'Optimize riser placement for better feeding',
                        'Consider modifying section thickness',
                    ]}
                    severity="info"
                />
            </div>
        </>
    ) : null;

    return (
        <SimulationPageLayout
            title="FOURIER - Solidification"
            subtitle="Thermal simulation with porosity and hot spot prediction"
            form={<SolidificationForm onSubmit={handleSubmit} isLoading={isLoading} />}
            results={results}
            error={error}
            isLoading={isLoading}
            hasRun={hasRun}
            emptyStateIcon={Snowflake}
            emptyStateMessage="No Simulation Results"
            emptyStateDescription="Configure the parameters and run a solidification simulation."
            loadingMessage="Running Simulation"
            loadingDescription="Calculating thermal fields and solidification fronts..."
        />
    );
}
