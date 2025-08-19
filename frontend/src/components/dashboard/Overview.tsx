import React from 'react';
import { 
  TrendingUpIcon, 
  TrendingDownIcon, 
  CurrencyDollarIcon,
  ChartBarIcon,
  CogIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import { PortfolioSummary } from './PortfolioSummary';
import { RecentActivity } from './RecentActivity';
import { StrategyStatus } from './StrategyStatus';

export const Overview: React.FC = () => {
  // Mock data - in real app, this would come from API
  const portfolioStats = {
    totalValue: 125000,
    dailyChange: 2500,
    dailyChangePercent: 2.04,
    isPositive: true
  };

  const quickActions = [
    {
      name: 'Start Trading',
      description: 'Place new orders',
      icon: ChartBarIcon,
      href: '/dashboard/trading',
      color: 'bg-blue-500'
    },
    {
      name: 'Manage Strategies',
      description: 'Configure automated trading',
      icon: CogIcon,
      href: '/dashboard/strategies',
      color: 'bg-green-500'
    },
    {
      name: 'Risk Settings',
      description: 'Update risk parameters',
      icon: ShieldCheckIcon,
      href: '/dashboard/risk',
      color: 'bg-yellow-500'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Overview</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's what's happening with your portfolio today.
        </p>
      </div>

      {/* Portfolio summary cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Portfolio Value */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Portfolio Value
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${portfolioStats.totalValue.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <div className="flex items-center">
                {portfolioStats.isPositive ? (
                  <TrendingUpIcon className="h-4 w-4 text-green-400" />
                ) : (
                  <TrendingDownIcon className="h-4 w-4 text-red-400" />
                )}
                <span className={`ml-2 font-medium ${
                  portfolioStats.isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {portfolioStats.isPositive ? '+' : ''}${portfolioStats.dailyChange.toLocaleString()}
                </span>
                <span className={`ml-2 ${
                  portfolioStats.isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  ({portfolioStats.isPositive ? '+' : ''}{portfolioStats.dailyChangePercent}%)
                </span>
              </div>
              <span className="text-gray-500">vs yesterday</span>
            </div>
          </div>
        </div>

        {/* Active Strategies */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CogIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Strategies
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">3</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="text-gray-500">2 running, 1 paused</span>
            </div>
          </div>
        </div>

        {/* Open Orders */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Open Orders
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">7</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="text-gray-500">$12,450 pending</span>
            </div>
          </div>
        </div>

        {/* Risk Level */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ShieldCheckIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Risk Level
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">Medium</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <span className="text-gray-500">Within limits</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Portfolio Summary */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Portfolio Summary
            </h3>
            <PortfolioSummary />
          </div>
        </div>

        {/* Strategy Status */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Strategy Status
            </h3>
            <StrategyStatus />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {quickActions.map((action) => (
              <a
                key={action.name}
                href={action.href}
                className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <div>
                  <span className={`inline-flex p-3 rounded-lg ${action.color} text-white`}>
                    <action.icon className="h-6 w-6" />
                  </span>
                </div>
                <div className="mt-4">
                  <h3 className="text-lg font-medium">
                    <span className="absolute inset-0" aria-hidden="true" />
                    {action.name}
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    {action.description}
                  </p>
                </div>
                <span
                  className="absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                  aria-hidden="true"
                >
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 1a1 1 0 000 2V1zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
                  </svg>
                </span>
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Activity
          </h3>
          <RecentActivity />
        </div>
      </div>
    </div>
  );
};
