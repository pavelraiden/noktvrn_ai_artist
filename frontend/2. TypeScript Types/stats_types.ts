export interface RevenueSubscriptionsData {
  name: string;
  revenue: number;
  subscriptions: number;
}

export interface PieChartData {
  name: string;
  value: number;
}

export interface Stats {
  totalRevenue: number;
  artistCount: number;
  activeRuns: number;
  revenueSubscriptionsData: RevenueSubscriptionsData[];
  genreDistribution: PieChartData[];
  conversionRates: PieChartData[];
}