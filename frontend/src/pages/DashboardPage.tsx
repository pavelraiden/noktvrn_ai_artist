import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchQuickStats, fetchSystemStatus } from '@/api/dashboard'; // Use path alias
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton'; // Import Skeleton
// import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'; // Example chart import

// Placeholder components for loading states
const QuickStatsSkeleton: React.FC = () => (
  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    {[...Array(4)].map((_, index) => (
      <Card key={index}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <Skeleton className="h-4 w-1/2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-6 w-1/4 mb-2" />
          <Skeleton className="h-3 w-3/4" />
        </CardContent>
      </Card>
    ))}
  </div>
);

const SystemStatusSkeleton: React.FC = () => (
  <Card className="lg:col-span-2">
    <CardHeader>
      <Skeleton className="h-6 w-1/2" />
    </CardHeader>
    <CardContent className="space-y-3">
      {[...Array(5)].map((_, index) => (
        <div key={index} className="flex items-center justify-between">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-5 w-16" />
        </div>
      ))}
    </CardContent>
  </Card>
);

const DashboardPage: React.FC = () => {
  // Fetch Quick Stats
  const { data: quickStats, isLoading: isLoadingStats, error: errorStats } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: fetchQuickStats,
  });

  // Fetch System Status
  const { data: systemStatus, isLoading: isLoadingStatus, error: errorStatus } = useQuery({
    queryKey: ['dashboardStatus'],
    queryFn: fetchSystemStatus,
  });

  // TODO: Add queries for Recent Activity and Performance Data

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard Overview</h1>

      {/* Quick Stats Section */}
      {isLoadingStats ? (
        <QuickStatsSkeleton />
      ) : errorStats ? (
        <div className="text-red-500">Error loading stats: {errorStats.message}</div>
      ) : quickStats ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Artists</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{quickStats.artists}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Artists</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{quickStats.active}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Autopilot Enabled</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{quickStats.autopilot}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Errors Today</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{quickStats.errors}</div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* System Status & Performance Chart Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {isLoadingStatus ? (
          <SystemStatusSkeleton />
        ) : errorStatus ? (
          <Card className="lg:col-span-2 border-red-500">
            <CardHeader><CardTitle>System Status</CardTitle></CardHeader>
            <CardContent className="text-red-500">Error loading status: {errorStatus.message}</CardContent>
          </Card>
        ) : systemStatus ? (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(systemStatus).map(([service, status]) => (
                <div key={service} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{service}</span>
                  <Badge variant={status === 'Online' ? 'default' : status === 'Degraded' ? 'secondary' : 'destructive'}>
                    {status}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        ) : null}

        {/* Performance Chart Placeholder */}
        <Card className="lg:col-span-5">
          <CardHeader>
            <CardTitle>Performance Overview (Placeholder)</CardTitle>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-[300px] flex items-center justify-center text-muted-foreground">
              Chart will be implemented here using Recharts.
            </div>
            {/* Chart implementation using Recharts would go here, potentially using another query */}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity Section (Placeholder) */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity (Placeholder)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">
            Table with recent logs/events will be implemented here.
          </div>
          {/* Table component using data from another query would go here */}
        </CardContent>
      </Card>

    </div>
  );
};

export default DashboardPage;

