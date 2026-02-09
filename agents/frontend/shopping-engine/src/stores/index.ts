'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Zustand Store for Global State Management
// ═══════════════════════════════════════════════════════════════════════════════

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { ProductInfo } from '@/src/types/api';

// ── Product Store ────────────────────────────────────────────────────────────

interface ProductState {
    // Current analyzed product
    currentProduct: ProductInfo | null;
    // Recent products (history)
    recentProducts: ProductInfo[];
    // Selected product for comparison
    comparisonProducts: ProductInfo[];

    // Actions
    setCurrentProduct: (product: ProductInfo | null) => void;
    addToRecent: (product: ProductInfo) => void;
    addToComparison: (product: ProductInfo) => void;
    removeFromComparison: (productName: string) => void;
    clearComparison: () => void;
    clearHistory: () => void;
}

export const useProductStore = create<ProductState>()(
    persist(
        (set, get) => ({
            currentProduct: null,
            recentProducts: [],
            comparisonProducts: [],

            setCurrentProduct: (product) => {
                set({ currentProduct: product });
                if (product) {
                    get().addToRecent(product);
                }
            },

            addToRecent: (product) => {
                set((state) => {
                    // Remove duplicate if exists
                    const filtered = state.recentProducts.filter(
                        (p) => p.name !== product.name
                    );
                    // Keep only last 10 products
                    const updated = [product, ...filtered].slice(0, 10);
                    return { recentProducts: updated };
                });
            },

            addToComparison: (product) => {
                set((state) => {
                    // Maximum 4 products for comparison
                    if (state.comparisonProducts.length >= 4) return state;
                    // Check if already exists
                    if (state.comparisonProducts.some((p) => p.name === product.name)) {
                        return state;
                    }
                    return {
                        comparisonProducts: [...state.comparisonProducts, product],
                    };
                });
            },

            removeFromComparison: (productName) => {
                set((state) => ({
                    comparisonProducts: state.comparisonProducts.filter(
                        (p) => p.name !== productName
                    ),
                }));
            },

            clearComparison: () => set({ comparisonProducts: [] }),
            clearHistory: () => set({ recentProducts: [] }),
        }),
        {
            name: 'shopping-engine-products',
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({
                recentProducts: state.recentProducts,
                comparisonProducts: state.comparisonProducts,
            }),
        }
    )
);

// ── UI Store ─────────────────────────────────────────────────────────────────

interface UIState {
    // Sidebar state
    isSidebarOpen: boolean;
    // Loading states
    isGlobalLoading: boolean;
    // Theme
    theme: 'dark' | 'light';

    // Actions
    toggleSidebar: () => void;
    setGlobalLoading: (loading: boolean) => void;
    setTheme: (theme: 'dark' | 'light') => void;
}

export const useUIStore = create<UIState>()(
    persist(
        (set) => ({
            isSidebarOpen: true,
            isGlobalLoading: false,
            theme: 'dark',

            toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
            setGlobalLoading: (loading) => set({ isGlobalLoading: loading }),
            setTheme: (theme) => set({ theme }),
        }),
        {
            name: 'shopping-engine-ui',
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({
                isSidebarOpen: state.isSidebarOpen,
                theme: state.theme,
            }),
        }
    )
);

// ── Search History Store ─────────────────────────────────────────────────────

interface SearchState {
    searches: Array<{
        query: string;
        type: 'analyze' | 'purchase' | 'recommendations' | 'compare' | 'details';
        timestamp: number;
    }>;

    addSearch: (query: string, type: SearchState['searches'][0]['type']) => void;
    clearSearches: () => void;
}

export const useSearchStore = create<SearchState>()(
    persist(
        (set) => ({
            searches: [],

            addSearch: (query, type) => {
                set((state) => {
                    const newSearch = { query, type, timestamp: Date.now() };
                    // Keep last 20 searches
                    const updated = [newSearch, ...state.searches].slice(0, 20);
                    return { searches: updated };
                });
            },

            clearSearches: () => set({ searches: [] }),
        }),
        {
            name: 'shopping-engine-searches',
            storage: createJSONStorage(() => localStorage),
        }
    )
);
