import React from 'react';
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  CogIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

export const RecentActivity: React.FC = () => {
  // Mock data - in real app, this would come from API
  const activities = [
    {
      id: '1',
      type: 'trade',
      action: 'buy',
      symbol: 'BTCUSDT',
      quantity: '0.5',
      price: '$52,450',
      time: '2 minutes ago',
      status: 'completed'
    },
    {
      id: '2',
      type: 'trade',
      action: 'sell',
      symbol: 'ETHUSDT',
      quantity: '2.0',
      price: '$3,120',
      time: '5 minutes ago',
      status: 'completed'
    },
    {
      id: '3',
      type: 'strategy',
      action: 'started',
      name: 'Grid Trading BTC',
      time: '10 minutes ago',
      status: 'success'
    },
    {
      id: '4',
      type: 'order',
      action: 'placed',
      symbol: 'BTCUSDT',
      quantity: '0.3',
      price: '$52,200',
      time: '15 minutes ago',
      status: 'pending'
    },
    {
      id: '5',
      type: 'system',
      action: 'risk_check',
      message: 'Daily loss limit reached',
      time: '1 hour ago',
      status: 'warning'
    }
  ];

  const getActivityIcon = (type: string, action: string) => {
    if (type === 'trade') {
      return action === 'buy' ? 
        <ArrowUpIcon className="h-5 w-5 text-green-500" /> : 
        <ArrowDownIcon className="h-5 w-5 text-red-500" />;
    }
    if (type === 'strategy') {
      return <CogIcon className="h-5 w-5 text-blue-500" />;
    }
    if (type === 'order') {
      return <CheckCircleIcon className="h-5 w-5 text-yellow-500" />;
    }
    if (type === 'system') {
      return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
    }
    return <CheckCircleIcon className="h-5 w-5 text-gray-500" />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'warning':
        return 'bg-orange-100 text-orange-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'success':
        return 'Success';
      case 'pending':
        return 'Pending';
      case 'warning':
        return 'Warning';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  const formatActivityMessage = (activity: any) => {
    if (activity.type === 'trade') {
      return `${activity.action === 'buy' ? 'Bought' : 'Sold'} ${activity.quantity} ${activity.symbol} at ${activity.price}`;
    }
    if (activity.type === 'strategy') {
      return `Strategy "${activity.name}" ${activity.action}`;
    }
    if (activity.type === 'order') {
      return `Order placed: ${activity.quantity} ${activity.symbol} at ${activity.price}`;
    }
    if (activity.type === 'system') {
      return activity.message;
    }
    return 'Unknown activity';
  };

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div key={activity.id} className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          {/* Icon */}
          <div className="flex-shrink-0 mt-0.5">
            {getActivityIcon(activity.type, activity.action)}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900">
              {formatActivityMessage(activity)}
            </p>
            <p className="text-sm text-gray-500">
              {activity.time}
            </p>
          </div>

          {/* Status */}
          <div className="flex-shrink-0">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
              {getStatusText(activity.status)}
            </span>
          </div>
        </div>
      ))}

      {/* View All Link */}
      <div className="text-center pt-2">
        <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
          View all activity →
        </button>
      </div>
    </div>
  );
};