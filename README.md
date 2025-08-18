# 🚀 Algorithmic Trading Platform

A full-stack algorithmic trading platform with multiple trading strategies, real-time data, and comprehensive risk management.

## 🏗️ Architecture

- **Frontend**: React + TypeScript + TailwindCSS + Recharts
- **Backend**: FastAPI (Python) + SQLAlchemy + PostgreSQL
- **Deployment**: Docker + Docker Compose
- **Exchanges**: Binance + Bybit (Testnet support)
- **Strategies**: Grid Trading, Mean Reversion, Momentum

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd algorithmic-trading-platform
```

### 2. Environment Configuration
```bash
# Copy environment file
cp backend/.env.example backend/.env

# Edit with your API keys
nano backend/.env
```

### 3. Start with Docker
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access the Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (user: trading_user, pass: trading_password)

## 🏃‍♂️ Local Development

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📊 Features

### Trading Strategies
- **Grid Trading**: Automated buy/sell orders at predefined price levels
- **Mean Reversion**: Capitalizes on price deviations from moving averages
- **Momentum**: Follows trending price movements

### Risk Management
- Configurable stop-loss and take-profit levels
- Daily loss limits
- Position sizing controls
- Paper trading mode

### Real-time Data
- Live price feeds via WebSocket
- Historical data storage
- Multi-exchange support (Binance + Bybit)

## 🔧 Configuration

### Strategy Parameters
Each strategy can be configured with:
- Trading pairs
- Position sizes
- Risk parameters
- Execution frequency

### Exchange Setup
1. Create testnet accounts on Binance and Bybit
2. Generate API keys with trading permissions
3. Add keys to `.env` file
4. Test connectivity before live trading

## 🚨 Security Notes

- **NEVER** commit API keys to version control
- Use testnet accounts for development
- Change default passwords in production
- Enable 2FA on exchange accounts
- Regular security audits

## 📁 Project Structure

```
├── frontend/                 # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Configuration
│   │   ├── db/              # Database models
│   │   ├── models/          # Data models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── strategies/      # Trading strategies
│   ├── main.py
│   └── requirements.txt
├── docker/                   # Docker configurations
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml        # Service orchestration
└── README.md
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring

- Real-time trade logging
- Performance metrics
- Error tracking
- Strategy performance analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading cryptocurrencies involves substantial risk. Always test thoroughly on testnet before using real funds. The authors are not responsible for any financial losses.

## 🆘 Support

For issues and questions:
- Check the documentation
- Review existing issues
- Create a new issue with detailed information
