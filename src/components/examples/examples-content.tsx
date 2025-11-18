'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Code, 
  Zap, 
  Database, 
  FormInput, 
  MousePointer, 
  BarChart3,
  Activity,
  Settings,
  Monitor,
  Network,
  Cpu,
  MemoryStick
} from 'lucide-react';
import { useExamplesStore } from '@/lib/stores/examples-store';

// Dynamic imports for better performance
const LocalStorageExample = dynamic(() => import('./local-storage-example'), {
  loading: () => <div className="p-4 text-center">Loading Local Storage Example...</div>
});

const DebounceExample = dynamic(() => import('./debounce-example'), {
  loading: () => <div className="p-4 text-center">Loading Debounce Example...</div>
});

const FormValidationExample = dynamic(() => import('./form-validation-example'), {
  loading: () => <div className="p-4 text-center">Loading Form Validation Example...</div>
});

const DataFetchingExample = dynamic(() => import('./data-fetching-example'), {
  loading: () => <div className="p-4 text-center">Loading Data Fetching Example...</div>
});

const AdvancedComponentsExample = dynamic(() => import('./advanced-components-example'), {
  loading: () => <div className="p-4 text-center">Loading Advanced Components Example...</div>
});

const PerformanceDashboard = dynamic(() => import('../dashboard/performance-dashboard'), {
  loading: () => <div className="p-4 text-center">Loading Performance Dashboard...</div>
});

interface ExampleConfig {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  component: React.ComponentType;
  category: 'hooks' | 'components' | 'performance' | 'monitoring';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
}

const examplesConfig: ExampleConfig[] = [
  {
    id: 'local-storage',
    title: 'Local Storage Hook',
    description: 'Persistent state management with localStorage integration',
    icon: Database,
    component: LocalStorageExample,
    category: 'hooks',
    difficulty: 'beginner',
    tags: ['state', 'persistence', 'localStorage']
  },
  {
    id: 'debounce',
    title: 'Debounce Hook',
    description: 'Optimize performance with debounced values and callbacks',
    icon: Zap,
    component: DebounceExample,
    category: 'hooks',
    difficulty: 'intermediate',
    tags: ['performance', 'optimization', 'debounce']
  },
  {
    id: 'form-validation',
    title: 'Form Validation',
    description: 'Advanced form validation with Zod and react-hook-form',
    icon: FormInput,
    component: FormValidationExample,
    category: 'hooks',
    difficulty: 'intermediate',
    tags: ['forms', 'validation', 'zod', 'react-hook-form']
  },
  {
    id: 'data-fetching',
    title: 'Data Fetching',
    description: 'Robust data fetching with caching, retry, and error handling',
    icon: BarChart3,
    component: DataFetchingExample,
    category: 'hooks',
    difficulty: 'advanced',
    tags: ['data', 'fetching', 'caching', 'error-handling']
  },
  {
    id: 'advanced-components',
    title: 'Advanced Components',
    description: 'Enterprise-level UI components with advanced features',
    icon: MousePointer,
    component: AdvancedComponentsExample,
    category: 'components',
    difficulty: 'advanced',
    tags: ['ui', 'components', 'enterprise', 'accessibility']
  },
  {
    id: 'performance-dashboard',
    title: 'Performance Dashboard',
    description: 'Comprehensive performance monitoring and analytics',
    icon: Activity,
    component: PerformanceDashboard,
    category: 'monitoring',
    difficulty: 'advanced',
    tags: ['performance', 'monitoring', 'analytics', 'dashboard']
  }
];

const categoryIcons = {
  hooks: Code,
  components: MousePointer,
  performance: Zap,
  monitoring: Monitor
};

const difficultyColors = {
  beginner: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  intermediate: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  advanced: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
};

