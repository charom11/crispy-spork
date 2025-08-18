import React, { useState, useEffect } from 'react';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { RiskProfileForm } from './RiskProfileForm';
import { RiskMetrics } from './RiskMetrics';
import { RiskAlerts } from './RiskAlerts';

export const RiskManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [riskProfile, setRiskProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data - in real app, this would come from API
  const mockRiskProfile = {
    name: "Conservative Profile",
    max_position_size: 10000,
    max_positions: 5,
    daily_loss_limit: 1000,
    weekly_loss_limit: 5000,
    monthly_loss_limit: 20000,
    default_stop_loss_percent: 5,
    default_take_profit_percent: 10,
    trailing_stop_enabled: true,
    trading_hours_start: "09:00",
    trading_hours_end: "17:00",
    weekend_trading: false
  };

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setRiskProfile(mockRiskProfile);
      setIsLoading(false);
    }, 1000);
  }, []);

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ShieldCheckIcon },
    { id: 'profile', name: 'Risk Profile', icon: ChartBarIcon },
    { id: 'alerts', name: 'Alerts', icon: ExclamationTriangleIcon },
    { id: 'metrics', name: 'Metrics', icon: CurrencyDollarIcon }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Risk Management</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor and control your trading risk with comprehensive safety measures.
        </p>
      </div>

      {/* Risk Level Indicator */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Current Risk Level</h3>
              <p className="text-sm text-gray-500">Based on your portfolio and limits</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-green-600">Low Risk</div>
            <div className="text-sm text-gray-500">All limits within bounds</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'overview' && <RiskOverview riskProfile={riskProfile} />}
          {activeTab === 'profile' && <RiskProfileForm riskProfile={riskProfile} />}
          {activeTab === 'alerts' && <RiskAlerts />}
          {activeTab === 'metrics' && <RiskMetrics />}
        </div>
      </div>
    </div>
  );
};

const RiskOverview: React.FC<{ riskProfile: any }> = ({ riskProfile }) => {
  if (!riskProfile) {
    return (
      <div className="text-center py-8">
        <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No Risk Profile</h3>
        <p className="mt-1 text-sm text-gray-500">Create a risk profile to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Profile Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <CurrencyDollarIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-900">Position Limits</span>
            </div>
            <div className="mt-2">
              <p className="text-2xl font-bold text-gray-900">${riskProfile.max_position_size.toLocaleString()}</p>
              <p className="text-sm text-gray-500">Max position size</p>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-900">Daily Loss Limit</span>
            </div>
            <div className="mt-2">
              <p className="text-2xl font-bold text-gray-900">${riskProfile.daily_loss_limit.toLocaleString()}</p>
              <p className="text-sm text-gray-500">Maximum daily loss</p>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <ClockIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-900">Trading Hours</span>
            </div>
            <div className="mt-2">
              <p className="text-2xl font-bold text-gray-900">{riskProfile.trading_hours_start} - {riskProfile.trading_hours_end}</p>
              <p className="text-sm text-gray-500">Weekend trading: {riskProfile.weekend_trading ? 'Yes' : 'No'}</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Stop Loss & Take Profit</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-red-800">Stop Loss</span>
              <span className="text-2xl font-bold text-red-600">{riskProfile.default_stop_loss_percent}%</span>
            </div>
            <p className="text-sm text-red-600 mt-1">Automatic stop loss percentage</p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-green-800">Take Profit</span>
              <span className="text-2xl font-bold text-green-600">{riskProfile.default_take_profit_percent}%</span>
            </div>
            <p className="text-sm text-green-600 mt-1">Automatic take profit percentage</p>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex space-x-3">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
            Update Profile
          </button>
          <button className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors">
            View Alerts
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
            Test Risk Check
          </button>
        </div>
      </div>
    </div>
  );
};