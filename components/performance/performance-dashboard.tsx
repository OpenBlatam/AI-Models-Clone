'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { AdvancedButton, PrimaryButton, SecondaryButton } from '@/components/ui/advanced-button';
import { 
  Activity, 
  Clock, 
  Zap, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  TrendingUp, 
  TrendingDown, 
  Eye, 
  EyeOff,
  RefreshCw,
  Download,
  Settings,
  BarChart3,
  Gauge,
  HardDrive,
  Wifi,
  Smartphone
} from 'lucide-react';
import { usePerformance } from '@/hooks/usePerformance';
import { checkPerformanceBudget } from '@/lib/performance';

export interface PerformanceDashboardProps {
  showDetails?: boolean;
  enableMonitoring?: boolean;
  refreshInterval?: number;
  showRecommendations?: boolean;
  className?: string;
}

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  status: 'good' | 'warning' | 'poor';
  target: number;
  description: string;
}

export interface PerformanceRecommendation {
  id: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'easy' | 'medium' | 'hard';
  category: 'performance' | 'accessibility' | 'seo' | 'security';
}

export function PerformanceDashboard({
  showDetails = true,
  enableMonitoring = true,
  refreshInterval = 5000,
  showRecommendations = true,
  className = '',
}: PerformanceDashboardProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  
  const performance = usePerformance();
  
  // Performance metrics with targets
  const metrics: PerformanceMetric[] = useMemo(() => [
    {
      name: 'First Contentful Paint',
      value: performance.firstContentfulPaint,
      unit: 'ms',
      status: performance.firstContentfulPaint < 2000 ? 'good' : performance.firstContentfulPaint < 4000 ? 'warning' : 'poor',
      target: 2000,
      description: 'Time until first content is painted on screen',
    },
    {
      name: 'Largest Contentful Paint',
      value: performance.largestContentfulPaint,
      unit: 'ms',
      status: performance.largestContentfulPaint < 2500 ? 'good' : performance.largestContentfulPaint < 4000 ? 'warning' : 'poor',
      target: 2500,
      description: 'Time until largest content is painted on screen',
    },
    {
      name: 'First Input Delay',
      value: performance.firstInputDelay,
      unit: 'ms',
      status: performance.firstInputDelay < 100 ? 'good' : performance.firstInputDelay < 300 ? 'warning' : 'poor',
      target: 100,
      description: 'Time from first interaction to response',
    },
    {
      name: 'Cumulative Layout Shift',
      value: performance.cumulativeLayoutShift,
      unit: '',
      status: performance.cumulativeLayoutShift < 0.1 ? 'good' : performance.cumulativeLayoutShift < 0.25 ? 'warning' : 'poor',
      target: 0.1,
      description: 'Measure of visual stability',
    },
    {
      name: 'Time to First Byte',
      value: performance.timeToFirstByte,
      unit: 'ms',
      status: performance.timeToFirstByte < 800 ? 'good' : performance.timeToFirstByte < 1800 ? 'warning' : 'poor',
      target: 800,
      description: 'Time until first byte is received',
    },
    {
      name: 'Time to Interactive',
      value: performance.timeToInteractive,
      unit: 'ms',
      status: performance.timeToInteractive < 3500 ? 'good' : performance.timeToInteractive < 7300 ? 'warning' : 'poor',
      target: 3500,
      description: 'Time until page is fully interactive',
    },
  ], [performance]);

  // Performance score calculation
  const performanceScore = useMemo(() => {
    const scores = metrics.map(metric => {
      const ratio = metric.value / metric.target;
      if (ratio <= 1) return 100; // Good
      if (ratio <= 2) return 100 - (ratio - 1) * 30; // Warning
      return Math.max(0, 100 - (ratio - 1) * 50); // Poor
    });
    
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }, [metrics]);

  // Performance budget violations
  const budgetViolations = useMemo(() => {
    const metricsData = {
      fcp: performance.firstContentfulPaint,
      lcp: performance.largestContentfulPaint,
      fid: performance.firstInputDelay,
      cls: performance.cumulativeLayoutShift,
      ttfb: performance.timeToFirstByte,
      tti: performance.timeToInteractive,
    };
    
    return checkPerformanceBudget(metricsData);
  }, [performance]);

  // Performance recommendations
  const recommendations: PerformanceRecommendation[] = useMemo(() => {
    const recs: PerformanceRecommendation[] = [];
    
    if (performance.firstContentfulPaint > 2000) {
      recs.push({
        id: 'fcp-optimization',
        title: 'Optimize First Contentful Paint',
        description: 'Reduce server response time, optimize critical resources, and eliminate render-blocking resources',
        impact: 'high',
        effort: 'medium',
        category: 'performance',
      });
    }
    
    if (performance.largestContentfulPaint > 2500) {
      recs.push({
        id: 'lcp-optimization',
        title: 'Optimize Largest Contentful Paint',
        description: 'Optimize images, use efficient image formats, and implement lazy loading',
        impact: 'high',
        effort: 'medium',
        category: 'performance',
      });
    }
    
    if (performance.cumulativeLayoutShift > 0.1) {
      recs.push({
        id: 'cls-optimization',
        title: 'Reduce Cumulative Layout Shift',
        description: 'Set explicit dimensions for images and avoid inserting content above existing content',
        impact: 'medium',
        effort: 'easy',
        category: 'performance',
      });
    }
    
    if (performance.firstInputDelay > 100) {
      recs.push({
        id: 'fid-optimization',
        title: 'Improve First Input Delay',
        description: 'Reduce JavaScript execution time and optimize event handlers',
        impact: 'high',
        effort: 'hard',
        category: 'performance',
      });
    }
    
    return recs;
  }, [performance]);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh || !enableMonitoring) return;
    
    const interval = setInterval(() => {
      // Trigger performance measurement refresh
      if (typeof window !== 'undefined' && 'performance' in window) {
        performance.getEntriesByType('navigation');
      }
    }, refreshInterval);
    
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, enableMonitoring]);

  // Handle metric selection
  const handleMetricToggle = useCallback((metricName: string) => {
    setSelectedMetrics(prev => 
      prev.includes(metricName) 
        ? prev.filter(name => name !== metricName)
        : [...prev, metricName]
    );
  }, []);

  // Export performance data
  const exportPerformanceData = useCallback(() => {
    const data = {
      timestamp: new Date().toISOString(),
      metrics,
      performanceScore,
      budgetViolations,
      recommendations,
      rawData: performance,
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [metrics, performanceScore, budgetViolations, recommendations, performance]);

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'poor': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // Get impact color
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <AdvancedButton
          onClick={() => setIsVisible(true)}
          leftIcon={<BarChart3 className="w-4 h-4" />}
          variant="outline"
          size="sm"
        >
          Performance
        </AdvancedButton>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-4 right-4 z-50 w-96 max-h-[80vh] overflow-hidden ${className}`}>
      <div className="bg-white rounded-lg shadow-xl border border-gray-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <h3 className="font-semibold">Performance Dashboard</h3>
            </div>
            <div className="flex items-center space-x-2">
              <AdvancedButton
                size="sm"
                variant="ghost"
                onClick={() => setIsExpanded(!isExpanded)}
                leftIcon={isExpanded ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                className="text-white hover:bg-white/20"
              >
                {isExpanded ? 'Collapse' : 'Expand'}
              </AdvancedButton>
              <AdvancedButton
                size="sm"
                variant="ghost"
                onClick={() => setIsVisible(false)}
                leftIcon={<X className="w-4 h-4" />}
                className="text-white hover:bg-white/20"
              />
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4 max-h-[calc(80vh-80px)] overflow-y-auto">
          {/* Performance Score */}
          <div className="text-center">
            <div className="relative inline-flex items-center justify-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                <span className="text-2xl font-bold text-white">{performanceScore}</span>
              </div>
              <div className="absolute -top-2 -right-2">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  performanceScore >= 90 ? 'bg-green-500' : performanceScore >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                }`}>
                  {performanceScore >= 90 ? (
                    <CheckCircle className="w-4 h-4 text-white" />
                  ) : performanceScore >= 70 ? (
                    <AlertTriangle className="w-4 h-4 text-white" />
                  ) : (
                    <X className="w-4 h-4 text-white" />
                  )}
                </div>
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-2">Performance Score</p>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between">
            <AdvancedButton
              size="sm"
              variant="outline"
              onClick={() => setAutoRefresh(!autoRefresh)}
              leftIcon={autoRefresh ? <RefreshCw className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
            >
              {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
            </AdvancedButton>
            
            <AdvancedButton
              size="sm"
              variant="outline"
              onClick={exportPerformanceData}
              leftIcon={<Download className="w-4 h-4" />}
            >
              Export
            </AdvancedButton>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-3">
            {metrics.map((metric) => (
              <div
                key={metric.name}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedMetrics.includes(metric.name) 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleMetricToggle(metric.name)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-gray-600 truncate">
                    {metric.name}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(metric.status)}`}>
                    {metric.status}
                  </span>
                </div>
                <div className="text-lg font-bold text-gray-900">
                  {metric.value.toLocaleString()}
                  <span className="text-sm text-gray-500 ml-1">{metric.unit}</span>
                </div>
                <div className="text-xs text-gray-500">
                  Target: {metric.target.toLocaleString()}{metric.unit}
                </div>
              </div>
            ))}
          </div>

          {/* Budget Violations */}
          {budgetViolations.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <h4 className="text-sm font-medium text-red-800 mb-2 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Performance Budget Violations
              </h4>
              <ul className="text-xs text-red-700 space-y-1">
                {budgetViolations.map((violation, index) => (
                  <li key={index}>• {violation}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {showRecommendations && recommendations.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-900 flex items-center">
                <Info className="w-4 h-4 mr-2" />
                Optimization Recommendations
              </h4>
              {recommendations.map((rec) => (
                <div key={rec.id} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <div className="flex items-start justify-between mb-2">
                    <h5 className="text-sm font-medium text-gray-900">{rec.title}</h5>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(rec.impact)}`}>
                      {rec.impact} impact
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mb-2">{rec.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      Effort: <span className="font-medium">{rec.effort}</span>
                    </span>
                    <span className="text-xs text-gray-500">
                      Category: <span className="font-medium">{rec.category}</span>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Detailed Metrics */}
          {isExpanded && showDetails && (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-900">Detailed Metrics</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Page Load Time:</span>
                  <span className="font-medium">{performance.pageLoadTime.toFixed(2)}ms</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">DOM Content Loaded:</span>
                  <span className="font-medium">{performance.domContentLoaded.toFixed(2)}ms</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Resource Count:</span>
                  <span className="font-medium">{performance.resourceCount}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Total Transfer Size:</span>
                  <span className="font-medium">{(performance.totalTransferSize / 1024 / 1024).toFixed(2)}MB</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Missing icon component
const X = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);
