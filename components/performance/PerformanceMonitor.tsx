'use client';

import React, { useState, useEffect } from 'react';
import { usePerformance } from '@/hooks/usePerformance';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
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
  EyeOff
} from 'lucide-react';

interface PerformanceScore {
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  color: string;
  status: 'excellent' | 'good' | 'needs-improvement' | 'poor';
}

export function PerformanceMonitor() {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [optimizationTips, setOptimizationTips] = useState<string[]>([]);
  
  const {
    metrics,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    resetMetrics,
    performanceScore,
  } = usePerformance();

  // Calculate performance score and grade
  const getPerformanceScore = (): PerformanceScore => {
    let score = 100;
    const tips: string[] = [];

    // FCP scoring
    if (metrics.firstContentfulPaint > 1800) {
      score -= 20;
      tips.push('First Contentful Paint is slow. Consider optimizing critical rendering path.');
    } else if (metrics.firstContentfulPaint > 1000) {
      score -= 10;
      tips.push('First Contentful Paint could be improved.');
    }

    // LCP scoring
    if (metrics.largestContentfulPaint > 4000) {
      score -= 25;
      tips.push('Largest Contentful Paint is very slow. Optimize images and reduce layout shifts.');
    } else if (metrics.largestContentfulPaint > 2500) {
      score -= 15;
      tips.push('Largest Contentful Paint needs improvement.');
    }

    // CLS scoring
    if (metrics.cumulativeLayoutShift > 0.25) {
      score -= 25;
      tips.push('Cumulative Layout Shift is high. Fix layout stability issues.');
    } else if (metrics.cumulativeLayoutShift > 0.1) {
      score -= 15;
      tips.push('Cumulative Layout Shift could be improved.');
    }

    // FID scoring
    if (metrics.firstInputDelay > 300) {
      score -= 20;
      tips.push('First Input Delay is high. Reduce JavaScript execution time.');
    } else if (metrics.firstInputDelay > 100) {
      score -= 10;
      tips.push('First Input Delay could be improved.');
    }

    const finalScore = Math.max(0, score);
    
    let grade: PerformanceScore['grade'];
    let color: string;
    let status: PerformanceScore['status'];

    if (finalScore >= 90) {
      grade = 'A';
      color = 'text-green-600';
      status = 'excellent';
    } else if (finalScore >= 80) {
      grade = 'B';
      color = 'text-blue-600';
      status = 'good';
    } else if (finalScore >= 60) {
      grade = 'C';
      color = 'text-yellow-600';
      status = 'needs-improvement';
    } else if (finalScore >= 40) {
      grade = 'D';
      color = 'text-orange-600';
      status = 'needs-improvement';
    } else {
      grade = 'F';
      color = 'text-red-600';
      status = 'poor';
    }

    setOptimizationTips(tips);

    return { score: finalScore, grade, color, status };
  };

  const performanceData = getPerformanceScore();

  // Auto-start monitoring on mount
  useEffect(() => {
    if (!isMonitoring) {
      startMonitoring();
    }
  }, [isMonitoring, startMonitoring]);

  // Format time values
  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  // Get status icon
  const getStatusIcon = () => {
    switch (performanceData.status) {
      case 'excellent':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'good':
        return <TrendingUp className="w-5 h-5 text-blue-600" />;
      case 'needs-improvement':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'poor':
        return <TrendingDown className="w-5 h-5 text-red-600" />;
      default:
        return <Info className="w-5 h-5 text-gray-600" />;
    }
  };

  if (!isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={() => setIsVisible(true)}
          variant="outline"
          size="sm"
          className="bg-white/90 backdrop-blur-sm shadow-lg"
        >
          <Activity className="w-4 h-4 mr-2" />
          Performance
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80">
      <Card className="bg-white/95 backdrop-blur-sm shadow-xl border-0">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Performance Monitor
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                onClick={() => setShowDetails(!showDetails)}
                variant="ghost"
                size="sm"
              >
                {showDetails ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
              <Button
                onClick={() => setIsVisible(false)}
                variant="ghost"
                size="sm"
              >
                ×
              </Button>
            </div>
          </div>
          
          {/* Performance Score */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{performanceData.score}</span>
              <Badge className={`text-lg px-2 py-1 ${performanceData.color}`}>
                {performanceData.grade}
              </Badge>
            </div>
            {getStatusIcon()}
          </div>
          
          {/* Progress Bar */}
          <Progress value={performanceData.score} className="h-2" />
        </CardHeader>

        <CardContent className="pt-0">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">FCP</div>
              <div className="font-semibold">{formatTime(metrics.firstContentfulPaint)}</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">LCP</div>
              <div className="font-semibold">{formatTime(metrics.largestContentfulPaint)}</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">CLS</div>
              <div className="font-semibold">{metrics.cumulativeLayoutShift.toFixed(3)}</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-sm text-gray-600">FID</div>
              <div className="font-semibold">{formatTime(metrics.firstInputDelay)}</div>
            </div>
          </div>

          {/* Detailed Metrics */}
          {showDetails && (
            <div className="space-y-3 mb-4">
              <div className="flex justify-between text-sm">
                <span>Page Load Time:</span>
                <span className="font-mono">{formatTime(metrics.pageLoadTime)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Time to First Byte:</span>
                <span className="font-mono">{formatTime(metrics.timeToFirstByte)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Time to Interactive:</span>
                <span className="font-mono">{formatTime(metrics.timeToInteractive)}</span>
              </div>
            </div>
          )}

          {/* Optimization Tips */}
          {optimizationTips.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
                Optimization Tips
              </h4>
              <ul className="text-xs text-gray-600 space-y-1">
                {optimizationTips.slice(0, 3).map((tip, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-yellow-600 mt-1">•</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <Button
              onClick={isMonitoring ? stopMonitoring : startMonitoring}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              {isMonitoring ? 'Stop' : 'Start'} Monitoring
            </Button>
            <Button
              onClick={resetMetrics}
              variant="ghost"
              size="sm"
            >
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Higher-order component for wrapping components with performance monitoring
export function withPerformanceMonitoring<P extends object>(
  Component: React.ComponentType<P>,
  componentName: string
) {
  return function WithPerformanceMonitoring(props: P) {
    const { measureOperation } = useComponentPerformance(componentName);
    
    return (
      <div>
        <Component {...props} />
        <PerformanceMonitor />
      </div>
    );
  };
}
