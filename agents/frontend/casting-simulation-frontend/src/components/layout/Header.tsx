'use client';

import { Bell, Search, User } from 'lucide-react';
import { useSimulationStore } from '@/services/store/simulationStore';

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    actions?: React.ReactNode;
}

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
    const { activeTasks } = useSimulationStore();
    const pendingCount = Array.from(activeTasks.values()).filter(
        t => t.status === 'pending' || t.status === 'running'
    ).length;

    return (
        <header className="page-header">
            <div>
                <h1 className="page-title">{title}</h1>
                {subtitle && <p className="page-subtitle">{subtitle}</p>}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {actions}

                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    background: 'var(--bg-tertiary)',
                    borderRadius: 'var(--radius-md)',
                    padding: '8px 16px',
                    gap: '8px',
                }}>
                    <Search size={16} style={{ color: 'var(--text-muted)' }} />
                    <input
                        type="text"
                        placeholder="Search simulations..."
                        style={{
                            background: 'transparent',
                            border: 'none',
                            outline: 'none',
                            color: 'var(--text-primary)',
                            fontSize: '14px',
                            width: '200px',
                        }}
                    />
                </div>

                <button className="btn-icon" style={{ position: 'relative' }}>
                    <Bell size={18} />
                    {pendingCount > 0 && (
                        <span style={{
                            position: 'absolute',
                            top: '-4px',
                            right: '-4px',
                            width: '18px',
                            height: '18px',
                            background: 'var(--accent-red)',
                            borderRadius: '50%',
                            fontSize: '10px',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                        }}>
                            {pendingCount}
                        </span>
                    )}
                </button>

                <button className="btn-icon">
                    <User size={18} />
                </button>
            </div>
        </header>
    );
}
