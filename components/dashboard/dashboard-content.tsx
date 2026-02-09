'use client';

import { useState } from 'react';
import { useDashboardData } from './hooks/useDashboardData';
import { useUserColumns, useOrderColumns } from './hooks/useTableColumns';
import { DashboardTabs } from './components/DashboardTabs';

export function DashboardContent() {
  const {
    users,
    orders,
    metrics,
    recentActivity,
    totalUsers,
    totalOrders,
    totalRevenue
  } = useDashboardData();

  const userColumns = useUserColumns();
  const orderColumns = useOrderColumns();

  const handleUserRowClick = (user: typeof users[0]) => {
    // In a real app, you might navigate to a user detail page
    console.log('User clicked:', user);
  };

  const handleOrderRowClick = (order: typeof orders[0]) => {
    // In a real app, you might navigate to an order detail page
    console.log('Order clicked:', order);
  };

  return (
    <div className="space-y-8">
      <DashboardTabs
        metrics={metrics}
        recentActivity={recentActivity}
        totalUsers={totalUsers}
        totalOrders={totalOrders}
        totalRevenue={totalRevenue}
        users={users}
        orders={orders}
        userColumns={userColumns}
        orderColumns={orderColumns}
        onUserRowClick={handleUserRowClick}
        onOrderRowClick={handleOrderRowClick}
      />
    </div>
  );
}    