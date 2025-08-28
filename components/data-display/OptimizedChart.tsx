import React, { useMemo, useCallback } from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { OptimizedIcon } from './OptimizedIcon';

// ============================================================================
// TYPES
// ============================================================================

interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  icon?: string;
}

interface ChartProps {
  data: ChartDataPoint[];
  type: 'bar' | 'line' | 'pie' | 'doughnut';
  title?: string;
  subtitle?: string;
  isLoading?: boolean;
  hasError?: boolean;
  errorMessage?: string;
  emptyMessage?: string;
  canAnimate?: boolean;
  canInteract?: boolean;
  maxHeight?: number;
  onDataPointPress?: (dataPoint: ChartDataPoint) => void;
}

interface ChartDimensions {
  width: number;
  height: number;
  padding: number;
  barWidth: number;
  barSpacing: number;
}

interface ChartCalculations {
  maxValue: number;
  minValue: number;
  totalValue: number;
  averageValue: number;
  percentageValues: number[];
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const CHART_COLORS = {
  primary: '#007AFF',
  secondary: '#5AC8FA',
  success: '#34C759',
  warning: '#FF9500',
  error: '#FF3B30',
  info: '#5856D6',
  default: '#8E8E93',
} as const;

const CHART_DIMENSIONS = {
  containerPadding: 16,
  chartPadding: 20,
  barHeight: 200,
  lineHeight: 150,
  pieSize: 200,
  labelHeight: 20,
  legendSpacing: 8,
} as const;

const ANIMATION_CONFIG = {
  duration: 1000,
  easing: 'ease-out',
  delay: 100,
} as const;

const CHART_ICONS = {
  bar: 'bar-chart',
  line: 'trending-up',
  pie: 'pie-chart',
  doughnut: 'circle',
  loading: 'refresh',
  error: 'warning',
  empty: 'information-circle',
} as const;

// ============================================================================
// HELPERS
// ============================================================================

const calculateChartDimensions = (containerWidth: number, type: string): ChartDimensions => {
  const padding = CHART_DIMENSIONS.chartPadding;
  const width = containerWidth - (padding * 2);
  
  let height: number;
  let barWidth: number;
  let barSpacing: number;
  
  switch (type) {
    case 'bar':
      height = CHART_DIMENSIONS.barHeight;
      barWidth = Math.max(20, width / 10);
      barSpacing = Math.max(8, (width - (barWidth * 5)) / 6);
      break;
    case 'line':
      height = CHART_DIMENSIONS.lineHeight;
      barWidth = 0;
      barSpacing = 0;
      break;
    case 'pie':
    case 'doughnut':
      height = CHART_DIMENSIONS.pieSize;
      barWidth = 0;
      barSpacing = 0;
      break;
    default:
      height = CHART_DIMENSIONS.barHeight;
      barWidth = 20;
      barSpacing = 8;
  }
  
  return {
    width,
    height,
    padding,
    barWidth,
    barSpacing,
  };
};

const calculateChartData = (data: ChartDataPoint[]): ChartCalculations => {
  if (data.length === 0) {
    return {
      maxValue: 0,
      minValue: 0,
      totalValue: 0,
      averageValue: 0,
      percentageValues: [],
    };
  }
  
  const values = data.map(point => point.value);
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const totalValue = values.reduce((sum, value) => sum + value, 0);
  const averageValue = totalValue / values.length;
  const percentageValues = values.map(value => (value / totalValue) * 100);
  
  return {
    maxValue,
    minValue,
    totalValue,
    averageValue,
    percentageValues,
  };
};

const getDataPointColor = (dataPoint: ChartDataPoint, index: number): string => {
  if (dataPoint.color) return dataPoint.color;
  
  const colors = Object.values(CHART_COLORS);
  return colors[index % colors.length];
};

const formatValue = (value: number): string => {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return value.toString();
};

const formatPercentage = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

const ChartTitle: React.FC<{
  title?: string;
  subtitle?: string;
}> = ({ title, subtitle }) => {
  if (!title && !subtitle) return null;
  
  return (
    <View style={styles.titleContainer}>
      {title && <Text style={styles.titleText}>{title}</Text>}
      {subtitle && <Text style={styles.subtitleText}>{subtitle}</Text>}
    </View>
  );
};

const BarChart: React.FC<{
  data: ChartDataPoint[];
  dimensions: ChartDimensions;
  calculations: ChartCalculations;
  onDataPointPress?: (dataPoint: ChartDataPoint) => void;
}> = ({ data, dimensions, calculations, onDataPointPress }) => {
  const renderBar = useCallback((dataPoint: ChartDataPoint, index: number) => {
    const height = (dataPoint.value / calculations.maxValue) * dimensions.height;
    const color = getDataPointColor(dataPoint, index);
    
    return (
      <View key={index} style={styles.barContainer}>
        <View
          style={[
            styles.bar,
            {
              height,
              backgroundColor: color,
              width: dimensions.barWidth,
            },
          ]}
        />
        <Text style={styles.barLabel} numberOfLines={1}>
          {dataPoint.label}
        </Text>
        <Text style={styles.barValue}>
          {formatValue(dataPoint.value)}
        </Text>
      </View>
    );
  }, [dimensions, calculations]);
  
  return (
    <View style={[styles.chartContainer, { height: dimensions.height }]}>
      {data.map((dataPoint, index) => renderBar(dataPoint, index))}
    </View>
  );
};

const LineChart: React.FC<{
  data: ChartDataPoint[];
  dimensions: ChartDimensions;
  calculations: ChartCalculations;
  onDataPointPress?: (dataPoint: ChartDataPoint) => void;
}> = ({ data, dimensions, calculations, onDataPointPress }) => {
  const renderDataPoint = useCallback((dataPoint: ChartDataPoint, index: number) => {
    const x = (index / (data.length - 1)) * dimensions.width;
    const y = dimensions.height - ((dataPoint.value / calculations.maxValue) * dimensions.height);
    const color = getDataPointColor(dataPoint, index);
    
    return (
      <View
        key={index}
        style={[
          styles.linePoint,
          {
            left: x,
            top: y,
            backgroundColor: color,
          },
        ]}
      />
    );
  }, [data, dimensions, calculations]);
  
  return (
    <View style={[styles.chartContainer, { height: dimensions.height }]}>
      {data.map((dataPoint, index) => renderDataPoint(dataPoint, index))}
    </View>
  );
};

const PieChart: React.FC<{
  data: ChartDataPoint[];
  dimensions: ChartDimensions;
  calculations: ChartCalculations;
  isDoughnut?: boolean;
  onDataPointPress?: (dataPoint: ChartDataPoint) => void;
}> = ({ data, dimensions, calculations, isDoughnut = false, onDataPointPress }) => {
  const renderSlice = useCallback((dataPoint: ChartDataPoint, index: number) => {
    const percentage = calculations.percentageValues[index];
    const color = getDataPointColor(dataPoint, index);
    
    return (
      <View key={index} style={styles.pieSliceContainer}>
        <View
          style={[
            styles.pieSlice,
            {
              backgroundColor: color,
              width: dimensions.width,
              height: dimensions.height,
            },
          ]}
        />
        <Text style={styles.pieLabel}>{dataPoint.label}</Text>
        <Text style={styles.pieValue}>{formatPercentage(percentage)}</Text>
      </View>
    );
  }, [dimensions, calculations]);
  
  return (
    <View style={styles.pieChartContainer}>
      <View
        style={[
          styles.pieChart,
          {
            width: dimensions.width,
            height: dimensions.height,
          },
        ]}
      >
        {data.map((dataPoint, index) => renderSlice(dataPoint, index))}
      </View>
    </View>
  );
};

const ChartLegend: React.FC<{
  data: ChartDataPoint[];
}> = ({ data }) => {
  const renderLegendItem = useCallback((dataPoint: ChartDataPoint, index: number) => {
    const color = getDataPointColor(dataPoint, index);
    
    return (
      <View key={index} style={styles.legendItem}>
        <View style={[styles.legendColor, { backgroundColor: color }]} />
        <Text style={styles.legendLabel}>{dataPoint.label}</Text>
        <Text style={styles.legendValue}>{formatValue(dataPoint.value)}</Text>
      </View>
    );
  }, []);
  
  return (
    <View style={styles.legendContainer}>
      {data.map((dataPoint, index) => renderLegendItem(dataPoint, index))}
    </View>
  );
};

const ChartLoading: React.FC = () => (
  <View style={styles.loadingContainer}>
    <OptimizedIcon
      name={CHART_ICONS.loading}
      size="large"
      variant="info"
    />
    <Text style={styles.loadingText}>Loading chart data...</Text>
  </View>
);

const ChartError: React.FC<{
  message: string;
}> = ({ message }) => (
  <View style={styles.errorContainer}>
    <OptimizedIcon
      name={CHART_ICONS.error}
      size="large"
      variant="error"
    />
    <Text style={styles.errorText}>{message}</Text>
  </View>
);

const ChartEmpty: React.FC<{
  message: string;
}> = ({ message }) => (
  <View style={styles.emptyContainer}>
    <OptimizedIcon
      name={CHART_ICONS.empty}
      size="large"
      variant="info"
    />
    <Text style={styles.emptyText}>{message}</Text>
  </View>
);

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedChart: React.FC<ChartProps> = ({
  data,
  type,
  title,
  subtitle,
  isLoading = false,
  hasError = false,
  errorMessage = 'Failed to load chart data',
  emptyMessage = 'No chart data available',
  canAnimate = true,
  canInteract = true,
  maxHeight = 400,
  onDataPointPress,
}) => {
  // Get screen dimensions
  const screenWidth = Dimensions.get('window').width;
  const containerWidth = screenWidth - (CHART_DIMENSIONS.containerPadding * 2);
  
  // Calculate chart dimensions and data
  const dimensions = useMemo(() => 
    calculateChartDimensions(containerWidth, type),
    [containerWidth, type]
  );
  
  const calculations = useMemo(() => 
    calculateChartData(data),
    [data]
  );
  
  // Render conditions
  if (isLoading) {
    return <ChartLoading />;
  }
  
  if (hasError) {
    return <ChartError message={errorMessage} />;
  }
  
  if (data.length === 0) {
    return <ChartEmpty message={emptyMessage} />;
  }
  
  // Render chart based on type
  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <BarChart
            data={data}
            dimensions={dimensions}
            calculations={calculations}
            onDataPointPress={onDataPointPress}
          />
        );
      case 'line':
        return (
          <LineChart
            data={data}
            dimensions={dimensions}
            calculations={calculations}
            onDataPointPress={onDataPointPress}
          />
        );
      case 'pie':
        return (
          <PieChart
            data={data}
            dimensions={dimensions}
            calculations={calculations}
            isDoughnut={false}
            onDataPointPress={onDataPointPress}
          />
        );
      case 'doughnut':
        return (
          <PieChart
            data={data}
            dimensions={dimensions}
            calculations={calculations}
            isDoughnut={true}
            onDataPointPress={onDataPointPress}
          />
        );
      default:
        return null;
    }
  };
  
  return (
    <View style={[styles.container, { maxHeight }]}>
      <ChartTitle title={title} subtitle={subtitle} />
      
      <View style={styles.chartWrapper}>
        {renderChart()}
      </View>
      
      <ChartLegend data={data} />
    </View>
  );
};

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: CHART_DIMENSIONS.containerPadding,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  titleContainer: {
    marginBottom: 16,
  },
  titleText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000000',
    marginBottom: 4,
  },
  subtitleText: {
    fontSize: 14,
    color: '#8E8E93',
  },
  chartWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 16,
  },
  chartContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    paddingHorizontal: CHART_DIMENSIONS.chartPadding,
  },
  barContainer: {
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  bar: {
    borderRadius: 4,
    marginBottom: 8,
  },
  barLabel: {
    fontSize: 12,
    color: '#8E8E93',
    textAlign: 'center',
    marginBottom: 4,
  },
  barValue: {
    fontSize: 12,
    fontWeight: '500',
    color: '#000000',
  },
  linePoint: {
    position: 'absolute',
    width: 8,
    height: 8,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  pieChartContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  pieChart: {
    borderRadius: 100,
    overflow: 'hidden',
  },
  pieSliceContainer: {
    alignItems: 'center',
    marginBottom: 8,
  },
  pieSlice: {
    borderRadius: 100,
  },
  pieLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#000000',
    marginBottom: 2,
  },
  pieValue: {
    fontSize: 10,
    color: '#8E8E93',
  },
  legendContainer: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  legendLabel: {
    fontSize: 14,
    color: '#000000',
    flex: 1,
  },
  legendValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#000000',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    marginTop: 12,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    marginTop: 12,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    marginTop: 12,
  },
}); 