'use client';

import { CheckCircle, AlertCircle, Clock, Loader2, ChevronRight } from 'lucide-react';
import type { SimulationResponse, TaskStatusResponse } from '@/types';

interface ResultCardProps {
    title: string;
    status: TaskStatusResponse['status'];
    result?: SimulationResponse;
    onViewDetails?: () => void;
}

export function ResultCard({ title, status, result, onViewDetails }: ResultCardProps) {
    const statusConfig = {
        pending: { icon: Clock, color: 'var(--accent-orange)', label: 'Pending' },
        running: { icon: Loader2, color: 'var(--accent-blue)', label: 'Running' },
        completed: { icon: CheckCircle, color: 'var(--accent-green)', label: 'Completed' },
        failed: { icon: AlertCircle, color: 'var(--accent-red)', label: 'Failed' },
    };

    const config = statusConfig[status];
    const Icon = config.icon;

    return (
        <div className="card" style={{
            cursor: onViewDetails ? 'pointer' : 'default',
            transition: 'all var(--transition-fast)',
        }}
            onClick={onViewDetails}
        >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: 'var(--radius-md)',
                        background: `${config.color}20`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: config.color,
                    }}>
                        <Icon
                            size={20}
                            className={status === 'running' ? 'spinner' : ''}
                            style={status === 'running' ? { animation: 'spin 0.8s linear infinite' } : {}}
                        />
                    </div>
                    <div>
                        <h4 style={{ fontWeight: 600, marginBottom: '2px' }}>{title}</h4>
                        <span className={`status-badge status-${status}`}>
                            <span className="status-dot" />
                            {config.label}
                        </span>
                    </div>
                </div>
                {onViewDetails && (
                    <ChevronRight size={20} style={{ color: 'var(--text-muted)' }} />
                )}
            </div>

            {result && status === 'completed' && result.data && (
                <div style={{
                    marginTop: '16px',
                    paddingTop: '16px',
                    borderTop: '1px solid var(--border-subtle)',
                }}>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(3, 1fr)',
                        gap: '12px',
                    }}>
                        {Object.entries(result.data).slice(0, 6).map(([key, value]) => (
                            <div key={key}>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                                    {key.replace(/_/g, ' ')}
                                </div>
                                <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)' }}>
                                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

interface MetricCardProps {
    label: string;
    value: string | number;
    unit?: string;
    change?: number;
    icon?: React.ReactNode;
    color?: string;
}

export function MetricCard({ label, value, unit, change, icon, color = 'var(--accent-blue)' }: MetricCardProps) {
    return (
        <div className="card">
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                        {label}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                        <span className="stat-value" style={{
                            background: `linear-gradient(135deg, ${color} 0%, color-mix(in srgb, ${color} 70%, white) 100%)`,
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                        }}>
                            {typeof value === 'number' ? value.toLocaleString() : value}
                        </span>
                        {unit && (
                            <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>{unit}</span>
                        )}
                    </div>
                    {change !== undefined && (
                        <div className={`stat-change ${change >= 0 ? 'positive' : 'negative'}`}>
                            {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
                        </div>
                    )}
                </div>
                {icon && (
                    <div style={{
                        width: '48px',
                        height: '48px',
                        borderRadius: 'var(--radius-md)',
                        background: `${color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: color,
                    }}>
                        {icon}
                    </div>
                )}
            </div>
        </div>
    );
}

interface RecommendationCardProps {
    title: string;
    recommendations: string[];
    severity?: 'info' | 'warning' | 'error';
}

export function RecommendationCard({ title, recommendations, severity = 'info' }: RecommendationCardProps) {
    const colors = {
        info: 'var(--accent-blue)',
        warning: 'var(--accent-orange)',
        error: 'var(--accent-red)',
    };

    return (
        <div className="card" style={{ borderLeft: `3px solid ${colors[severity]}` }}>
            <h4 style={{ fontWeight: 600, marginBottom: '12px', color: colors[severity] }}>
                {title}
            </h4>
            <ul style={{
                listStyle: 'none',
                margin: 0,
                padding: 0,
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
            }}>
                {recommendations.map((rec, i) => (
                    <li key={i} style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '8px',
                        fontSize: '14px',
                        color: 'var(--text-secondary)',
                    }}>
                        <span style={{
                            color: colors[severity],
                            fontWeight: 600,
                            minWidth: '16px',
                        }}>
                            {i + 1}.
                        </span>
                        {rec}
                    </li>
                ))}
            </ul>
        </div>
    );
}
