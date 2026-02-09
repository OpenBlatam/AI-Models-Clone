'use client';

import {
    LineChart,
    Line,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend
} from 'recharts';

interface TemperatureChartProps {
    data?: Array<{
        time: number;
        temperature: number;
        solidification?: number;
    }>;
    title?: string;
}

// Generate sample data if none provided
function generateSampleData() {
    const data = [];
    for (let i = 0; i <= 100; i += 5) {
        const t = i;
        const temp = 720 - (720 - 25) * (1 - Math.exp(-t / 30));
        const solidification = Math.min(100, Math.max(0, (t - 10) * 2));
        data.push({
            time: t,
            temperature: Math.round(temp),
            solidification: Math.round(solidification),
        });
    }
    return data;
}

export function TemperatureChart({
    data = generateSampleData(),
    title = "Temperature vs Time"
}: TemperatureChartProps) {
    return (
        <div className="card">
            <div className="card-header">
                <div>
                    <h3 className="card-title">{title}</h3>
                    <p className="card-description">Temperature evolution during solidification</p>
                </div>
            </div>

            <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="solidGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                        <XAxis
                            dataKey="time"
                            stroke="var(--text-muted)"
                            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                            label={{ value: 'Time (s)', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
                        />
                        <YAxis
                            yAxisId="temp"
                            stroke="var(--text-muted)"
                            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                            domain={[0, 800]}
                            label={{ value: '°C', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
                        />
                        <YAxis
                            yAxisId="solid"
                            orientation="right"
                            stroke="var(--text-muted)"
                            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                            domain={[0, 100]}
                            label={{ value: '%', angle: 90, position: 'insideRight', fill: 'var(--text-muted)' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: 'var(--bg-elevated)',
                                border: '1px solid var(--border-default)',
                                borderRadius: 'var(--radius-md)',
                            }}
                            labelStyle={{ color: 'var(--text-primary)' }}
                        />
                        <Legend />
                        <Area
                            yAxisId="temp"
                            type="monotone"
                            dataKey="temperature"
                            stroke="#ef4444"
                            fill="url(#tempGradient)"
                            strokeWidth={2}
                            name="Temperature (°C)"
                        />
                        <Area
                            yAxisId="solid"
                            type="monotone"
                            dataKey="solidification"
                            stroke="#3b82f6"
                            fill="url(#solidGradient)"
                            strokeWidth={2}
                            name="Solidification (%)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

interface StressContourProps {
    maxStress?: number;
    yieldStrength?: number;
    safetyFactor?: number;
}

export function StressChart({ maxStress = 85, yieldStrength = 170, safetyFactor = 2.0 }: StressContourProps) {
    // Simulated stress distribution data
    const data = [];
    for (let i = 0; i <= 10; i++) {
        const x = i;
        const stress = maxStress * Math.sin((i / 10) * Math.PI) * 0.8 + maxStress * 0.2;
        data.push({
            position: x,
            vonMises: Math.round(stress),
            principal: Math.round(stress * 0.9),
            yield: yieldStrength,
        });
    }

    const isSafe = safetyFactor > 1.5;

    return (
        <div className="card">
            <div className="card-header">
                <div>
                    <h3 className="card-title">Stress Distribution</h3>
                    <p className="card-description">Von Mises stress along critical path</p>
                </div>
                <div className={`status-badge ${isSafe ? 'status-completed' : 'status-failed'}`}>
                    <span className="status-dot" />
                    SF: {safetyFactor.toFixed(2)}
                </div>
            </div>

            <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                        <XAxis
                            dataKey="position"
                            stroke="var(--text-muted)"
                            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                            label={{ value: 'Position (mm)', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
                        />
                        <YAxis
                            stroke="var(--text-muted)"
                            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                            domain={[0, 200]}
                            label={{ value: 'Stress (MPa)', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: 'var(--bg-elevated)',
                                border: '1px solid var(--border-default)',
                                borderRadius: 'var(--radius-md)',
                            }}
                        />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="vonMises"
                            stroke="#f59e0b"
                            strokeWidth={2}
                            dot={{ fill: '#f59e0b', strokeWidth: 0 }}
                            name="Von Mises Stress"
                        />
                        <Line
                            type="monotone"
                            dataKey="principal"
                            stroke="#8b5cf6"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={false}
                            name="Principal Stress"
                        />
                        <Line
                            type="monotone"
                            dataKey="yield"
                            stroke="#ef4444"
                            strokeWidth={2}
                            strokeDasharray="10 5"
                            dot={false}
                            name="Yield Strength"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
