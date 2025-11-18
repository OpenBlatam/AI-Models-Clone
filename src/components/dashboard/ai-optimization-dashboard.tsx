'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  Zap, 
  Shield, 
  Accessibility, 
  Search, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  BarChart3,
  Target,
  Activity,
  Settings,
  Download,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react';
import { 
  aiOptimizer, 
  aiUtils,
  type OptimizationSuggestion, 
  type AIPrediction,
  type PerformancePattern 
} from '@/lib/ai/ai-optimizer';

interface AIDashboardProps {
  className?: string;
}

export function AIOptimizationDashboard({ className }: AIDashboardProps) {
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [predictions, setPredictions] = useState<AIPrediction[]>([]);
  const [patterns, setPatterns] = useState<PerformancePattern[]>([]);
  const [modelStatus, setModelStatus] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<OptimizationSuggestion | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const status = aiUtils.getModelStatus();
      setModelStatus(status);
      
      const criticalSuggestions = aiUtils.getCriticalSuggestions();
      const highImpactSuggestions = aiUtils.getHighImpactSuggestions();
      setSuggestions([...criticalSuggestions, ...highImpactSuggestions]);
      
      const aiPredictions = await aiOptimizer.generatePredictions();
      setPredictions(aiPredictions);
      
      const performancePatterns = aiOptimizer.getPerformancePatterns();
      setPatterns(performancePatterns);
    } catch (error) {
      console.error('Error loading AI dashboard data:', error);
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const newSuggestions = await aiUtils.quickAnalysis();
      setSuggestions(newSuggestions);
    } catch (error) {
      console.error('Error during analysis:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTrainModel = async () => {
    setIsTraining(true);
    try {
      await aiUtils.trainModel();
      const status = aiUtils.getModelStatus();
      setModelStatus(status);
    } catch (error) {
      console.error('Error training model:', error);
    } finally {
      setIsTraining(false);
    }
  };

  const handleExportData = () => {
    const data = aiUtils.exportData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-optimization-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'performance': return <Zap className="h-4 w-4" />;
      case 'security': return <Shield className="h-4 w-4" />;
      case 'accessibility': return <Accessibility className="h-4 w-4" />;
      case 'seo': return <Search className="h-4 w-4" />;
      case 'ux': return <TrendingUp className="h-4 w-4" />;
      default: return <Lightbulb className="h-4 w-4" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'in-progress': return <Clock className="h-4 w-4 text-blue-500" />;
      case 'pending': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'rejected': return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getImpactScore = (suggestion: OptimizationSuggestion) => {
    const scores = Object.values(suggestion.impact);
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Brain className="h-8 w-8 text-purple-600" />
            AI Optimization Dashboard
          </h2>
          <p className="text-muted-foreground">
            Intelligent performance optimization powered by machine learning
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            variant="outline"
            className="flex items-center gap-2"
          >
            {isAnalyzing ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Activity className="h-4 w-4" />
            )}
            {isAnalyzing ? 'Analyzing...' : 'Analyze'}
          </Button>
          <Button
            onClick={handleTrainModel}
            disabled={isTraining}
            variant="outline"
            className="flex items-center gap-2"
          >
            {isTraining ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Brain className="h-4 w-4" />
            )}
            {isTraining ? 'Training...' : 'Train Model'}
          </Button>
          <Button
            onClick={handleExportData}
            variant="outline"
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Export Data
          </Button>
        </div>
      </div>

      {/* Model Status */}
      {modelStatus && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Model Version</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{modelStatus.version}</div>
              <p className="text-xs text-muted-foreground">
                {modelStatus.isTraining ? 'Training in progress' : 'Ready for analysis'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{modelStatus.successRate.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                Optimization success rate
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Suggestions</CardTitle>
              <Lightbulb className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{modelStatus.totalSuggestions}</div>
              <p className="text-xs text-muted-foreground">
                Total optimization suggestions
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Training Data</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{modelStatus.trainingDataPoints}</div>
              <p className="text-xs text-muted-foreground">
                Data points for training
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Tabs defaultValue="suggestions" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="suggestions" className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Suggestions
          </TabsTrigger>
          <TabsTrigger value="predictions" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Predictions
          </TabsTrigger>
          <TabsTrigger value="patterns" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Patterns
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="suggestions" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {suggestions.map((suggestion) => (
              <Card 
                key={suggestion.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setSelectedSuggestion(suggestion)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getTypeIcon(suggestion.type)}
                      <CardTitle className="text-lg">{suggestion.title}</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(suggestion.status)}
                      <Badge className={getPriorityColor(suggestion.priority)}>
                        {suggestion.priority}
                      </Badge>
                    </div>
                  </div>
                  <CardDescription>{suggestion.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Impact Score</span>
                      <span className="text-sm font-bold">{getImpactScore(suggestion)}/100</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Confidence</span>
                      <span className="text-sm font-bold">{suggestion.confidence}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Effort</span>
                      <Badge variant="outline">{suggestion.effort}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Estimated Time</span>
                      <span className="text-sm">{suggestion.estimatedTime}</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {suggestion.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {predictions.map((prediction, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    <CardTitle className="text-lg capitalize">
                      {prediction.type.replace('_', ' ')} Prediction
                    </CardTitle>
                  </div>
                  <CardDescription>
                    Confidence: {prediction.confidence}% | Timeframe: {prediction.timeframe}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium mb-2">Prediction</h4>
                      <pre className="text-xs bg-muted p-2 rounded overflow-auto">
                        {JSON.stringify(prediction.prediction, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Recommendations</h4>
                      <ul className="text-sm space-y-1">
                        {prediction.recommendations.map((rec, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-muted-foreground">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="patterns" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {patterns.length > 0 ? (
              patterns.map((pattern) => (
                <Card key={pattern.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{pattern.name}</CardTitle>
                    <CardDescription>{pattern.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Category</span>
                        <Badge variant="outline">{pattern.category}</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Frequency</span>
                        <span className="text-sm font-bold">{pattern.frequency}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Impact</span>
                        <span className="text-sm font-bold">{pattern.impact}/100</span>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Recommendations</h4>
                        <ul className="text-sm space-y-1">
                          {pattern.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-muted-foreground">•</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card className="col-span-2">
                <CardContent className="flex items-center justify-center py-8">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No Patterns Detected</h3>
                    <p className="text-muted-foreground">
                      Run analysis to detect performance patterns and optimization opportunities.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Optimization Impact</CardTitle>
                <CardDescription>
                  Average improvement across all implemented optimizations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Performance</span>
                    <span className="text-sm font-bold">+42%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Security</span>
                    <span className="text-sm font-bold">+38%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Accessibility</span>
                    <span className="text-sm font-bold">+35%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">User Experience</span>
                    <span className="text-sm font-bold">+45%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Implementation Status</CardTitle>
                <CardDescription>
                  Current status of optimization suggestions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Completed</span>
                    <span className="text-sm font-bold text-green-600">
                      {suggestions.filter(s => s.status === 'completed').length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">In Progress</span>
                    <span className="text-sm font-bold text-blue-600">
                      {suggestions.filter(s => s.status === 'in-progress').length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Pending</span>
                    <span className="text-sm font-bold text-yellow-600">
                      {suggestions.filter(s => s.status === 'pending').length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Rejected</span>
                    <span className="text-sm font-bold text-red-600">
                      {suggestions.filter(s => s.status === 'rejected').length}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Suggestion Detail Modal */}
      {selectedSuggestion && (
        <Card className="fixed inset-4 z-50 overflow-auto">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getTypeIcon(selectedSuggestion.type)}
                <CardTitle className="text-xl">{selectedSuggestion.title}</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedSuggestion(null)}
              >
                ×
              </Button>
            </div>
            <CardDescription>{selectedSuggestion.description}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Impact Analysis</h4>
                <div className="space-y-2">
                  {Object.entries(selectedSuggestion.impact).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{key}</span>
                      <span className="text-sm font-bold">{value}/100</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-3">Implementation Details</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Effort</span>
                    <Badge variant="outline">{selectedSuggestion.effort}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Estimated Time</span>
                    <span className="text-sm">{selectedSuggestion.estimatedTime}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Confidence</span>
                    <span className="text-sm font-bold">{selectedSuggestion.confidence}%</span>
                  </div>
                </div>
              </div>
            </div>

            {selectedSuggestion.codeExample && (
              <div>
                <h4 className="font-medium mb-3">Code Example</h4>
                <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                  {selectedSuggestion.codeExample}
                </pre>
              </div>
            )}

            <div>
              <h4 className="font-medium mb-3">Implementation Steps</h4>
              <ol className="list-decimal list-inside space-y-2">
                {selectedSuggestion.implementation.steps.map((step, index) => (
                  <li key={index} className="text-sm">{step}</li>
                ))}
              </ol>
            </div>

            <div>
              <h4 className="font-medium mb-3">Expected Metrics</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {Object.values(selectedSuggestion.metrics.before)[0]}
                  </div>
                  <div className="text-sm text-muted-foreground">Before</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {Object.values(selectedSuggestion.metrics.after)[0]}
                  </div>
                  <div className="text-sm text-muted-foreground">After</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    +{selectedSuggestion.metrics.improvement}%
                  </div>
                  <div className="text-sm text-muted-foreground">Improvement</div>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => {
                  aiOptimizer.markSuggestionCompleted(selectedSuggestion.id);
                  setSelectedSuggestion(null);
                  loadInitialData();
                }}
                className="flex items-center gap-2"
              >
                <CheckCircle className="h-4 w-4" />
                Mark as Completed
              </Button>
              <Button variant="outline" onClick={() => setSelectedSuggestion(null)}>
                Close
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}



