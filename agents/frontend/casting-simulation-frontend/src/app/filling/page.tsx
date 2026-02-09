'use client';

import { useState } from 'react';
import { SimulationPageLayout } from '@/components/layout/SimulationPageLayout';
import { FillingForm } from '@/components/forms/SimulationForms';
import { TemperatureChart } from '@/components/visualizations/Charts';
import { MetricCard, RecommendationCard } from '@/components/cards/ResultCard';
import { useFillingSimulation } from '@/services/hooks/useSimulation';
import { Clock, Gauge, Thermometer } from 'lucide-react';
import type { FillingRequest } from '@/types';

export default function FillingPage() {
    const { run, isLoading, result, error } = useFillingSimulation();
    const [hasRun, setHasRun] = useState(false);

    const handleSubmit = async (data: FillingRequest) => {
        setHasRun(true);
        await run(data);
    };

    // Extract result data
    const fillingData = result?.data as {
        fill_time?: number;
        max_velocity?: number;
        min_temperature?: number;
        fill_percentage?: number;
        defects_detected?: string[];
    } | undefined;

    const results = result ? (
        <>
            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <MetricCard
                    label="Fill Time"
                    value={fillingData?.fill_time?.toFixed(1) || '0'}
                    unit="seconds"
                    icon={<Clock size={24} />}
                    color="var(--accent-cyan)"
                />
                <MetricCard
                    label="Max Velocity"
                    value={fillingData?.max_velocity?.toFixed(2) || '0'}
                    unit="m/s"
                    icon={<Gauge size={24} />}
                    color="var(--accent-blue)"
                />
            </div>

            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <MetricCard
                    label="Min Temperature"
                    value={fillingData?.min_temperature?.toFixed(0) || '0'}
                    unit="°C"
                    icon={<Thermometer size={24} />}
                    color="var(--accent-orange)"
                />
                <MetricCard
                    label="Fill Percentage"
                    value={fillingData?.fill_percentage?.toFixed(1) || '100'}
                    unit="%"
                    color="var(--accent-green)"
                />
            </div>

            <TemperatureChart title="Temperature Evolution During Fill" />

            {fillingData?.defects_detected && fillingData.defects_detected.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                    <RecommendationCard
                        title="Detected Issues"
                        recommendations={fillingData.defects_detected}
                        severity="warning"
                    />
                </div>
            )}

            {result.success && (
                <div style={{ marginTop: '24px' }}>
                    <RecommendationCard
                        title="Optimization Suggestions"
                        recommendations={[
                            'Use bottom gating for reduced turbulence',
                            'Add filter in runner for oxide removal',
                            'Consider increasing pouring temperature by 10-20°C',
                        ]}
                        severity="info"
                    />
                </div>
            )}
        </>
    ) : null;

    return (
        <SimulationPageLayout
            title="EULER - Filling Simulation"
            subtitle="Mold filling simulation with temperature and velocity tracking"
            form={<FillingForm onSubmit={handleSubmit} isLoading={isLoading} />}
            results={results}
            error={error}
            isLoading={isLoading}
            hasRun={hasRun}
            emptyStateIcon={Thermometer}
            emptyStateMessage="No Simulation Results"
            emptyStateDescription="Configure the parameters on the left and run a filling simulation to see results here."
            loadingMessage="Running Simulation"
            loadingDescription="Calculating metal flow and temperature distribution..."
        />
    );
}
