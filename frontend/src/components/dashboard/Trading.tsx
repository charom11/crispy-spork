import React, { useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

export const Trading: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [orderType, setOrderType] = useState('limit');
  const [orderSide, setOrderSide] = useState('buy');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [showOrderBook, setShowOrderBook] = useState(true);

  // Mock data - in real app, this would come from API
  const priceData = [
    { time: '09:00', price: 52000, volume: 1250 },
    { time: '10:00', price: 52150, volume: 980 },
    { time: '11:00', price: 51900, volume: 1450 },
    { time: '12:00', price: 52200, volume: 1100 },
    { time: '13:00', price: 52450, volume: 1350 },
    { time: '14:00', price: 52300, volume: 1200 },
    { time: '15:00', price: 52500, volume: 1600 },
    { time: '16:00', price: 52650, volume: 1400 },
  ];

  const orderBookData = {
    asks: [
      { price: 52650, quantity: 0.5, total: 0.5 },
      { price: 52600, quantity: 1.2, total: 1.7 },
      { price: 52550, quantity: 0.8, total: 2.5 },
      { price: 52500, quantity: 2.1, total: 4.6 },
      { price: 52450, quantity: 1.5, total: 6.1 },
    ],
    bids: [
      { price: 52400, quantity: 1.8, total: 1.8 },
      { price: 52350, quantity: 2.3, total: 4.1 },
      { price: 52300, quantity: 1.6, total: 5.7 },
      { price: 52250, quantity: 0.9, total: 6.6 },
      { price: 52200, quantity: 1.4, total: 8.0 },
    ]
  };

  const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT'];

  const handlePlaceOrder = () => {
    // In real app, this would call the API
    console.log('Placing order:', { orderType, orderSide, quantity, price, symbol: selectedSymbol });
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trading</h1>
        <p className="mt-1 text-sm text-gray-500">
          Real-time trading interface with advanced charts and order management.
        </p>
      </div>

      {/* Symbol selector and price info */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-lg font-semibold"
            >
              {symbols.map(symbol => (
                <option key={symbol} value={symbol}>{symbol}</option>
              ))}
            </select>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">$52,450.00</div>
              <div className="text-sm text-green-600">+$450.00 (+0.87%)</div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowOrderBook(!showOrderBook)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
            >
              {showOrderBook ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Price Chart */}
        <div className="h-64 mb-6">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={['dataMin - 100', 'dataMax + 100']} />
              <Tooltip 
                formatter={(value: any, name: any) => [`$${value.toLocaleString()}`, name]}
                labelFormatter={(label) => `Time: ${label}`}
              />
              <Area 
                type="monotone" 
                dataKey="price" 
                stroke="#3B82F6" 
                fill="#3B82F6" 
                fillOpacity={0.1}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Trading interface */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Order Book */}
          {showOrderBook && (
            <div className="lg:col-span-1">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Order Book</h3>
              <div className="space-y-1">
                {/* Asks (Sell orders) */}
                {orderBookData.asks.slice().reverse().map((ask, index) => (
                  <div key={`ask-${index}`} className="flex justify-between text-sm">
                    <span className="text-red-600">{ask.price.toLocaleString()}</span>
                    <span className="text-gray-600">{ask.quantity.toFixed(2)}</span>
                    <span className="text-gray-500">{ask.total.toFixed(2)}</span>
                  </div>
                ))}
                
                {/* Spread */}
                <div className="border-t border-gray-200 pt-1 mt-2">
                  <div className="flex justify-between text-sm font-medium">
                    <span>Spread</span>
                    <span className="text-gray-600">$250.00 (0.48%)</span>
                  </div>
                </div>
                
                {/* Bids (Buy orders) */}
                {orderBookData.bids.map((bid, index) => (
                  <div key={`bid-${index}`} className="flex justify-between text-sm">
                    <span className="text-green-600">{bid.price.toLocaleString()}</span>
                    <span className="text-gray-600">{bid.quantity.toFixed(2)}</span>
                    <span className="text-gray-500">{bid.total.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trading Form */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Place Order</h3>
            <div className="space-y-4">
              {/* Order Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Order Type
                </label>
                <div className="flex space-x-2">
                  {['market', 'limit', 'stop_loss', 'take_profit'].map(type => (
                    <button
                      key={type}
                      onClick={() => setOrderType(type)}
                      className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        orderType === type
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type.replace('_', ' ').toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              {/* Order Side */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Order Side
                </label>
                <div className="flex space-x-2">
                  {['buy', 'sell'].map(side => (
                    <button
                      key={side}
                      onClick={() => setOrderSide(side)}
                      className={`flex-1 px-4 py-3 text-sm font-medium rounded-md transition-colors ${
                        orderSide === side
                          ? side === 'buy'
                            ? 'bg-green-600 text-white'
                            : 'bg-red-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <div className="flex items-center justify-center space-x-2">
                        {side === 'buy' ? (
                          <ArrowUpIcon className="h-4 w-4" />
                        ) : (
                          <ArrowDownIcon className="h-4 w-4" />
                        )}
                        <span>{side.toUpperCase()}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Quantity and Price */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity
                  </label>
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="0.00"
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price
                  </label>
                  <input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    placeholder="0.00"
                    disabled={orderType === 'market'}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                  />
                </div>
              </div>

              {/* Order Summary */}
              {quantity && price && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Order Summary</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Total Value:</span>
                      <span className="font-medium">${(parseFloat(quantity) * parseFloat(price)).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Fee:</span>
                      <span className="font-medium">$0.00</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Place Order Button */}
              <button
                onClick={handlePlaceOrder}
                disabled={!quantity || (!price && orderType !== 'market')}
                className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
                  orderSide === 'buy'
                    ? 'bg-green-600 hover:bg-green-700 text-white disabled:bg-gray-300'
                    : 'bg-red-600 hover:bg-red-700 text-white disabled:bg-gray-300'
                }`}
              >
                Place {orderSide.toUpperCase()} Order
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
