import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Share } from 'react-native';
import { OptimizedTranslatedText } from '../i18n-components/OptimizedTranslatedText';
import { appOptimizer, generateOptimizationReport } from '../../utils/optimization/AppOptimizer';
import { componentOptimizer, generateComponentReport } from '../../utils/optimization/ComponentOptimizer';
import { bundleOptimizer, generateBundleReport } from '../../utils/optimization/BundleOptimizer';
import { performanceMonitor } from '../../utils/performance/PerformanceMonitor';
import { cacheManager } from '../../utils/caching/CacheManager';
import { analytics } from '../../utils/analytics/AnalyticsService';
import { securityManager } from '../../utils/security/SecurityManager';

interface OptimizationReportProps {
  onClose?: () => void;
  style?: any;
}

interface ReportSectionProps {
  title: string;
  children: React.ReactNode;
  expanded?: boolean;
  onToggle?: () => void;
}

const ReportSection: React.FC<ReportSectionProps> = ({ title, children, expanded = true, onToggle }) => (
  <View style={styles.section}>
    <TouchableOpacity
      style={styles.sectionHeader}
      onPress={onToggle}
      disabled={!onToggle}
    >
      <Text style={styles.sectionTitle}>{title}</Text>
      {onToggle && (
        <Text style={styles.expandIcon}>{expanded ? '▼' : '▶'}</Text>
      )}
    </TouchableOpacity>
    {expanded && <View style={styles.sectionContent}>{children}</View>}
  </View>
);

interface MetricRowProps {
  label: string;
  value: string | number;
  unit?: string;
  status?: 'excellent' | 'good' | 'warning' | 'critical';
}

const MetricRow: React.FC<MetricRowProps> = ({ label, value, unit, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'excellent': return '#4CAF50';
      case 'good': return '#8BC34A';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#666';
    }
  };

  return (
    <View style={styles.metricRow}>
      <Text style={styles.metricLabel}>{label}</Text>
      <View style={styles.metricValue}>
        <Text style={[styles.metricValueText, { color: getStatusColor() }]}>
          {value}{unit && ` ${unit}`}
        </Text>
        {status && (
          <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
        )}
      </View>
    </View>
  );
};

interface RecommendationItemProps {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  impact: string;
}

const RecommendationItem: React.FC<RecommendationItemProps> = ({ title, description, priority, impact }) => {
  const getPriorityColor = () => {
    switch (priority) {
      case 'high': return '#F44336';
      case 'medium': return '#FF9800';
      case 'low': return '#4CAF50';
      default: return '#666';
    }
  };

  return (
    <View style={styles.recommendationItem}>
      <View style={styles.recommendationHeader}>
        <Text style={styles.recommendationTitle}>{title}</Text>
        <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor() }]}>
          <Text style={styles.priorityText}>{priority.toUpperCase()}</Text>
        </View>
      </View>
      <Text style={styles.recommendationDescription}>{description}</Text>
      <Text style={styles.impactText}>Impact: {impact}</Text>
    </View>
  );
};

