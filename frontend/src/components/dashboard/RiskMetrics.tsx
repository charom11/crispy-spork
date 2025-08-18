import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';
import { 
  TrendingUpIcon, 
  TrendingDownIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

export const RiskMetrics: React.FC = () => {
  // Mock data - in real app, this would come from API
  const riskMetrics = {
    current_portfolio_value: 125000,
    daily_pnl: 2500,
    daily_pnl_percent: 2.04,
    weekly_pnl: 8500,
    weekly_pnl_percent: 7.28,
    monthly_pnl: 18500,
    monthly_pnl_percent: 17.38,
    total_pnl: 25000,
    total_pnl_percent: 25.0,
    current_risk_level: "low",
    portfolio_risk_percent: 5.0,
    max_drawdown: 8.5,
    sharpe_ratio: 1.2,
    volatility: 25.0,
    open_positions: 3,
    total_position_value: 45000,
    largest_position: 20000,
    position_concentration: 16.0,
    daily_loss_limit_remaining: 1000,
    weekly_loss_limit_remaining: 5000,
    monthly_loss_limit_remaining: 20000,
    total_loss_limit_remaining: 50000,
    active_alerts_count: 0,
    critical_alerts_count: 0
  };

  const drawdownData = [
    { date: 'Jan', drawdown: 0 },
    { date: 'Feb', drawdown: -2.5 },
    { date: 'Mar', drawdown: -1.8 },
    { date: 'Apr', drawdown: -4.2 },
    { date: 'May', drawdown: -3.1 },
    { date: 'Jun', drawdown: -2.0 },
    { date: 'Jul', drawdown: -1.5 },
    { date: 'Aug', drawdown: -0.8 },
    { date: 'Sep', drawdown: -2.3 },
    { date: 'Oct', drawdown: -1.9 },
    { date: 'Nov', drawdown: -1.2 },
    { date: 'Dec', drawdown: -0.5 }
  ];

  const volatilityData = [
    { month: 'Jan', volatility: 22.5 },
    { month: 'Feb', volatility: 28.3 },
    { month: 'Mar', volatility: 31.7 },
    { month: 'Apr', volatility: 25.9 },
    { month: 'May', volatility: 29.4 },
    { month: 'Jun', volatility: 26.8 },
    { month: 'Jul', volatility: 24.1 },
    { month: 'Aug', volatility: 27.6 },
    { month: 'Sep', volatility: 30.2 },
    { month: 'Oct', volatility: 28.9 },
    { month: 'Nov', volatility: 25.3 },
    { month: 'Dec', volatility: 23.7 }
  ];

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'critical':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskLevelIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'medium':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'high':
        return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
      case 'critical':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <CheckCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Risk Overview</h3>
        
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Risk Level</span>
              {getRiskLevelIcon(riskMetrics.current_risk_level)}
            </div>
            <div className="mt-2">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(riskMetrics.current_risk_level)}`}>
                {riskMetrics.current_risk_level.toUpperCase()}
              </span>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-sm text-gray-500">Portfolio Risk</div>
            <div className="mt-2 text-2xl font-bold text-gray-900">{riskMetrics.portfolio_risk_percent}%</div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-sm text-gray-500">Max Drawdown</div>
            <div className="mt-2 text-2xl font-bold text-red-600">{riskMetrics.max_drawdown}%</div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-sm text-gray-500">Sharpe Ratio</div>
            <div className="mt-2 text-2xl font-bold text-gray-900">{riskMetrics.sharpe_ratio}</div>
          </div>
        </div>

        {/* P&L Summary */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Profit & Loss Summary</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-500">Daily</div>
              <div className={`text-lg font-semibold ${riskMetrics.daily_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {riskMetrics.daily_pnl >= 0 ? '+' : ''}${riskMetrics.daily_pnl.toLocaleString()}
              </div>
              <div className={`text-sm ${riskMetrics.daily_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ({riskMetrics.daily_pnl_percent >= 0 ? '+' : ''}{riskMetrics.daily_pnl_percent}%)
              </div>
            </div>

            <div className="text-center">
              <div className="text-sm text-gray-500">Weekly</div>
              <div className={`text-lg font-semibold ${riskMetrics.weekly_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {riskMetrics.weekly_pnl >= 0 ? '+' : ''}${riskMetrics.weekly_pnl.toLocaleString()}
              </div>
              <div className={`text-sm ${riskMetrics.weekly_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ({riskMetrics.weekly_pnl_percent >= 0 ? '+' : ''}{riskMetrics.weekly_pnl_percent}%)
              </div>
            </div>

            <div className="text-center">
              <div className="text-sm text-gray-500">Monthly</div>
              <div className={`text-lg font-semibold ${riskMetrics.monthly_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {riskMetrics.monthly_pnl >= 0 ? '+' : ''}${riskMetrics.monthly_pnl.toLocaleString()}
              </div>
              <div className={`text-sm ${riskMetrics.monthly_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ({riskMetrics.monthly_pnl_percent >= 0 ? '+' : ''}{riskMetrics.monthly_pnl_percent}%)
              </div>
            </div>

            <div className="text-center">
              <div className="text-sm text-gray-500">Total</div>
              <div className={`text-lg font-semibold ${riskMetrics.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {riskMetrics.total_pnl >= 0 ? '+' : ''}${riskMetrics.total_pnl.toLocaleString()}
              </div>
              <div className={`text-sm ${riskMetrics.total_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ({riskMetrics.total_pnl_percent >= 0 ? '+' : ''}{riskMetrics.total_pnl_percent}%)
              </div>
            </div>
          </div>
        </div>

        {/* Position Information */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-3">Position Information</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-500">Open Positions</div>
              <div className="text-lg font-semibold text-gray-900">{riskMetrics.open_positions}</div>
            </div>

            <div className="text-center">
              <div className="text-sm text-gray-500">Total Position Value</div>
              <div className="text-lg font-semibold text-gray-900">${riskMetrics.total_position_value.toLocaleString()}</div>
            </div>

            <div className="text-center">
              <div className="text-sm text-gray-500">Largest Position</div>
              <div className="text-lg font-semibold text-gray-900">${riskMetrics.largest_position.toLocaleString()}</div>
            </div>

            <div className="text-center">
              <div className="text-sm text-gray-500">Concentration</div>
              <div className="text-lg font-semibold text-gray-900">{riskMetrics.position_concentration}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Drawdown Chart */}
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Maximum Drawdown</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={drawdownData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[-5, 1]} />
                <Tooltip 
                  formatter={(value: any) => [`${value}%`, 'Drawdown']}
                  labelFormatter={(label) => `Month: ${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="drawdown" 
                  stroke="#EF4444" 
                  strokeWidth={2}
                  dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Volatility Chart */}
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Volatility Trend</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={volatilityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[0, 35]} />
                <Tooltip 
                  formatter={(value: any) => [`${value}%`, 'Volatility']}
                  labelFormatter={(label) => `Month: ${label}`}
                />
                <Bar dataKey="volatility" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Loss Limits Status */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-4">Loss Limits Status</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-sm text-gray-500">Daily Limit Remaining</div>
            <div className="text-lg font-semibold text-green-600">${riskMetrics.daily_loss_limit_remaining.toLocaleString()}</div>
          </div>

          <div className="text-center">
            <div className="text-sm text-gray-500">Weekly Limit Remaining</div>
            <div className="text-lg font-semibold text-green-600">${riskMetrics.weekly_loss_limit_remaining.toLocaleString()}</div>
          </div>

          <div className="text-center">
            <div className="text-sm text-gray-500">Monthly Limit Remaining</div>
            <div className="text-lg font-semibold text-green-600">${riskMetrics.monthly_loss_limit_remaining.toLocaleString()}</div>
          </div>

          <div className="text-center">
            <div className="text-sm text-gray-500">Total Limit Remaining</div>
            <div className="text-lg font-semibold text-green-600">${riskMetrics.total_loss_limit_remaining.toLocaleString()}</div>
          </div>
        </div>
      </div>

      {/* Alerts Summary */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-4">Risk Alerts</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-sm text-gray-500">Active Alerts</div>
            <div className="text-lg font-semibold text-yellow-600">{riskMetrics.active_alerts_count}</div>
          </div>

          <div className="text-center">
            <div className="text-sm text-gray-500">Critical Alerts</div>
            <div className="text-lg font-semibold text-red-600">{riskMetrics.critical_alerts_count}</div>
          </div>
        </div>
      </div>
    </div>
  );
};