import React from 'react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { PieChartData } from '../../types'; // Adjusted path

interface PieChartProps {
  data: PieChartData[];
  height?: number;
  title?: string;
  colors?: string[];
}

/**
 * Pie chart component for displaying distribution data
 * @param props Chart properties
 * @returns PieChart component
 */
const PieChart: React.FC<PieChartProps> = ({ 
  data, 
  height = 300,
  title,
  colors = ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'] // Example colors
}) => {
  return (
    <div>
      {title && <h3 className="text-base font-medium text-gray-900 mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={colors[index % colors.length]} 
              />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value, name) => [`${value}`, name]}
          />
          <Legend layout="horizontal" verticalAlign="bottom" align="center" />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PieChart;

