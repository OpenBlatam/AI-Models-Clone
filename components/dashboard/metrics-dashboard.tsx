'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  DollarSign, 
  ShoppingCart, 
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  MoreHorizontal
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MetricCard {
  title: string;
  value: string | number;
  description?: string;
  change?: {
    value: number;
    period: string;
    isPositive: boolean;
  };
  icon: React.ComponentType<{ className?: string }>;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
}

export interface ChartData {
  label: string;
  value: number;
  color?: string;
}

export interface MetricsDashboardProps {
  metrics: MetricCard[];
  recentActivity?: Array<{
    id: string;
    title: string;
    description: string;
    time: string;
    type: 'info' | 'success' | 'warning' | 'error';
  }>;
  className?: string;
}

const colorVariants = {
  primary: 'text-blue-600 bg-blue-100 dark:bg-blue-900/20',
  secondary: 'text-gray-600 bg-gray-100 dark:bg-gray-900/20',
  success: 'text-green-600 bg-green-100 dark:bg-green-900/20',
  warning: 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20',
  danger: 'text-red-600 bg-red-100 dark:bg-red-900/20',
};

const iconVariants = {
  primary: 'text-blue-600',
  secondary: 'text-gray-600',
  success: 'text-green-600',
  warning: 'text-yellow-600',
  danger: 'text-red-600',
};

export function MetricsDashboard({ metrics, recentActivity, className }: MetricsDashboardProps) {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <MetricCard key={index} metric={metric} />
        ))}
      </div>

      {/* Charts and Additional Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Placeholder */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Performance Overview</CardTitle>
              <CardDescription>
                Key metrics and trends over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted/20 rounded-lg">
                <div className="text-center text-muted-foreground">
                  <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Chart visualization would go here</p>
                  <p className="text-sm">Using libraries like Recharts or Chart.js</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest updates and notifications
              </CardDescription>
            </CardHeader>
            <CardContent>
              {recentActivity && recentActivity.length > 0 ? (
                <div className="space-y-4">
                  {recentActivity.slice(0, 5).map((activity) => (
                    <ActivityItem key={activity.id} activity={activity} />
                  ))}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No recent activity</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <QuickActionButton
              icon={Users}
              label="Add User"
              description="Create new user account"
              onClick={() => console.log('Add User clicked')}
            />
            <QuickActionButton
              icon={ShoppingCart}
              label="New Order"
              description="Process customer order"
              onClick={() => console.log('New Order clicked')}
            />
            <QuickActionButton
              icon={DollarSign}
              label="Generate Report"
              description="Create financial report"
              onClick={() => console.log('Generate Report clicked')}
            />
            <QuickActionButton
              icon={Activity}
              label="View Analytics"
              description="Check performance metrics"
              onClick={() => console.log('View Analytics clicked')}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({ metric }: { metric: MetricCard }) {
  return (
    <Card className="group hover:shadow-lg transition-all duration-200">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {metric.title}
        </CardTitle>
        <div className={cn(
          'p-2 rounded-lg',
          colorVariants[metric.color]
        )}>
          <metric.icon className={cn('h-4 w-4', iconVariants[metric.color])} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{metric.value}</div>
        {metric.description && (
          <p className="text-xs text-muted-foreground mt-1">
            {metric.description}
          </p>
        )}
        {metric.change && (
          <div className="flex items-center mt-2">
            {metric.change.isPositive ? (
              <ArrowUpRight className="h-3 w-3 text-green-600 mr-1" />
            ) : (
              <ArrowDownRight className="h-3 w-3 text-red-600 mr-1" />
            )}
            <span
              className={cn(
                'text-xs font-medium',
                metric.change.isPositive ? 'text-green-600' : 'text-red-600'
              )}
            >
              {metric.change.isPositive ? '+' : ''}{metric.change.value}%
            </span>
            <span className="text-xs text-muted-foreground ml-1">
              {metric.change.period}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ActivityItem({ activity }: { activity: MetricsDashboardProps['recentActivity'][0] }) {
  const typeColors = {
    info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    success: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    error: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
  };

  return (
    <div className="flex items-start space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
      <Badge className={cn('text-xs', typeColors[activity.type])}>
        {activity.type}
      </Badge>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground">
          {activity.title}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          {activity.description}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          {activity.time}
        </p>
      </div>
    </div>
  );
}

function QuickActionButton({ 
  icon: Icon, 
  label, 
  description, 
  onClick 
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  description: string;
  onClick: () => void;
}) {
  return (
    <Button
      variant="outline"
      className="h-auto p-4 flex flex-col items-center space-y-2 hover:shadow-md transition-all duration-200"
      onClick={onClick}
    >
      <Icon className="h-6 w-6 text-primary" />
      <div className="text-center">
        <div className="font-medium text-sm">{label}</div>
        <div className="text-xs text-muted-foreground">{description}</div>
      </div>
    </Button>
  );
}





