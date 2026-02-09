'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Users,
  DollarSign,
  ShoppingCart,
  Activity,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { MetricCard } from './components/MetricCard';
import { ActivityItem } from './components/ActivityItem';
import { QuickActionButton } from './components/QuickActionButton';

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






