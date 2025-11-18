'use client';

import { useState, useMemo } from 'react';
import { MetricsDashboard, MetricCard } from '@/components/dashboard/metrics-dashboard';
import { PerformanceDashboard } from '@/components/dashboard/performance-dashboard';
import { AIOptimizationDashboard } from '@/components/dashboard/ai-optimization-dashboard';
import { CollaborationDashboard } from '@/components/collaboration/collaboration-dashboard';
import { SecurityDashboard } from '@/components/security/security-dashboard';
import { ApiDocumentationDashboard } from '@/components/api-docs/api-documentation-dashboard';
import { CacheDashboard } from '@/components/cache/cache-dashboard';
import { DataTable, Column } from '@/components/ui/data-table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Users, DollarSign, ShoppingCart, TrendingUp, Activity, BarChart3, Settings, Brain, Users2, Shield, BookOpen, Database } from 'lucide-react';

// Sample data types
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'inactive' | 'pending';
  lastLogin: string;
  createdAt: string;
}

interface Order {
  id: string;
  customer: string;
  amount: number;
  status: 'pending' | 'processing' | 'completed' | 'cancelled';
  date: string;
  items: number;
}

// Sample data
const sampleUsers: User[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Admin',
    status: 'active',
    lastLogin: '2024-01-15',
    createdAt: '2023-06-01',
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane@example.com',
    role: 'User',
    status: 'active',
    lastLogin: '2024-01-14',
    createdAt: '2023-08-15',
  },
  {
    id: '3',
    name: 'Bob Johnson',
    email: 'bob@example.com',
    role: 'Moderator',
    status: 'pending',
    lastLogin: '2024-01-10',
    createdAt: '2023-12-01',
  },
  {
    id: '4',
    name: 'Alice Brown',
    email: 'alice@example.com',
    role: 'User',
    status: 'inactive',
    lastLogin: '2023-12-20',
    createdAt: '2023-09-01',
  },
  {
    id: '5',
    name: 'Charlie Wilson',
    email: 'charlie@example.com',
    role: 'User',
    status: 'active',
    lastLogin: '2024-01-16',
    createdAt: '2023-11-01',
  },
];

const sampleOrders: Order[] = [
  {
    id: 'ORD-001',
    customer: 'John Doe',
    amount: 299.99,
    status: 'completed',
    date: '2024-01-15',
    items: 3,
  },
  {
    id: 'ORD-002',
    customer: 'Jane Smith',
    amount: 149.50,
    status: 'processing',
    date: '2024-01-16',
    items: 2,
  },
  {
    id: 'ORD-003',
    customer: 'Bob Johnson',
    amount: 89.99,
    status: 'pending',
    date: '2024-01-16',
    items: 1,
  },
  {
    id: 'ORD-004',
    customer: 'Alice Brown',
    amount: 199.99,
    status: 'cancelled',
    date: '2024-01-14',
    items: 2,
  },
  {
    id: 'ORD-005',
    customer: 'Charlie Wilson',
    amount: 399.99,
    status: 'completed',
    date: '2024-01-13',
    items: 4,
  },
];

// Recent activity data
const recentActivity = [
  {
    id: '1',
    title: 'New user registered',
    description: 'Alice Brown joined the platform',
    time: '2 hours ago',
    type: 'info' as const,
  },
  {
    id: '2',
    title: 'Order completed',
    description: 'ORD-001 has been successfully delivered',
    time: '4 hours ago',
    type: 'success' as const,
  },
  {
    id: '3',
    title: 'Payment failed',
    description: 'ORD-003 payment processing failed',
    time: '6 hours ago',
    type: 'error' as const,
  },
  {
    id: '4',
    title: 'System update',
    description: 'Platform updated to version 2.1.0',
    time: '1 day ago',
    type: 'info' as const,
  },
  {
    id: '5',
    title: 'High traffic alert',
    description: 'Unusual traffic spike detected',
    time: '1 day ago',
    type: 'warning' as const,
  },
];

