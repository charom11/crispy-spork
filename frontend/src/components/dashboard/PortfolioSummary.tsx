import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export const PortfolioSummary: React.FC = () => {
  // Mock data - in real app, this would come from API
  const portfolioData = [
    { name: 'Bitcoin', value: 45000, percentage: 36 },
    { name: 'Ethereum', value: 30000, percentage: 24 },
    { name: 'USDT', value: 25000, percentage: 20 },
    { name: 'Other Crypto', value: 15000, percentage: 12 },
    { name: 'Cash', value: 10000, percentage: 8 }
  ];

  const totalValue = portfolioData.reduce((sum, item) => sum + item.value, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{data.name}</p>
          <p className="text-gray-600">${data.value.toLocaleString()}</p>
          <p className="text-gray-500">{data.percentage}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      {/* Total Value */}
      <div className="text-center">
        <p className="text-sm text-gray-500">Total Portfolio Value</p>
        <p className="text-2xl font-bold text-gray-900">${totalValue.toLocaleString()}</p>
      </div>

      {/* Chart */}
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={portfolioData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
            >
              {portfolioData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="space-y-2">
        {portfolioData.map((item, index) => (
          <div key={item.name} className="flex items-center justify-between">
            <div className="flex items-center">
              <div 
                className="w-3 h-3 rounded-full mr-2"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-sm text-gray-700">{item.name}</span>
            </div>
            <div className="text-right">
              <span className="text-sm font-medium text-gray-900">
                ${item.value.toLocaleString()}
              </span>
              <span className="text-sm text-gray-500 ml-2">
                ({item.percentage}%)
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Performance Summary */}
      <div className="pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-sm text-gray-500">24h Change</p>
            <p className="text-lg font-semibold text-green-600">+$2,500</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">7d Change</p>
            <p className="text-lg font-semibold text-red-600">-$1,200</p>
          </div>
        </div>
      </div>
    </div>
  );
};
