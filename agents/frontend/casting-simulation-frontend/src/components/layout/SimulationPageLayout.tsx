'use client';

import { ReactNode } from 'react';
import { PageHeader } from '@/components/layout/Header';
import { AlertTriangle, LucideIcon } from 'lucide-react';

interface SimulationPageLayoutProps {
    title: string;
    subtitle: string;
    form: ReactNode;
    results: ReactNode;
    error?: string | null;
    isLoading?: boolean;
    hasRun?: boolean;
    emptyStateIcon: LucideIcon;
    emptyStateMessage: string;
    emptyStateDescription: string;
    loadingMessage?: string;
    loadingDescription?: string;
}

export function SimulationPageLayout({
    title,
    subtitle,
    form,
    results,
    error,
    isLoading,
    hasRun,
    emptyStateIcon: EmptyIcon,
    emptyStateMessage,
    emptyStateDescription,
    loadingMessage = 'Running Simulation',
    loadingDescription = 'Processing your request...',
}: SimulationPageLayoutProps) {
    return (
        <>
            <PageHeader title={title} subtitle={subtitle} />

            <div className="page-content">
                <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '24px' }}>
                    {/* Form Panel */}
                    <div>
                        <div className="card">
                            <h3 style={{ fontWeight: '600', marginBottom: '20px' }}>Parameters</h3>
                            {form}
                        </div>

                        {error && (
                            <div className="card" style={{
                                marginTop: '16px',
                                borderLeft: '3px solid var(--accent-red)',
                                background: 'rgba(239, 68, 68, 0.1)',
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-red)' }}>
                                    <AlertTriangle size={18} />
                                    <span>{error}</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Results Panel */}
                    <div>
                        {!hasRun ? (
                            <div className="card" style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                minHeight: '400px',
                                textAlign: 'center',
                            }}>
                                <div>
                                    <div style={{
                                        width: '80px',
                                        height: '80px',
                                        borderRadius: '50%',
                                        background: 'var(--bg-tertiary)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        margin: '0 auto 16px',
                                    }}>
                                        <EmptyIcon size={32} style={{ color: 'var(--text-muted)' }} />
                                    </div>
                                    <h3 style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}>
                                        {emptyStateMessage}
                                    </h3>
                                    <p style={{ color: 'var(--text-muted)', maxWidth: '300px' }}>
                                        {emptyStateDescription}
                                    </p>
                                </div>
                            </div>
                        ) : isLoading ? (
                            <div className="card" style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                minHeight: '400px',
                            }}>
                                <div style={{ textAlign: 'center' }}>
                                    <div className="spinner" style={{
                                        width: 48,
                                        height: 48,
                                        margin: '0 auto 16px',
                                        borderWidth: '4px',
                                    }} />
                                    <h3 style={{ marginBottom: '8px' }}>{loadingMessage}</h3>
                                    <p style={{ color: 'var(--text-muted)' }}>
                                        {loadingDescription}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            results
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
