import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchStats } from '../services/api';
import { BarLineChart, PieChart } from '../components/charts';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { formatCurrency } from '../utils/formatters';

/**
 * Dashboard page component
 * @returns Dashboard page with stats and charts
 */
const Dashboard: React.FC = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
  });

  if (isLoading) {
    return <div className="flex justify-center items-center h-full">Loading...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        Error loading data. Please try again later.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {formatCurrency(stats?.totalRevenue || 0)}
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Cumulative revenue across all artists
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Artist Count</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {stats?.artistCount || 0}
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Total number of artists on the platform
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Runs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">
              {stats?.activeRuns || 0}
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Currently running generation processes
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Revenue & Subscriptions</CardTitle>
          </CardHeader>
          <CardContent>
            <BarLineChart 
              data={stats?.revenueSubscriptionsData || []} 
              height={300} 
            />
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Genre Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <PieChart 
                data={stats?.genreDistribution || []} 
                height={220}
                colors={['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Conversion Rates</CardTitle>
            </CardHeader>
            <CardContent>
              <PieChart 
                data={stats?.conversionRates || []} 
                height={220}
                colors={['#10b981', '#ef4444']}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;