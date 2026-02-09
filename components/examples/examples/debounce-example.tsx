'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useDebounce } from '@/hooks/use-debounce';
import { Search, Activity, Clock } from 'lucide-react';

// Constants for better maintainability
const DEBOUNCE_DELAY = 500;
const MIN_SEARCH_LENGTH = 2;

interface SearchState {
  term: string;
  isTyping: boolean;
  lastTyped: number;
}

export default function DebounceExample() {
  // Local state management
  const [searchState, setSearchState] = useState<SearchState>({
    term: '',
    isTyping: false,
    lastTyped: Date.now(),
  });

  // Debounced search term for API calls
  const debouncedSearchTerm = useDebounce(searchState.term, DEBOUNCE_DELAY);

  // Memoized computed values
  const hasValidSearch = useMemo(() => 
    debouncedSearchTerm.length >= MIN_SEARCH_LENGTH, 
    [debouncedSearchTerm]
  );

  const isSearching = useMemo(() => 
    searchState.isTyping || (hasValidSearch && debouncedSearchTerm !== searchState.term),
    [searchState.isTyping, hasValidSearch, debouncedSearchTerm, searchState.term]
  );

  const searchDelay = useMemo(() => {
    if (!searchState.isTyping) return 0;
    return Math.max(0, DEBOUNCE_DELAY - (Date.now() - searchState.lastTyped));
  }, [searchState.isTyping, searchState.lastTyped]);

  // Optimized handlers with useCallback
  const handleSearchChange = useCallback((value: string) => {
    setSearchState(prev => ({
      term: value,
      isTyping: true,
      lastTyped: Date.now(),
    }));
  }, []);

  const handleSearchComplete = useCallback(() => {
    setSearchState(prev => ({
      ...prev,
      isTyping: false,
    }));
  }, []);

  // Effect to handle search completion
  useEffect(() => {
    if (debouncedSearchTerm !== searchState.term) {
      handleSearchComplete();
    }
  }, [debouncedSearchTerm, searchState.term, handleSearchComplete]);

  // Early return for invalid states
  if (searchState.term === undefined) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">Failed to initialize search</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Search Input Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Search className="h-5 w-5" />
              Search Input
            </CardTitle>
            <CardDescription>
              Type here to see debouncing in action
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Input
                placeholder="Search..."
                value={searchState.term}
                onChange={(e) => handleSearchChange(e.target.value)}
                className={`transition-all duration-200 ${
                  searchState.isTyping 
                    ? 'ring-2 ring-primary/20 border-primary' 
                    : ''
                }`}
              />
              {searchState.isTyping && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Activity className="h-4 w-4 animate-pulse text-primary" />
                </div>
              )}
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium">Current value:</span>
                <span className="text-muted-foreground">
                  {searchState.term || '(empty)'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">Debounced value:</span>
                <span className="text-muted-foreground">
                  {debouncedSearchTerm || '(empty)'}
                </span>
              </div>
              {searchState.isTyping && (
                <div className="flex items-center justify-between text-primary">
                  <span className="font-medium">Searching in:</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {Math.ceil(searchDelay)}ms
                  </span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* API Call Simulation Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">API Call Simulation</CardTitle>
            <CardDescription>
              This would trigger an API call with the debounced value
            </CardDescription>
          </CardHeader>
          <CardContent>
            {hasValidSearch ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="success" className="animate-pulse">
                    API Call Triggered
                  </Badge>
                  {isSearching && (
                    <Badge variant="default">
                      <Activity className="h-3 w-3 mr-1 animate-spin" />
                      Searching
                    </Badge>
                  )}
                </div>
                
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    <span className="font-medium">Searching for:</span>{' '}
                    <span className="font-mono bg-muted px-2 py-1 rounded">
                      {debouncedSearchTerm}
                    </span>
                  </p>
                  
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>• API endpoint: <code>/api/search?q={debouncedSearchTerm}</code></p>
                    <p>• Debounce delay: {DEBOUNCE_DELAY}ms</p>
                    <p>• Min search length: {MIN_SEARCH_LENGTH} characters</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-sm text-muted-foreground">
                  {searchState.term.length > 0 && searchState.term.length < MIN_SEARCH_LENGTH ? (
                    <p>Type at least {MIN_SEARCH_LENGTH} characters to trigger search</p>
                  ) : (
                    <p>No search term yet</p>
                  )}
                </div>
                
                <div className="text-xs text-muted-foreground space-y-1">
                  <p>• Minimum search length: {MIN_SEARCH_LENGTH} characters</p>
                  <p>• Debounce delay: {DEBOUNCE_DELAY}ms</p>
                  <p>• Prevents excessive API calls</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Performance Tips */}
      <div className="text-sm text-muted-foreground space-y-2">
        <p>💡 Notice how the API call only triggers {DEBOUNCE_DELAY}ms after you stop typing!</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Performance Benefits</p>
            <ul className="space-y-1">
              <li>• Reduces API calls</li>
              <li>• Improves user experience</li>
              <li>• Saves bandwidth</li>
            </ul>
          </div>
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Use Cases</p>
            <ul className="space-y-1">
              <li>• Search inputs</li>
              <li>• Form validation</li>
              <li>• Window resize handlers</li>
            </ul>
          </div>
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Implementation</p>
            <ul className="space-y-1">
              <li>• Custom hook</li>
              <li>• Configurable delay</li>
              <li>• TypeScript support</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
