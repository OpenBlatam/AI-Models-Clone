'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useDebounce } from '@/hooks/use-debounce';
import { toast } from 'react-hot-toast';
import { Search, Activity, Clock, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { usePerformanceMonitor, useHookStatusMonitor, useExamplesStore } from '@/lib/stores/examples-store';

const DEBOUNCE_DELAY = 500;
const MIN_SEARCH_LENGTH = 2;

interface SearchState {
  term: string;
  isTyping: boolean;
  lastTyped: number;
}

export default function DebounceExample() {
  const [searchState, setSearchState] = useState<SearchState>({
    term: '',
    isTyping: false,
    lastTyped: Date.now()
  });

  // Performance monitoring
  const { updatePerformanceMetrics } = usePerformanceMonitor();
  const { updateHookStatus } = useHookStatusMonitor('debounce');

  // Debounced search term
  const debouncedSearchTerm = useDebounce(searchState.term, DEBOUNCE_DELAY);

  // Memoized values for performance
  const hasValidSearch = useMemo(() => 
    debouncedSearchTerm.length >= MIN_SEARCH_LENGTH, 
    [debouncedSearchTerm]
  );

  const isSearching = useMemo(() => 
    searchState.isTyping && hasValidSearch, 
    [searchState.isTyping, hasValidSearch]
  );

  const searchDelay = useMemo(() => {
    if (!searchState.isTyping) return 0;
    const elapsed = Date.now() - searchState.lastTyped;
    return Math.max(0, DEBOUNCE_DELAY - elapsed);
  }, [searchState.isTyping, searchState.lastTyped]);

  // Error handling
  const [hasError, setHasError] = useState(false);

  // Update hook status in store
  useEffect(() => {
    try {
      updateHookStatus({
        isActive: searchState.isTyping,
        lastUsed: Date.now(),
        usageCount: (prev) => prev + 1
      });
    } catch (error) {
      console.error('Failed to update hook status:', error);
      setHasError(true);
    }
  }, [searchState.isTyping, updateHookStatus]);

  // Log errors to store
  useEffect(() => {
    if (hasError) {
      const { logError } = useExamplesStore.getState();
      logError({
        message: 'Debounce hook error',
        stack: 'Error in debounce example component',
        severity: 'warning'
      });
    }
  }, [hasError]);

  // Handle search input changes
  const handleSearchChange = useCallback((value: string) => {
    try {
      setSearchState(prev => ({
        term: value,
        isTyping: true,
        lastTyped: Date.now()
      }));
    } catch (error) {
      console.error('Search change error:', error);
      setHasError(true);
      toast.error('Failed to update search');
    }
  }, []);

  // Handle search completion
  const handleSearchComplete = useCallback((term: string) => {
    try {
      if (term.length >= MIN_SEARCH_LENGTH) {
        // Simulate API call
        console.log('Searching for:', term);
        setSearchState(prev => ({ ...prev, isTyping: false }));
        toast.success(`Search completed for: ${term}`);
      }
    } catch (error) {
      console.error('Search completion error:', error);
      setHasError(true);
      toast.error('Search failed');
    }
  }, []);

  // Effect to trigger search when debounced term changes
  useEffect(() => {
    if (debouncedSearchTerm !== searchState.term) {
      handleSearchComplete(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm, searchState.term, handleSearchComplete]);

  // Early return for initialization failures
  if (hasError) {
    return (
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Error Loading Component
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            There was an error initializing the debounce example. Please refresh the page.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Input Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search with Debouncing
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="search-input" className="text-sm font-medium">
              Search Term
            </label>
            <div className="relative">
              <Input
                id="search-input"
                type="text"
                placeholder="Type to search..."
                value={searchState.term}
                onChange={(e) => handleSearchChange(e.target.value)}
                className={`transition-all duration-200 ${
                  searchState.isTyping 
                    ? 'ring-2 ring-primary border-primary' 
                    : ''
                }`}
                aria-describedby="search-help"
                aria-invalid={hasError}
                data-testid="search-input"
              />
              {searchState.isTyping && (
                <Activity className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
              )}
            </div>
            <p id="search-help" className="text-xs text-muted-foreground">
              Type at least {MIN_SEARCH_LENGTH} characters to trigger search
            </p>
          </div>

          {/* Real-time Status */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">
                Current value
              </label>
              <div className="text-sm font-mono bg-muted px-2 py-1 rounded">
                {searchState.term || 'empty'}
              </div>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">
                Debounced value
              </label>
              <div className="text-sm font-mono bg-muted px-2 py-1 rounded">
                {debouncedSearchTerm || 'empty'}
              </div>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">
                Searching in
              </label>
              <div className="text-sm font-mono bg-muted px-2 py-1 rounded">
                {searchDelay > 0 ? `${Math.ceil(searchDelay / 100)}s` : '0s'}
              </div>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex flex-wrap gap-2">
            {hasValidSearch && (
              <Badge variant="default" className="animate-pulse">
                API Call Triggered
              </Badge>
            )}
            {isSearching && (
              <Badge variant="secondary" className="animate-spin">
                Searching
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Configuration Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">API Endpoint</label>
              <div className="text-sm text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                /api/search
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Debounce Delay</label>
              <div className="text-sm text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                {DEBOUNCE_DELAY}ms
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Min Search Length</label>
              <div className="text-sm text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                {MIN_SEARCH_LENGTH} characters
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <div className="flex items-center gap-2">
                <Badge variant={isSearching ? 'default' : 'secondary'}>
                  {isSearching ? 'Active' : 'Idle'}
                </Badge>
                {isSearching && <Clock className="h-4 w-4 animate-pulse" />}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            Performance Tips
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <h4 className="font-medium">Why Debouncing?</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Reduces unnecessary API calls during typing</li>
              <li>• Improves user experience with smoother interactions</li>
              <li>• Saves bandwidth and server resources</li>
              <li>• Prevents rapid state updates that can cause performance issues</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">Use Cases</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Search inputs and autocomplete</li>
              <li>• Window resize handlers</li>
              <li>• Scroll event handlers</li>
              <li>• Form input validation</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}





