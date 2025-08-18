import React, { useState } from 'react';
import { 
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

export const RiskAlerts: React.FC = () => {
  const [showAcknowledged, setShowAcknowledged] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');

  // Mock data - in real app, this would come from API
  const alerts = [
    {
      id: '1',
      alert_type: 'loss_limit',
      severity: 'critical',
      message: 'Daily loss limit exceeded by $500',
      details: {
        current_loss: -1500,
        limit: -1000,
        exceeded_by: 500
      },
      is_active: true,
      is_acknowledged: false,
      created_at: '2024-01-15T10:30:00Z',
      acknowledged_at: null
    },
    {
      id: '2',
      alert_type: 'position_limit',
      severity: 'high',
      message: 'Position size exceeds 80% of maximum allowed',
      details: {
        current_size: 8000,
        max_size: 10000,
        percentage: 80
      },
      is_active: true,
      is_acknowledged: false,
      created_at: '2024-01-15T09:15:00Z',
      acknowledged_at: null
    },
    {
      id: '3',
      alert_type: 'volatility',
      severity: 'medium',
      message: 'High volatility detected in BTCUSDT',
      details: {
        symbol: 'BTCUSDT',
        volatility: 65.2,
        threshold: 50.0
      },
      is_active: true,
      is_acknowledged: true,
      created_at: '2024-01-15T08:45:00Z',
      acknowledged_at: '2024-01-15T09:00:00Z'
    },
    {
      id: '4',
      alert_type: 'trading_hours',
      severity: 'low',
      message: 'Trading outside allowed hours',
      details: {
        current_time: '18:30',
        allowed_start: '09:00',
        allowed_end: '17:00'
      },
      is_active: false,
      is_acknowledged: true,
      created_at: '2024-01-14T18:30:00Z',
      acknowledged_at: '2024-01-14T18:35:00Z'
    },
    {
      id: '5',
      alert_type: 'correlation',
      severity: 'medium',
      message: 'High correlation detected between positions',
      details: {
        correlation: 0.85,
        threshold: 0.7,
        positions: ['BTCUSDT', 'ETHUSDT']
      },
      is_active: true,
      is_acknowledged: false,
      created_at: '2024-01-15T07:20:00Z',
      acknowledged_at: null
    }
  ];

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      case 'high':
        return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
      case 'medium':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'low':
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAlertTypeLabel = (type: string) => {
    switch (type) {
      case 'loss_limit':
        return 'Loss Limit';
      case 'position_limit':
        return 'Position Limit';
      case 'volatility':
        return 'Volatility';
      case 'correlation':
        return 'Correlation';
      case 'trading_hours':
        return 'Trading Hours';
      case 'leverage':
        return 'Leverage';
      case 'portfolio_risk':
        return 'Portfolio Risk';
      default:
        return type.replace('_', ' ').toUpperCase();
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now.getTime() - alertTime.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    }
  };

  const handleAcknowledge = (alertId: string) => {
    // In real app, this would call the API
    console.log('Acknowledging alert:', alertId);
    alert('Alert acknowledged!');
  };

  const filteredAlerts = alerts.filter(alert => {
    // Filter by acknowledgment status
    if (!showAcknowledged && alert.is_acknowledged) {
      return false;
    }
    
    // Filter by severity
    if (filterSeverity !== 'all' && alert.severity !== filterSeverity) {
      return false;
    }
    
    return true;
  });

  const activeAlerts = alerts.filter(alert => alert.is_active && !alert.is_acknowledged);
  const criticalAlerts = activeAlerts.filter(alert => alert.severity === 'critical');

  return (
    <div className="space-y-6">
      {/* Alerts Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Alerts</p>
              <p className="text-2xl font-bold text-gray-900">{alerts.length}</p>
            </div>
            <ExclamationTriangleIcon className="h-8 w-8 text-gray-400" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Alerts</p>
              <p className="text-2xl font-bold text-yellow-600">{activeAlerts.length}</p>
            </div>
            <ExclamationTriangleIcon className="h-8 w-8 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Critical Alerts</p>
              <p className="text-2xl font-bold text-red-600">{criticalAlerts.length}</p>
            </div>
            <ExclamationCircleIcon className="h-8 w-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={showAcknowledged}
                onChange={(e) => setShowAcknowledged(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">Show Acknowledged</span>
            </label>

            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div className="text-sm text-gray-500">
            {filteredAlerts.length} alert{filteredAlerts.length !== 1 ? 's' : ''} shown
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircleIcon className="mx-auto h-12 w-12 text-green-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Alerts</h3>
            <p className="mt-1 text-sm text-gray-500">
              {showAcknowledged ? 'No alerts found with current filters.' : 'All alerts have been acknowledged.'}
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-white p-4 rounded-lg border ${
                alert.is_acknowledged ? 'border-gray-200 opacity-75' : 'border-l-4 border-l-red-500'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {getSeverityIcon(alert.severity)}
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                        {alert.severity.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {getAlertTypeLabel(alert.alert_type)}
                      </span>
                      {alert.is_acknowledged && (
                        <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded flex items-center">
                          <CheckCircleIcon className="h-3 w-3 mr-1" />
                          Acknowledged
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm font-medium text-gray-900 mb-2">
                      {alert.message}
                    </p>
                    
                    {alert.details && (
                      <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                        <pre className="whitespace-pre-wrap">{JSON.stringify(alert.details, null, 2)}</pre>
                      </div>
                    )}
                    
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span className="flex items-center">
                        <ClockIcon className="h-3 w-3 mr-1" />
                        {formatTimeAgo(alert.created_at)}
                      </span>
                      
                      {alert.acknowledged_at && (
                        <span className="flex items-center">
                          <CheckCircleIcon className="h-3 w-3 mr-1" />
                          Acknowledged {formatTimeAgo(alert.acknowledged_at)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  {!alert.is_acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                      title="Acknowledge Alert"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  )}
                  
                  <button
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                    title="View Details"
                  >
                    <EyeSlashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-3">Quick Actions</h4>
        <div className="flex space-x-3">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
            Acknowledge All
          </button>
          <button className="bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors">
            Export Alerts
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors">
            Test Alert System
          </button>
        </div>
      </div>
    </div>
  );
};