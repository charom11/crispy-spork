import React from 'react';
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export const StrategyStatus: React.FC = () => {
  // Mock data - in real app, this would come from API
  const strategies = [
    {
      id: '1',
      name: 'Grid Trading BTC',
      type: 'Grid',
      status: 'running',
      performance: '+$1,250',
      performancePercent: '+2.8%',
      isPositive: true,
      lastTrade: '2 min ago'
    },
    {
      id: '2',
      name: 'Mean Reversion ETH',
      type: 'Mean Reversion',
      status: 'running',
      performance: '+$850',
      performancePercent: '+1.5%',
      isPositive: true,
      lastTrade: '5 min ago'
    },
    {
      id: '3',
      name: 'Momentum Strategy',
      type: 'Momentum',
      status: 'paused',
      performance: '-$320',
      performancePercent: '-0.8%',
      isPositive: false,
      lastTrade: '1 hour ago'
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <PlayIcon className="h-4 w-4 text-green-500" />;
      case 'paused':
        return <PauseIcon className="h-4 w-4 text-yellow-500" />;
      case 'stopped':
        return <StopIcon className="h-4 w-4 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'stopped':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return 'Running';
      case 'paused':
        return 'Paused';
      case 'stopped':
        return 'Stopped';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">Active Strategies</span>
        <span className="text-sm font-medium text-gray-900">
          {strategies.filter(s => s.status === 'running').length} of {strategies.length}
        </span>
      </div>

      {/* Strategy List */}
      <div className="space-y-3">
        {strategies.map((strategy) => (
          <div key={strategy.id} className="border border-gray-200 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {getStatusIcon(strategy.status)}
                <span className="text-sm font-medium text-gray-900">
                  {strategy.name}
                </span>
              </div>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(strategy.status)}`}>
                {getStatusText(strategy.status)}
              </span>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <div>
                <span className="text-gray-500">Type: </span>
                <span className="text-gray-900">{strategy.type}</span>
              </div>
              <div>
                <span className="text-gray-500">Last trade: </span>
                <span className="text-gray-900">{strategy.lastTrade}</span>
              </div>
            </div>
            
            <div className="mt-2 flex items-center justify-between">
              <div>
                <span className="text-gray-500">Performance: </span>
                <span className={`font-medium ${
                  strategy.isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {strategy.performance}
                </span>
                <span className={`ml-1 text-xs ${
                  strategy.isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  ({strategy.performancePercent})
                </span>
              </div>
              
              <div className="flex space-x-1">
                <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                  <PlayIcon className="h-4 w-4" />
                </button>
                <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                  <PauseIcon className="h-4 w-4" />
                </button>
                <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                  <StopIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="pt-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <button className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
            Start All
          </button>
          <button className="flex-1 bg-gray-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors">
            Pause All
          </button>
        </div>
      </div>
    </div>
  );
};