export function DashboardContent() {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Metrics data
  const metrics: MetricCard[] = useMemo(() => [
    {
      title: 'Total Users',
      value: sampleUsers.length,
      description: 'Registered users',
      change: { value: 12, period: 'this month', isPositive: true },
      icon: Users,
      color: 'primary',
    },
    {
      title: 'Total Revenue',
      value: `$${sampleOrders
        .filter(order => order.status === 'completed')
        .reduce((sum, order) => sum + order.amount, 0)
        .toFixed(2)}`,
      description: 'From completed orders',
      change: { value: 8.2, period: 'this month', isPositive: true },
      icon: DollarSign,
      color: 'success',
    },
    {
      title: 'Active Orders',
      value: sampleOrders.filter(order => 
        ['pending', 'processing'].includes(order.status)
      ).length,
      description: 'Orders in progress',
      change: { value: 5.1, period: 'this week', isPositive: false },
      icon: ShoppingCart,
      color: 'warning',
    },
    {
      title: 'Conversion Rate',
      value: '68.5%',
      description: 'Order completion rate',
      change: { value: 2.3, period: 'this month', isPositive: true },
      icon: TrendingUp,
      color: 'info',
    },
  ], []);

  // Table columns for users
  const userColumns: Column<User>[] = useMemo(() => [
    {
      key: 'name',
      header: 'Name',
      sortable: true,
      filterable: true,
    },
    {
      key: 'email',
      header: 'Email',
      sortable: true,
      filterable: true,
    },
    {
      key: 'role',
      header: 'Role',
      sortable: true,
      filterable: true,
      render: (value) => (
        <Badge variant="secondary" size="sm">
          {value}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const variants = {
          active: 'success',
          inactive: 'secondary',
          pending: 'warning',
        } as const;
        return (
          <Badge variant={variants[value]} size="sm">
            {value}
          </Badge>
        );
      },
    },
    {
      key: 'lastLogin',
      header: 'Last Login',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'createdAt',
      header: 'Created',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString(),
    },
  ], []);

  // Table columns for orders
  const orderColumns: Column<Order>[] = useMemo(() => [
    {
      key: 'id',
      header: 'Order ID',
      sortable: true,
      filterable: true,
    },
    {
      key: 'customer',
      header: 'Customer',
      sortable: true,
      filterable: true,
    },
    {
      key: 'amount',
      header: 'Amount',
      sortable: true,
      render: (value) => `$${value.toFixed(2)}`,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const variants = {
          pending: 'warning',
          processing: 'info',
          completed: 'success',
          cancelled: 'destructive',
        } as const;
        return (
          <Badge variant={variants[value]} size="sm">
            {value}
          </Badge>
        );
      },
    },
    {
      key: 'date',
      header: 'Date',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'items',
      header: 'Items',
      sortable: true,
    },
  ], []);

  const handleUserRowClick = (user: User) => {
    setSelectedUser(user);
    // In a real app, you might navigate to a user detail page
    console.log('User clicked:', user);
  };

  const handleOrderRowClick = (order: Order) => {
    // In a real app, you might navigate to an order detail page
    console.log('Order clicked:', order);
  };

  return (
    <div className="space-y-8">
                  <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-8">
                <TabsTrigger value="overview" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="performance" className="flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Performance
                </TabsTrigger>
                <TabsTrigger value="ai-optimization" className="flex items-center gap-2">
                  <Brain className="h-4 w-4" />
                  AI Optimization
                </TabsTrigger>
                <TabsTrigger value="collaboration" className="flex items-center gap-2">
                  <Users2 className="h-4 w-4" />
                  Collaboration
                </TabsTrigger>
                <TabsTrigger value="security" className="flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  Security
                </TabsTrigger>
                <TabsTrigger value="api-docs" className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4" />
                  API Docs
                </TabsTrigger>
                <TabsTrigger value="cache" className="flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  Cache
                </TabsTrigger>
                <TabsTrigger value="management" className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  Management
                </TabsTrigger>
              </TabsList>

        <TabsContent value="overview" className="space-y-8">
          {/* Metrics Dashboard */}
          <MetricsDashboard 
            metrics={metrics} 
            recentActivity={recentActivity}
          />

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{sampleUsers.length}</div>
                <p className="text-xs text-muted-foreground">
                  +12 from last month
                </p>
              </CardContent>
            </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Orders</CardTitle>
                <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{sampleOrders.length}</div>
              <p className="text-xs text-muted-foreground">
                  +5 from last week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">
                  ${sampleOrders
                    .filter(order => order.status === 'completed')
                    .reduce((sum, order) => sum + order.amount, 0)
                    .toFixed(2)}
                </div>
              <p className="text-xs text-muted-foreground">
                  +8.2% from last month
              </p>
            </CardContent>
          </Card>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4">
            <Button>
              <Users className="mr-2 h-4 w-4" />
              Add New User
            </Button>
            <Button variant="outline">
              <ShoppingCart className="mr-2 h-4 w-4" />
              Create Order
            </Button>
            <Button variant="outline">
              <Activity className="mr-2 h-4 w-4" />
              View Reports
            </Button>
            <Button variant="outline">
              <TrendingUp className="mr-2 h-4 w-4" />
              Export Data
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-8">
          <PerformanceDashboard />
        </TabsContent>

        <TabsContent value="ai-optimization" className="space-y-8">
          <AIOptimizationDashboard />
        </TabsContent>

                      <TabsContent value="collaboration" className="space-y-8">
                <CollaborationDashboard />
              </TabsContent>

              <TabsContent value="security" className="space-y-8">
                <SecurityDashboard />
              </TabsContent>

              <TabsContent value="api-docs" className="space-y-8">
                <ApiDocumentationDashboard />
              </TabsContent>

              <TabsContent value="cache" className="space-y-8">
                <CacheDashboard />
              </TabsContent>

              <TabsContent value="management" className="space-y-8">
          {/* Users Table */}
          <Card>
            <CardHeader>
              <CardTitle>Users Management</CardTitle>
              <CardDescription>
                Manage user accounts and permissions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                data={sampleUsers}
                columns={userColumns}
                title="Users"
                searchable
                filterable
                downloadable
                pageSize={5}
                onRowClick={handleUserRowClick}
                emptyMessage="No users found"
              />
            </CardContent>
          </Card>

          {/* Orders Table */}
          <Card>
            <CardHeader>
              <CardTitle>Order Management</CardTitle>
              <CardDescription>
                Track and manage customer orders
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                data={sampleOrders}
                columns={orderColumns}
                title="Orders"
                searchable
                filterable
                downloadable
                pageSize={5}
                onRowClick={handleOrderRowClick}
                emptyMessage="No orders found"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
                    </div>
  );
}    