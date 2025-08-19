# 🚀 Algorithmic Trading Platform

A comprehensive, production-ready algorithmic trading platform built with modern technologies, featuring real-time trading strategies, risk management, and exchange integrations.

## ✨ Features

### 🔐 **Authentication & Security**
- JWT-based authentication system
- Secure password hashing with bcrypt
- Role-based access control
- CORS protection and security headers

### 📊 **Trading Strategies**
- **Grid Trading**: Automated grid-based trading with configurable levels
- **Mean Reversion**: Statistical mean reversion strategy using SMA analysis
- **Momentum Trading**: Trend-following strategy with RSI and MACD indicators
- **Custom Strategy Framework**: Extensible strategy engine for custom algorithms

### 🛡️ **Risk Management**
- Configurable stop-loss and take-profit levels
- Daily, weekly, monthly, and total loss limits
- Position size and leverage controls
- Real-time risk monitoring and alerts
- Volatility and correlation controls
- Trading hours restrictions

### 💱 **Exchange Integration**
- **Binance**: Full API integration with testnet support
- **Bybit**: Complete V5 API integration
- **WebSocket Support**: Real-time price feeds and order updates
- **Multi-Exchange Support**: Unified interface for multiple exchanges

### 📈 **Trading Modes**
- **Paper Trading**: Risk-free strategy testing with virtual funds
- **Live Trading**: Production trading with enhanced safety controls
- **Mode Switching**: Seamless transition between paper and live trading
- **Balance Management**: Separate balance tracking for each mode

### 📊 **Dashboard & Analytics**
- Real-time portfolio monitoring
- Interactive charts with Recharts
- Performance metrics and P&L tracking
- Strategy performance analysis
- Risk metrics and alerts

### 🔧 **Technical Features**
- **FastAPI Backend**: High-performance Python backend
- **React Frontend**: Modern, responsive UI with TypeScript
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Redis Caching**: High-speed caching and message queuing
- **Docker Deployment**: Containerized deployment with Docker Compose
- **Comprehensive Logging**: Structured logging with file and database storage

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  PostgreSQL DB │
│   (TypeScript)  │◄──►│   (Python)      │◄──►│   + SQLAlchemy │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         │              │   (Caching)     │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Exchange APIs │              │
         │              │ (Binance/Bybit) │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  Risk Engine    │              │
         │              │   + Alerts      │              │
         │              └─────────────────┘              │
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/algorithmic-trading-platform.git
cd algorithmic-trading-platform
```

### 2. Environment Setup
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.development frontend/.env.local

# Edit environment variables
nano backend/.env
nano frontend/.env.local
```

### 3. Start Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## 🏭 Production Deployment

### 1. Production Environment Setup
```bash
# Copy production configuration
cp .env.production .env

# Edit production settings
nano .env
```

### 2. Deploy with Script
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 3. Manual Deployment
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Check service health
docker-compose -f docker-compose.prod.yml ps
```

## 📚 API Documentation

### Authentication Endpoints
```http
POST /auth/register     # User registration
POST /auth/login        # User authentication
GET  /auth/me           # Get current user
PUT  /auth/me           # Update user profile
```

### Strategy Endpoints
```http
GET    /strategies              # List user strategies
POST   /strategies              # Create new strategy
GET    /strategies/{id}         # Get strategy details
PUT    /strategies/{id}         # Update strategy
DELETE /strategies/{id}         # Delete strategy
POST   /strategies/{id}/action  # Start/stop strategy
```

### Risk Management Endpoints
```http
GET    /risk/profile            # Get risk profile
POST   /risk/profile            # Create risk profile
PUT    /risk/profile            # Update risk profile
GET    /risk/metrics            # Get risk metrics
POST   /risk/check              # Validate trade risk
GET    /risk/alerts             # Get risk alerts
```

### Trading Mode Endpoints
```http
GET    /trading-mode            # Get trading mode summary
POST   /trading-mode            # Create trading mode
PUT    /trading-mode            # Update trading mode
POST   /trading-mode/switch     # Switch between paper/live
GET    /trading-mode/statistics # Get trading statistics
```

### Exchange Endpoints
```http
GET    /exchanges               # List exchanges
POST   /exchanges/connect       # Connect to exchange
GET    /exchanges/prices        # Get market prices
POST   /exchanges/orders        # Place orders
GET    /exchanges/orders        # Get order history
```

## 🛠️ Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Database migrations
alembic upgrade head
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Database Management
```bash
# Connect to database
docker-compose exec postgres psql -U trading_user -d trading_platform

