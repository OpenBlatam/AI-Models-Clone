'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// React Query Provider & Configuration
// ═══════════════════════════════════════════════════════════════════════════════

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, type ReactNode } from 'react';

interface QueryProviderProps {
    children: ReactNode;
}

export const QueryProvider = ({ children }: QueryProviderProps) => {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        // Stale time: 1 minute
                        staleTime: 60 * 1000,
                        // Cache time: 5 minutes
                        gcTime: 5 * 60 * 1000,
                        // Retry failed queries up to 2 times
                        retry: 2,
                        // Refetch on window focus
                        refetchOnWindowFocus: false,
                        // Refetch on reconnect
                        refetchOnReconnect: true,
                    },
                    mutations: {
                        // Retry mutations once
                        retry: 1,
                    },
                },
            })
    );

    return (
        <QueryClientProvider client={queryClient}>
            {children}
            <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
    );
};

export default QueryProvider;