export default function ExamplesContent() {
  const { activeTab, setActiveTab, performanceMetrics, errorLogs } = useExamplesStore();
  const [selectedExample, setSelectedExample] = useState<string>('local-storage');

  const handleTabChange = (value: string) => {
    setActiveTab(value);
  };

  const handleExampleSelect = (exampleId: string) => {
    setSelectedExample(exampleId);
  };

  const selectedExampleConfig = examplesConfig.find(ex => ex.id === selectedExample);
  const SelectedComponent = selectedExampleConfig?.component;

  const getCategoryExamples = (category: string) => {
    return examplesConfig.filter(ex => ex.category === category);
  };

  const getTotalErrors = () => {
    return errorLogs.filter(error => !error.resolved).length;
  };

  const getPerformanceScore = () => {
    if (!performanceMetrics) return 0;
    const { renderTime, memoryUsage, interactionCount } = performanceMetrics;
    
    // Simple scoring algorithm
    let score = 100;
    if (renderTime > 16) score -= 20; // Slow renders
    if (memoryUsage > 50) score -= 15; // High memory usage
    if (interactionCount > 100) score -= 10; // Too many interactions
    
    return Math.max(0, score);
  };

  return (
    <div className="space-y-8">
      {/* Header with Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance Score</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getPerformanceScore()}/100</div>
            <p className="text-xs text-muted-foreground">
              Based on render time, memory usage, and interactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Errors</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getTotalErrors()}</div>
            <p className="text-xs text-muted-foreground">
              {getTotalErrors() === 0 ? 'No active errors' : 'Errors need attention'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Examples Available</CardTitle>
            <Code className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{examplesConfig.length}</div>
            <p className="text-xs text-muted-foreground">
              Interactive examples and demos
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content with Tabs */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="hooks" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Hooks
          </TabsTrigger>
          <TabsTrigger value="components" className="flex items-center gap-2">
            <MousePointer className="h-4 w-4" />
            Components
          </TabsTrigger>
          <TabsTrigger value="monitoring" className="flex items-center gap-2">
            <Monitor className="h-4 w-4" />
            Monitoring
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {examplesConfig.map((example) => {
              const CategoryIcon = categoryIcons[example.category];
              return (
                <Card 
                  key={example.id} 
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => handleExampleSelect(example.id)}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <example.icon className="h-5 w-5" />
                        <CardTitle className="text-lg">{example.title}</CardTitle>
                      </div>
                      <CategoryIcon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <CardDescription>{example.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <Badge className={difficultyColors[example.difficulty]}>
                        {example.difficulty}
                      </Badge>
                      <div className="flex gap-1">
                        {example.tags.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="hooks" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {getCategoryExamples('hooks').map((example) => (
              <Card 
                key={example.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => handleExampleSelect(example.id)}
              >
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <example.icon className="h-5 w-5" />
                    <CardTitle className="text-lg">{example.title}</CardTitle>
                  </div>
                  <CardDescription>{example.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <Badge className={difficultyColors[example.difficulty]}>
                      {example.difficulty}
                    </Badge>
                    <Button variant="outline" size="sm">
                      Try Example
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="components" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {getCategoryExamples('components').map((example) => (
              <Card 
                key={example.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => handleExampleSelect(example.id)}
              >
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <example.icon className="h-5 w-5" />
                    <CardTitle className="text-lg">{example.title}</CardTitle>
                  </div>
                  <CardDescription>{example.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <Badge className={difficultyColors[example.difficulty]}>
                      {example.difficulty}
                    </Badge>
                    <Button variant="outline" size="sm">
                      Try Example
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {getCategoryExamples('monitoring').map((example) => (
              <Card 
                key={example.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => handleExampleSelect(example.id)}
              >
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <example.icon className="h-5 w-5" />
                    <CardTitle className="text-lg">{example.title}</CardTitle>
                  </div>
                  <CardDescription>{example.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <Badge className={difficultyColors[example.difficulty]}>
                      {example.difficulty}
                    </Badge>
                    <Button variant="outline" size="sm">
                      View Dashboard
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Selected Example Display */}
      {SelectedComponent && (
        <Card className="mt-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {selectedExampleConfig && (
                  <>
                    <selectedExampleConfig.icon className="h-5 w-5" />
                    <CardTitle className="text-xl">{selectedExampleConfig.title}</CardTitle>
                  </>
                )}
              </div>
              <div className="flex gap-2">
                {selectedExampleConfig?.tags.map((tag) => (
                  <Badge key={tag} variant="outline">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
            {selectedExampleConfig && (
              <CardDescription className="text-base">
                {selectedExampleConfig.description}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            <SelectedComponent />
          </CardContent>
        </Card>
      )}
    </div>
  );
}