# Run migrations
docker-compose exec backend alembic upgrade head

# Create backup
docker-compose exec postgres pg_dump -U trading_user trading_platform > backup.sql
```

## 📊 Monitoring & Logging

### Log Files
- **Application Logs**: `logs/trading_platform.log`
- **Error Logs**: `logs/errors.log`
- **Trading Logs**: `logs/trading.log`
- **Nginx Logs**: `logs/nginx/`

### Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost/health

# Check individual services
docker-compose exec postgres pg_isready -U trading_user
docker-compose exec redis redis-cli ping
```

## 🔒 Security Features

### Authentication & Authorization
- JWT tokens with configurable expiration
- Password complexity requirements
- Rate limiting on authentication endpoints
- Session management and logout

### Data Protection
- HTTPS enforcement in production
- SQL injection prevention with SQLAlchemy
- XSS protection with React
- CORS configuration for API access

### Risk Controls
- Pre-trade risk validation
- Real-time position monitoring
- Automatic stop-loss enforcement
- Trading hour restrictions

## 📈 Performance & Scalability

### Backend Performance
- Async/await support with FastAPI
- Database connection pooling
- Redis caching for frequently accessed data
- Background task processing with Celery

### Frontend Performance
- React optimization with useMemo and useCallback
- Lazy loading of components
- Efficient state management
- Optimized bundle size

### Database Optimization
- Indexed queries for performance
- Connection pooling
- Query optimization
- Regular maintenance and cleanup

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database status
docker-compose exec postgres pg_isready -U trading_user

# Restart database
docker-compose restart postgres
```

#### Redis Connection Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

#### Frontend Build Issues
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Backend Import Errors
```bash
# Check Python path
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -c "import app"
```

### Log Analysis
```bash
# View real-time logs
docker-compose logs -f backend

# Search for errors
docker-compose logs backend | grep ERROR

# Check specific service logs
docker-compose logs frontend
```

## 🔄 Updates & Maintenance

### Updating the Platform
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose up -d --build
```

### Database Maintenance
```bash
# Create backup before updates
./backup.sh

# Run database migrations
docker-compose exec backend alembic upgrade head

# Clean up old logs
docker-compose exec backend python -c "from app.core.logging import LogEntry; LogEntry.cleanup_old_logs()"
```

### Monitoring Updates
```bash
# Update Prometheus configuration
docker-compose restart prometheus

# Update Grafana dashboards
docker-compose restart grafana
```

## 📋 Configuration Options

### Environment Variables

#### Backend Configuration
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Exchange APIs
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BYBIT_API_KEY=your_api_key
BYBIT_SECRET_KEY=your_secret_key

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production
```

#### Frontend Configuration
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DEBUG_MODE=false
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/TypeScript
- Write comprehensive tests
- Update documentation for new features

### Testing
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent Python web framework
- React team for the powerful frontend library
- PostgreSQL and Redis communities
- Trading strategy research and algorithms
- Open source community contributions

## 📞 Support

### Getting Help
- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Wiki**: Check the project wiki for detailed guides

### Community
- **Discord**: Join our trading community
- **Telegram**: Get real-time updates
- **Email**: support@yourdomain.com

---

**⚠️ Disclaimer**: This platform is for educational and research purposes. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

**🔒 Security**: Never share your API keys or credentials. Use testnet accounts for development and testing.

**📊 Compliance**: Ensure compliance with local regulations and exchange terms of service before using live trading features.
