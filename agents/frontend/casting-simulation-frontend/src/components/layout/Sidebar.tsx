'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Settings,
    HelpCircle,
    Activity
} from 'lucide-react';
import { useSimulationStore } from '@/services/store/simulationStore';
import { SIMULATION_MODULES } from '@/types';
import { ModuleIcon } from '@/components/ui/ModuleIcon';

export function Sidebar() {
    const pathname = usePathname();
    const { isConnected, activeTasks } = useSimulationStore();
    const activeCount = Array.from(activeTasks.values()).filter(t => t.status === 'running').length;

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <div className="sidebar-logo-icon">CS</div>
                    <div>
                        <div className="sidebar-logo-text">CastSim AI</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            v1.0.0
                        </div>
                    </div>
                </div>
            </div>

            <nav className="sidebar-nav">
                <div className="sidebar-section">
                    <div className="sidebar-section-title">Navigation</div>
                    <Link
                        href="/"
                        className={`nav-item ${pathname === '/' ? 'active' : ''}`}
                    >
                        <LayoutDashboard className="nav-item-icon" style={{ color: pathname === '/' ? '#94a3b8' : undefined }} />
                        <span className="nav-item-text">Dashboard</span>
                    </Link>
                </div>

                <div className="sidebar-section">
                    <div className="sidebar-section-title">Simulation Modules</div>
                    {SIMULATION_MODULES.map((module) => {
                        const isActive = pathname === module.path;
                        return (
                            <Link
                                key={module.id}
                                href={module.path}
                                className={`nav-item ${isActive ? 'active' : ''}`}
                            >
                                <ModuleIcon
                                    name={module.icon}
                                    className="nav-item-icon"
                                    style={{ color: isActive ? module.color : undefined }}
                                />
                                <div style={{ flex: 1 }}>
                                    <span className="nav-item-text">{module.name}</span>
                                    {module.description && (
                                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                            {module.description}
                                        </div>
                                    )}
                                </div>
                            </Link>
                        );
                    })}
                </div>

                <div className="sidebar-section">
                    <div className="sidebar-section-title">System</div>
                    <div className="nav-item">
                        <Activity className="nav-item-icon" />
                        <span className="nav-item-text">Status</span>
                        <span
                            className="nav-item-badge"
                            style={{
                                background: isConnected ? 'var(--accent-green)' : 'var(--accent-red)',
                            }}
                        >
                            {isConnected ? 'Online' : 'Offline'}
                        </span>
                    </div>
                    {activeCount > 0 && (
                        <div className="nav-item" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>
                            <div className="spinner" style={{ width: 18, height: 18 }} />
                            <span className="nav-item-text">Running Tasks</span>
                            <span className="nav-item-badge">{activeCount}</span>
                        </div>
                    )}
                    <Link href="/settings" className="nav-item">
                        <Settings className="nav-item-icon" />
                        <span className="nav-item-text">Settings</span>
                    </Link>
                    <Link href="/help" className="nav-item">
                        <HelpCircle className="nav-item-icon" />
                        <span className="nav-item-text">Help</span>
                    </Link>
                </div>
            </nav>

            <div style={{
                padding: '16px 20px',
                borderTop: '1px solid var(--border-subtle)',
                fontSize: '12px',
                color: 'var(--text-muted)',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: isConnected ? 'var(--accent-green)' : 'var(--accent-red)',
                    }} />
                    Backend: {isConnected ? 'Connected' : 'Disconnected'}
                </div>
                <div>Based on PoligonCast</div>
            </div>
        </aside>
    );
}
