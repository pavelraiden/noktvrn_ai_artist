import React from 'react';
import {
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts';
import { RevenueSubscriptionsData } from '../../types'; // Adjusted path
import { formatCurrency } from '../../utils/formatters'; // Adjusted path

interface BarLineChartProps {
  data: RevenueSubscriptionsData[];
  height?: number;
  title?: string;
}

/**
 * Combined bar and line chart component for revenue and subscriptions data
 * @param props Chart properties
 * @returns BarLineChart component
 */
const BarLineChart: React.FC<BarLineChartProps> = ({ 
  data, 
  height = 300,
  title 
}) => {
  return (
    <div>
      {title && <h3 className="text-base font-medium text-gray-900 mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis 
            yAxisId="left" 
            tick={{ fontSize: 12 }} 
            tickFormatter={(value) => formatCurrency(value as number)} // Use formatCurrency
            domain={[0, 'auto']}
          />
          <YAxis 
            yAxisId="right" 
            orientation="right" 
            tick={{ fontSize: 12 }}
            domain={[0, 'auto']}
          />
          <Tooltip 
            formatter={(value, name) => {
              if (name === 'revenue') return [formatCurrency(value as number), 'Revenue'];
              return [value, 'Subscriptions'];
            }}
            labelFormatter={(label) => `Period: ${label}`}
          />
          <Legend 
            formatter={(value) => {
              if (value === 'revenue') return 'Revenue';
              return 'Subscriptions';
            }}
          />
          <Bar 
            yAxisId="left" 
            dataKey="revenue" 
            fill="#0ea5e9" // Example color
            radius={[4, 4, 0, 0]} 
          />
          <Line 
            yAxisId="right" 
            type="monotone" 
            dataKey="subscriptions" 
            stroke="#8b5cf6" // Example color
            strokeWidth={2} 
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BarLineChart;