export const OptimizationReport: React.FC<OptimizationReportProps> = ({
  onClose,
  style,
}) => {
  const [reports, setReports] = useState<any>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    app: true,
    component: true,
    bundle: true,
    performance: true,
    cache: true,
    security: true,
    recommendations: true,
  });

  // Generate reports
  const generateReports = async () => {
    try {
      const appReport = appOptimizer.generateReport();
      const componentReport = generateComponentReport();
      const bundleReport = generateBundleReport();
      const performanceReport = performanceMonitor.getReport();
      const cacheStats = cacheManager.getStats();
      const securityMetrics = securityManager.getSecurityMetrics();

      setReports({
        app: appReport,
        component: componentReport,
        bundle: bundleReport,
        performance: performanceReport,
        cache: cacheStats,
        security: securityMetrics,
      });
    } catch (error) {
      console.error('Failed to generate reports:', error);
    }
  };

  // Generate recommendations
  const generateRecommendations = () => {
    const recommendations: RecommendationItemProps[] = [];

    // Bundle size recommendations
    if (reports.app?.bundleSize > 10 * 1024 * 1024) {
      recommendations.push({
        title: 'Reduce Bundle Size',
        description: 'Consider implementing code splitting and removing unused dependencies',
        priority: 'high',
        impact: 'High - 30-50% size reduction',
      });
    }

    // Memory usage recommendations
    if (reports.app?.memoryUsage > 100 * 1024 * 1024) {
      recommendations.push({
        title: 'Optimize Memory Usage',
        description: 'Implement memory cleanup and optimize image caching',
        priority: 'high',
        impact: 'High - 20-40% memory reduction',
      });
    }

    // Cache hit rate recommendations
    if (reports.cache?.hitRate < 0.7) {
      recommendations.push({
        title: 'Improve Cache Strategy',
        description: 'Optimize cache policies and implement intelligent prefetching',
        priority: 'medium',
        impact: 'Medium - 15-25% performance improvement',
      });
    }

    // Render time recommendations
    if (reports.app?.renderTime > 16) {
      recommendations.push({
        title: 'Optimize Component Rendering',
        description: 'Implement React.memo and optimize component re-renders',
        priority: 'medium',
        impact: 'Medium - 20-30% render time improvement',
      });
    }

    // Security recommendations
    if (reports.security?.failedLoginAttempts > 5) {
      recommendations.push({
        title: 'Enhance Security Measures',
        description: 'Implement rate limiting and additional authentication layers',
        priority: 'high',
        impact: 'High - Improved security posture',
      });
    }

    return recommendations;
  };

  // Share report
  const handleShare = async () => {
    try {
      const reportText = `
Optimization Report - ${new Date().toLocaleDateString()}

${reports.app || 'No app report available'}
${reports.component || 'No component report available'}
${reports.bundle || 'No bundle report available'}
${reports.performance || 'No performance report available'}

Generated by Blatam Academy Optimization System
      `.trim();

      await Share.share({
        message: reportText,
        title: 'Optimization Report',
      });
    } catch (error) {
      console.error('Failed to share report:', error);
    }
  };

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Load reports on mount
  useEffect(() => {
    generateReports();
  }, []);

  const recommendations = generateRecommendations();

  return (
    <ScrollView style={[styles.container, style]} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <OptimizedTranslatedText
          translationKey="optimization.report.title"
          style={styles.title}
        />
        <Text style={styles.subtitle}>
          Generated on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
        </Text>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
          <OptimizedTranslatedText
            translationKey="optimization.report.share"
            style={styles.shareButtonText}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.refreshButton} onPress={generateReports}>
          <OptimizedTranslatedText
            translationKey="optimization.report.refresh"
            style={styles.refreshButtonText}
          />
        </TouchableOpacity>

        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
          <OptimizedTranslatedText
            translationKey="optimization.report.close"
            style={styles.closeButtonText}
          />
        </TouchableOpacity>
      </View>

      {/* App Optimization Report */}
      <ReportSection
        title="App Optimization"
        expanded={expandedSections.app}
        onToggle={() => toggleSection('app')}
      >
        <Text style={styles.reportText}>{reports.app || 'No app optimization data available'}</Text>
      </ReportSection>

      {/* Component Optimization Report */}
      <ReportSection
        title="Component Optimization"
        expanded={expandedSections.component}
        onToggle={() => toggleSection('component')}
      >
        <Text style={styles.reportText}>{reports.component || 'No component optimization data available'}</Text>
      </ReportSection>

      {/* Bundle Optimization Report */}
      <ReportSection
        title="Bundle Optimization"
        expanded={expandedSections.bundle}
        onToggle={() => toggleSection('bundle')}
      >
        <Text style={styles.reportText}>{reports.bundle || 'No bundle optimization data available'}</Text>
      </ReportSection>

      {/* Performance Metrics */}
      <ReportSection
        title="Performance Metrics"
        expanded={expandedSections.performance}
        onToggle={() => toggleSection('performance')}
      >
        <MetricRow
          label="Bundle Size"
          value={reports.app?.bundleSize ? (reports.app.bundleSize / (1024 * 1024)).toFixed(2) : '0'}
          unit="MB"
          status={reports.app?.bundleSize > 15 * 1024 * 1024 ? 'critical' : reports.app?.bundleSize > 10 * 1024 * 1024 ? 'warning' : 'good'}
        />
        <MetricRow
          label="Memory Usage"
          value={reports.app?.memoryUsage ? (reports.app.memoryUsage / (1024 * 1024)).toFixed(2) : '0'}
          unit="MB"
          status={reports.app?.memoryUsage > 150 * 1024 * 1024 ? 'critical' : reports.app?.memoryUsage > 100 * 1024 * 1024 ? 'warning' : 'good'}
        />
        <MetricRow
          label="Render Time"
          value={reports.app?.renderTime ? reports.app.renderTime.toFixed(2) : '0'}
          unit="ms"
          status={reports.app?.renderTime > 33 ? 'critical' : reports.app?.renderTime > 16 ? 'warning' : 'excellent'}
        />
        <MetricRow
          label="Startup Time"
          value={reports.app?.startupTime ? reports.app.startupTime.toFixed(2) : '0'}
          unit="ms"
          status={reports.app?.startupTime > 3000 ? 'critical' : reports.app?.startupTime > 2000 ? 'warning' : 'good'}
        />
      </ReportSection>

      {/* Cache Performance */}
      <ReportSection
        title="Cache Performance"
        expanded={expandedSections.cache}
        onToggle={() => toggleSection('cache')}
      >
        <MetricRow
          label="Cache Hit Rate"
          value={reports.cache?.hitRate ? (reports.cache.hitRate * 100).toFixed(1) : '0'}
          unit="%"
          status={(reports.cache?.hitRate || 0) < 0.6 ? 'critical' : (reports.cache?.hitRate || 0) < 0.75 ? 'warning' : 'excellent'}
        />
        <MetricRow
          label="Cache Size"
          value={reports.cache?.totalSize ? (reports.cache.totalSize / 1024).toFixed(2) : '0'}
          unit="KB"
          status={reports.cache?.totalSize > 10 * 1024 * 1024 ? 'warning' : 'good'}
        />
        <MetricRow
          label="Cache Entries"
          value={reports.cache?.entryCount || 0}
          unit="entries"
        />
      </ReportSection>

      {/* Security Metrics */}
      <ReportSection
        title="Security Metrics"
        expanded={expandedSections.security}
        onToggle={() => toggleSection('security')}
      >
        <MetricRow
          label="Failed Login Attempts"
          value={reports.security?.failedLoginAttempts || 0}
          unit="attempts"
          status={(reports.security?.failedLoginAttempts || 0) > 10 ? 'critical' : (reports.security?.failedLoginAttempts || 0) > 5 ? 'warning' : 'good'}
        />
        <MetricRow
          label="Active Sessions"
          value={reports.security?.activeSessions || 0}
          unit="sessions"
        />
        <MetricRow
          label="Security Score"
          value={reports.security?.securityScore ? reports.security.securityScore.toFixed(1) : '0'}
          unit="%"
          status={(reports.security?.securityScore || 0) < 60 ? 'critical' : (reports.security?.securityScore || 0) < 80 ? 'warning' : 'excellent'}
        />
      </ReportSection>

      {/* Recommendations */}
      <ReportSection
        title={`Optimization Recommendations (${recommendations.length})`}
        expanded={expandedSections.recommendations}
        onToggle={() => toggleSection('recommendations')}
      >
        {recommendations.length > 0 ? (
          recommendations.map((recommendation, index) => (
            <RecommendationItem
              key={index}
              title={recommendation.title}
              description={recommendation.description}
              priority={recommendation.priority}
              impact={recommendation.impact}
            />
          ))
        ) : (
          <Text style={styles.noRecommendationsText}>
            No optimization recommendations at this time. Your app is performing well!
          </Text>
        )}
      </ReportSection>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  actionButtons: {
    flexDirection: 'row',
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  shareButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 6,
    marginRight: 10,
    alignItems: 'center',
  },
  shareButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  refreshButton: {
    flex: 1,
    backgroundColor: '#34C759',
    padding: 12,
    borderRadius: 6,
    marginRight: 10,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  closeButton: {
    flex: 1,
    backgroundColor: '#FF3B30',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  section: {
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  expandIcon: {
    fontSize: 16,
    color: '#666',
  },
  sectionContent: {
    padding: 20,
  },
  reportText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
    fontFamily: 'monospace',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  metricLabel: {
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  metricValue: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metricValueText: {
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  recommendationItem: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {
    fontSize: 10,
    color: '#fff',
    fontWeight: 'bold',
  },
  recommendationDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
  impactText: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  noRecommendationsText: {
    fontSize: 14,
    color: '#4CAF50',
    textAlign: 'center',
    fontStyle: 'italic',
  },
}); 