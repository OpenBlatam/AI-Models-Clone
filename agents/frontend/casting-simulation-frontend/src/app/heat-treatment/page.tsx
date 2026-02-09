'use client';

import { PageHeader } from '@/components/layout/Header';
import { Flame } from 'lucide-react';

export default function HeatTreatmentPage() {
    return (
        <>
            <PageHeader
                title="HEAT TREATMENT"
                subtitle="Heat treatment and property prediction"
            />

            <div className="page-content">
                <div className="card" style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '500px',
                    textAlign: 'center',
                }}>
                    <div>
                        <div style={{
                            width: '100px',
                            height: '100px',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 24px',
                            boxShadow: '0 0 40px rgba(239, 68, 68, 0.3)',
                        }}>
                            <Flame size={48} style={{ color: 'white' }} />
                        </div>
                        <h2 style={{ fontSize: '24px', marginBottom: '12px' }}>
                            Heat Treatment Simulation
                        </h2>
                        <p style={{
                            color: 'var(--text-secondary)',
                            maxWidth: '400px',
                            marginBottom: '24px',
                            lineHeight: 1.6,
                        }}>
                            Simulate quenching, tempering, annealing, and normalizing processes.
                            Predict final mechanical properties based on treatment parameters.
                        </p>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '8px 16px',
                            background: 'var(--bg-tertiary)',
                            borderRadius: 'var(--radius-md)',
                            fontSize: '14px',
                            color: 'var(--accent-red)',
                        }}>
                            <div style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                background: 'var(--accent-red)',
                                animation: 'pulse 1.5s ease-in-out infinite',
                            }} />
                            In Development
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
