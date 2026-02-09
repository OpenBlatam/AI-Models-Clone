'use client';

import { ReactNode, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { useHealthCheck } from '@/services/hooks/useSimulation';

interface AppLayoutProps {
    children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
    // Start health check polling
    useHealthCheck();

    return (
        <div className="app-layout">
            <Sidebar />
            <main className="main-content">
                {children}
            </main>
        </div>
    );
}
