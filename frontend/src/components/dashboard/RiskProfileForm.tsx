import React, { useState } from 'react';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  ClockIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

interface RiskProfileFormProps {
  riskProfile: any;
}

export const RiskProfileForm: React.FC<RiskProfileFormProps> = ({ riskProfile }) => {
  const [formData, setFormData] = useState({
    name: riskProfile?.name || "Conservative Profile",
    max_position_size: riskProfile?.max_position_size || 10000,
    max_positions: riskProfile?.max_positions || 5,
    max_leverage: riskProfile?.max_leverage || 1.0,
    daily_loss_limit: riskProfile?.daily_loss_limit || 1000,
    weekly_loss_limit: riskProfile?.weekly_loss_limit || 5000,
    monthly_loss_limit: riskProfile?.monthly_loss_limit || 20000,
    total_loss_limit: riskProfile?.total_loss_limit || 50000,
    default_stop_loss_percent: riskProfile?.default_stop_loss_percent || 5,
    default_take_profit_percent: riskProfile?.default_take_profit_percent || 10,
    trailing_stop_enabled: riskProfile?.trailing_stop_enabled || false,
    trailing_stop_percent: riskProfile?.trailing_stop_percent || 2,
    max_risk_per_trade: riskProfile?.max_risk_per_trade || 2,
    max_portfolio_risk: riskProfile?.max_portfolio_risk || 10,
    max_volatility_threshold: riskProfile?.max_volatility_threshold || 50,
    correlation_limit: riskProfile?.correlation_limit || 0.7,
    trading_hours_start: riskProfile?.trading_hours_start || "09:00",
    trading_hours_end: riskProfile?.trading_hours_end || "17:00",
    weekend_trading: riskProfile?.weekend_trading || false
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Basic validations
    if (formData.max_position_size <= 0) {
      errors.max_position_size = "Position size must be greater than 0";
    }

    if (formData.max_positions <= 0 || formData.max_positions > 100) {
      errors.max_positions = "Max positions must be between 1 and 100";
    }

    if (formData.daily_loss_limit <= 0) {
      errors.daily_loss_limit = "Daily loss limit must be greater than 0";
    }

    if (formData.weekly_loss_limit < formData.daily_loss_limit * 5) {
      errors.weekly_loss_limit = "Weekly loss limit should be at least 5x daily limit";
    }

    if (formData.monthly_loss_limit < formData.weekly_loss_limit * 3) {
      errors.monthly_loss_limit = "Monthly loss limit should be at least 3x weekly limit";
    }

    if (formData.default_stop_loss_percent <= 0 || formData.default_stop_loss_percent > 50) {
      errors.default_stop_loss_percent = "Stop loss must be between 0.1% and 50%";
    }

    if (formData.default_take_profit_percent <= 0 || formData.default_take_profit_percent > 100) {
      errors.default_take_profit_percent = "Take profit must be between 0.1% and 100%";
    }

    if (formData.trading_hours_end <= formData.trading_hours_start) {
      errors.trading_hours_end = "End time must be after start time";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In real app, this would call the API
      console.log('Saving risk profile:', formData);
      
      // Show success message
      alert('Risk profile saved successfully!');
      
    } catch (error) {
      console.error('Error saving risk profile:', error);
      alert('Error saving risk profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetToDefaults = () => {
    setFormData({
      name: "Conservative Profile",
      max_position_size: 10000,
      max_positions: 5,
      max_leverage: 1.0,
      daily_loss_limit: 1000,
      weekly_loss_limit: 5000,
      monthly_loss_limit: 20000,
      total_loss_limit: 50000,
      default_stop_loss_percent: 5,
      default_take_profit_percent: 10,
      trailing_stop_enabled: false,
      trailing_stop_percent: 2,
      max_risk_per_trade: 2,
      max_portfolio_risk: 10,
      max_volatility_threshold: 50,
      correlation_limit: 0.7,
      trading_hours_start: "09:00",
      trading_hours_end: "17:00",
      weekend_trading: false
    });
    setValidationErrors({});
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Risk Profile Configuration</h3>
        <button
          onClick={resetToDefaults}
          className="text-sm text-gray-600 hover:text-gray-800 underline"
        >
          Reset to Defaults
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
            <ShieldCheckIcon className="h-5 w-5 mr-2" />
            Basic Information
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Profile Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter profile name"
              />
            </div>
          </div>
        </div>

        {/* Position Limits */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
            <CurrencyDollarIcon className="h-5 w-5 mr-2" />
            Position Limits
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Position Size (USD)
              </label>
              <input
                type="number"
                value={formData.max_position_size}
                onChange={(e) => handleInputChange('max_position_size', parseFloat(e.target.value))}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.max_position_size ? 'border-red-500' : 'border-gray-300'
                }`}
                min="0"
                step="100"
              />
              {validationErrors.max_position_size && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.max_position_size}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Positions
              </label>
              <input
                type="number"
                value={formData.max_positions}
                onChange={(e) => handleInputChange('max_positions', parseInt(e.target.value))}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.max_positions ? 'border-red-500' : 'border-gray-300'
                }`}
                min="1"
                max="100"
              />
              {validationErrors.max_positions && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.max_positions}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Leverage
              </label>
              <input
                type="number"
                value={formData.max_leverage}
                onChange={(e) => handleInputChange('max_leverage', parseFloat(e.target.value))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="0.1"
                max="100"
                step="0.1"
              />
            </div>
          </div>
        </div>

        {/* Loss Limits */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            Loss Limits
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Daily Loss Limit (USD)
              </label>
              <input
                type="number"
                value={formData.daily_loss_limit}
                onChange={(e) => handleInputChange('daily_loss_limit', parseFloat(e.target.value))}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.daily_loss_limit ? 'border-red-500' : 'border-gray-300'
                }`}
                min="0"
                step="100"
              />
              {validationErrors.daily_loss_limit && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.daily_loss_limit}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Weekly Loss Limit (USD)
              </label>
              <input
                type="number"
                value={formData.weekly_loss_limit}
                onChange={(e) => handleInputChange('weekly_loss_limit', parseFloat(e.target.value))}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.weekly_loss_limit ? 'border-red-500' : 'border-gray-300'
                }`}
                min="0"
                step="100"
              />
              {validationErrors.weekly_loss_limit && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.weekly_loss_limit}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Monthly Loss Limit (USD)
              </label>
              <input
                type="number"
                value={formData.monthly_loss_limit}
                onChange={(e) => handleInputChange('monthly_loss_limit', parseFloat(e.target.value))}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.monthly_loss_limit ? 'border-red-500' : 'border-gray-300'
                }`}
                min="0"
                step="100"
              />
              {validationErrors.monthly_loss_limit && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.monthly_loss_limit}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Total Loss Limit (USD)
              </label>
              <input
                type="number"
                value={formData.total_loss_limit}
                onChange={(e) => handleInputChange('total_loss_limit', parseFloat(e.target.value))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="0"
                step="1000"
              />
            </div>
          </div>
        </div>

        {/* Stop Loss & Take Profit */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-md font-medium text-gray-900 mb-4">Stop Loss & Take Profit</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Stop Loss (%)
              </label>
              <input
                type="number"
                value={formData.default_stop_loss_percent}
                onChange={(e) => handleInputChange('default_stop_loss_percent', parseFloat(e.target.value))}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.default_stop_loss_percent ? 'border-red-500' : 'border-gray-300'
                }`}
                min="0.1"
                max="50"
                step="0.1"
              />
              {validationErrors.default_stop_loss_percent && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.default_stop_loss_percent}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Take Profit (%)
              </label>
              <input
                type="number"
                value={formData.default_take_profit_percent}
                onChange={(e) => handleInputChange('default_take_profit_percent', parseFloat(e.target.value))}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.default_take_profit_percent ? 'border-red-500' : 'border-gray-300'
                }`}
                min="0.1"
                max="100"
                step="0.1"
              />
              {validationErrors.default_take_profit_percent && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.default_take_profit_percent}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trailing Stop (%)
              </label>
              <input
                type="number"
                value={formData.trailing_stop_percent}
                onChange={(e) => handleInputChange('trailing_stop_percent', parseFloat(e.target.value))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="0.1"
                max="20"
                step="0.1"
                disabled={!formData.trailing_stop_enabled}
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.trailing_stop_enabled}
                onChange={(e) => handleInputChange('trailing_stop_enabled', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">Enable Trailing Stop Loss</span>
            </label>
          </div>
        </div>

        {/* Trading Hours */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
            <ClockIcon className="h-5 w-5 mr-2" />
            Trading Hours
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Time
              </label>
              <input
                type="time"
                value={formData.trading_hours_start}
                onChange={(e) => handleInputChange('trading_hours_start', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Time
              </label>
              <input
                type="time"
                value={formData.trading_hours_end}
                onChange={(e) => handleInputChange('trading_hours_end', e.target.value)}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  validationErrors.trading_hours_end ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {validationErrors.trading_hours_end && (
                <p className="text-red-500 text-sm mt-1">{validationErrors.trading_hours_end}</p>
              )}
            </div>

            <div className="flex items-end">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.weekend_trading}
                  onChange={(e) => handleInputChange('weekend_trading', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Allow Weekend Trading</span>
              </label>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={resetToDefaults}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Saving...' : 'Save Risk Profile'}
          </button>
        </div>
      </form>
    </div>
  );
};
