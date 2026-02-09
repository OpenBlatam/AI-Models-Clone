'use client';

import { PageHeader } from '@/components/layout/Header';
import { Microscope } from 'lucide-react';

export default function StructurePage() {
    return (
        <>
            <PageHeader
                title="STRUCTURE - Grain Analysis"
                subtitle="Macroestructure and grain size prediction"
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
                            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 24px',
                            boxShadow: '0 0 40px rgba(16, 185, 129, 0.3)',
                        }}>
                            <Microscope size={48} style={{ color: 'white' }} />
                        </div>
                        <h2 style={{ fontSize: '24px', marginBottom: '12px' }}>
                            Grain Structure Analysis
                        </h2>
                        <p style={{
                            color: 'var(--text-secondary)',
                            maxWidth: '400px',
                            marginBottom: '24px',
                            lineHeight: 1.6,
                        }}>
                            This module analyzes the microstructure and grain formation based on cooling
                            conditions and chemical composition. Coming soon with advanced nucleation modeling.
                        </p>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '8px 16px',
                            background: 'var(--bg-tertiary)',
                            borderRadius: 'var(--radius-md)',
                            fontSize: '14px',
                            color: 'var(--accent-green)',
                        }}>
                            <div style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                background: 'var(--accent-green)',
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
