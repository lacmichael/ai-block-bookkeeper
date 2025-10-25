# AI Block Bookkeeper - Backend

A FastAPI-based backend service for the AI Block Bookkeeper application, providing health check endpoints and database connectivity to Supabase.

## 🏗️ Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Supabase**: Backend-as-a-Service for database and authentication
- **Pydantic**: Data validation and settings management
- **Structlog**: Structured logging for better observability
- **Uvicorn**: ASGI server for running the FastAPI application

## 📋 Prerequisites

- Python 3.9 or higher
- A Supabase project (get one at [supabase.com](https://supabase.com))

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the backend directory with your Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

**How to get your Supabase credentials:**

1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy the Project URL and API keys

### 5. Test the Setup

Run a one-time health check to verify your configuration:

```bash
python health_check.py
```

If successful, you'll see:

```
✅ Health check PASSED
   Status: Database connection successful
   Database: Connected to https://your-project.supabase.co
```

### 6. Start the Health Check Service

To run the health check service with API endpoints:

```bash
python health_check.py --server
```

Or use the convenience script:

```bash
./scripts/start_health_check.sh
```

The service will be available at `http://localhost:8000`

## 📡 API Endpoints

Once the service is running, you can access:

- **GET /** - Basic service information
- **GET /health** - Health check endpoint
- **GET /ready** - Readiness check (more detailed)
- **GET /status** - Detailed system status
- **GET /docs** - Interactive API documentation (Swagger UI)

### Example Health Check Response

```json
{
  "status": "healthy",
  "service": "AI Block Bookkeeper",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "database": {
    "status": "connected",
    "message": "Database connection successful",
    "details": {
      "supabase_url": "https://your-project.supabase.co",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "client_created": true
    }
  }
}
```

## 🗂️ Project Structure

```
backend/
├── config/
│   └── database.py          # Supabase configuration
├── models/
│   └── domain_models.py     # Pydantic models
├── services/
│   └── database_service.py  # Database operations
├── scripts/
│   └── start_health_check.sh # Convenience startup script
├── health_check.py          # Main health check application
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Development

### Adding New Endpoints

The health check service is built with FastAPI. To add new endpoints:

1. Edit `health_check.py`
2. Add your endpoint functions with appropriate decorators
3. Restart the service

### Database Operations

Use the `DatabaseService` class for database operations:

```python
from services.database_service import db_service

# Create a business event
event_data = {
    "event_id": "evt_123",
    "source_system": "blockchain",
    "event_type": "transaction",
    "data": {"amount": 100, "currency": "USD"}
}
result = await db_service.create_business_event(event_data)
```

### Logging

The application uses structured logging with `structlog`. Logs are output in JSON format for easy parsing:

```python
import structlog
logger = structlog.get_logger()
logger.info("Operation completed", user_id="123", action="create_event")
```

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**

```
❌ Import error: No module named 'supabase'
```

**Solution**: Make sure you've activated the virtual environment and installed requirements:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**2. Missing Environment Variables**

```
❌ Health check FAILED
   Error: Missing Supabase environment variables
```

**Solution**: Create a `.env` file with your Supabase credentials (see Environment Configuration above).

**3. Database Connection Issues**

```
❌ Health check FAILED
   Error: Database connection failed
```

**Solution**:

- Verify your Supabase URL and keys are correct
- Check that your Supabase project is active
- Ensure your network can reach Supabase

**4. Permission Denied on Script**

```
./scripts/start_health_check.sh: Permission denied
```

**Solution**: Make the script executable:

```bash
chmod +x scripts/start_health_check.sh
```

### Debug Mode

For more detailed logging, you can modify the logging configuration in `health_check.py` or set environment variables:

```bash
export LOG_LEVEL=DEBUG
python health_check.py --server
```

## 🔒 Security Notes

- Never commit your `.env` file to version control
- The service role key has elevated permissions - keep it secure
- Use environment variables for all sensitive configuration
- Consider using different keys for development and production

## 📚 Next Steps

1. **Set up your database schema** in the Supabase dashboard
2. **Build your main FastAPI application** using the health check as a foundation
3. **Implement your domain models** in `models/domain_models.py`
4. **Add authentication** using Supabase Auth
5. **Deploy to production** using your preferred hosting platform

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add appropriate logging for new features
3. Update this README if you add new setup requirements
4. Test your changes with the health check endpoints

## 📄 License

This project is part of the AI Block Bookkeeper application.
