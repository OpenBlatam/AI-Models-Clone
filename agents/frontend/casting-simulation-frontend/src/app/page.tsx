'use client';

import Link from 'next/link';
import {
  ArrowRight,
  Activity,
  Clock,
  CheckCircle2,
  Droplets
} from 'lucide-react';
import { PageHeader } from '@/components/layout/Header';
import { MetricCard } from '@/components/cards/ResultCard';
import { useSimulationStore } from '@/services/store/simulationStore';
import { SIMULATION_MODULES } from '@/types';
import { ModuleIcon } from '@/components/ui/ModuleIcon';

export default function DashboardPage() {
  const { history, activeTasks, isConnected } = useSimulationStore();
  const runningTasks = Array.from(activeTasks.values()).filter(t => t.status === 'running').length;
  const completedToday = history.slice(0, 10).length;

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="Casting Simulation AI Overview"
      />

      <div className="page-content">
        {/* Quick Stats */}
        <div className="grid-3" style={{ marginBottom: '32px' }}>
          <MetricCard
            label="System Status"
            value={isConnected ? 'Online' : 'Offline'}
            icon={<Activity size={24} />}
            color={isConnected ? 'var(--accent-green)' : 'var(--accent-red)'}
          />
          <MetricCard
            label="Running Simulations"
            value={runningTasks}
            icon={<Clock size={24} />}
            color="var(--accent-blue)"
          />
          <MetricCard
            label="Completed Today"
            value={completedToday}
            icon={<CheckCircle2 size={24} />}
            color="var(--accent-green)"
            change={12}
          />
        </div>

        {/* Module Cards */}
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          marginBottom: '20px',
          color: 'var(--text-secondary)'
        }}>
          Simulation Modules
        </h2>

        <div className="grid-modules">
          {SIMULATION_MODULES.map((module) => {
            return (
              <Link key={module.id} href={module.path}>
                <div
                  className="module-card"
                  style={{ '--module-color': module.color } as React.CSSProperties}
                >
                  <div
                    className="module-icon"
                    style={{ background: module.color }}
                  >
                    <ModuleIcon name={module.icon} size={24} />
                  </div>
                  <h3 className="module-name">{module.name}</h3>
                  <p className="module-description">{module.description}</p>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    marginTop: '16px',
                    color: module.color,
                    fontSize: '14px',
                    fontWeight: '500',
                  }}>
                    Open Module <ArrowRight size={16} />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Recent Activity */}
        {history.length > 0 && (
          <div style={{ marginTop: '40px' }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              marginBottom: '20px',
              color: 'var(--text-secondary)'
            }}>
              Recent Simulations
            </h2>

            <div className="card">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {history.slice(0, 5).map((result, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px',
                      background: 'var(--bg-tertiary)',
                      borderRadius: 'var(--radius-md)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <CheckCircle2 size={18} style={{ color: 'var(--accent-green)' }} />
                      <div>
                        <div style={{ fontWeight: '500' }}>
                          Simulation #{history.length - i}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          {result.timestamp || 'Just now'}
                        </div>
                      </div>
                    </div>
                    <span className="status-badge status-completed">
                      <span className="status-dot" />
                      Completed
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Quick Start */}
        <div style={{ marginTop: '40px' }}>
          <div className="card" style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
              🚀 Quick Start
            </h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
              New to casting simulation? Start with a filling simulation to see the metal flow.
            </p>
            <Link href="/filling">
              <button className="btn btn-primary">
                <Droplets size={18} />
                Start Filling Simulation
              </button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
