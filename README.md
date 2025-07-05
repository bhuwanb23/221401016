# URL Shortener with Logging Middleware

A full-stack HTTP URL shortener microservice with comprehensive logging middleware integration. Built with React frontend using Material-UI and Flask backend with SQLite database.

## 🚀 Features

### Core Functionality
- ✅ **URL Shortening**: Create short, shareable links from long URLs
- ✅ **Custom Shortcodes**: Optional custom shortcodes for branded links
- ✅ **Expiry Management**: Configurable validity periods (default: 30 minutes)
- ✅ **Analytics**: Track clicks, IP addresses, and user agents
- ✅ **URL Management**: View and manage all shortened URLs
- ✅ **Health Monitoring**: Built-in health check endpoints

### Logging Middleware
- ✅ **Comprehensive Logging**: Full lifecycle logging for both frontend and backend
- ✅ **API Compliance**: Matches exact evaluation service API structure
- ✅ **Input Validation**: Validates stack, level, and package parameters
- ✅ **Error Handling**: Robust error handling with fallback logging
- ✅ **Performance Monitoring**: Tracks API call performance
- ✅ **Multiple Usage Patterns**: Class-based and function-based usage

## 📁 Project Structure

```
placement/
├── backend/
│   ├── app.py                 # Flask backend application
│   └── url_shortener.db       # SQLite database
├── logging_middleware/
│   ├── logger.py              # Python logging middleware
│   ├── test_logger.py         # Comprehensive test suite
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Logging middleware documentation
├── website/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── UrlsList.jsx       # URL management component
│   │   ├── logger.js          # JavaScript logging middleware
│   │   ├── App.css            # Styles
│   │   └── main.jsx           # React entry point
│   ├── package.json           # Node.js dependencies
│   └── vite.config.js         # Vite configuration
└── test_logging.py            # Simple logging test script
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install flask flask-cors requests
```

2. **Install logging middleware dependencies:**
```bash
cd ../logging_middleware
pip install -r requirements.txt
```

3. **Start the backend server:**
```bash
cd ../backend
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Install Node.js dependencies:**
```bash
cd website
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📊 Logging Middleware

### API Structure

The logging middleware sends POST requests to `http://20.244.56.144/evaluation-service/logs` with the following structure:

```json
{
  "stack": "backend",
  "level": "error",
  "package": "handler",
  "message": "received string, expected bool"
}
```

### Valid Parameters

#### Stacks
- `"backend"`
- `"frontend"`

#### Levels
- `"debug"`
- `"info"`
- `"warn"`
- `"error"`
- `"fatal"`

#### Backend Packages
- `"cache"`
- `"controller"`
- `"cron_job"`
- `"db"`
- `"domain"`
- `"handler"`
- `"respoistory"`
- `"route"`
- `"service"`

#### Frontend Packages
- `"api"`
- `"components"`
- `"hooks"`
- `"page"`
- `"state"`
- `"style"`

#### Shared Packages
- `"auth"`
- `"config"`
- `"middleware"`
- `"utils"`

### Usage Examples

#### Python (Backend)
```python
from logger import Log, log_info, log_error

# Basic logging
Log("backend", "info", "handler", "Request processed successfully")

# With context
log_error("backend", "db", "Database connection failed", 
          error_code="DB_001", retry_count=3)
```

#### JavaScript (Frontend)
```javascript
import { Log, logInfo, logError } from './logger';

// Basic logging
await Log("frontend", "info", "components", "Component rendered");

// With context
await logError("frontend", "api", "API request failed", 
               status: 500, endpoint: "/shorturls");
```

## 🔧 API Endpoints

### Backend Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shorturls` | Create a new shortened URL |
| GET | `/<shortcode>` | Redirect to original URL |
| GET | `/analytics/<shortcode>` | Get analytics for a shortcode |
| GET | `/urls` | Get all URLs with analytics |
| GET | `/health` | Health check endpoint |

### Request/Response Examples

#### Create Short URL
```bash
POST /shorturls
Content-Type: application/json

{
  "url": "https://example.com/very-long-url",
  "validity": 30,
  "shortcode": "custom123"  // Optional
}
```

Response:
```json
{
  "shortLink": "http://localhost:5000/abc123",
  "expiry": "2025-07-05T11:30:00Z"
}
```

#### Get Analytics
```bash
GET /analytics/abc123
```

Response:
```json
{
  "shortcode": "abc123",
  "original_url": "https://example.com/very-long-url",
  "created_at": "2025-07-05T10:30:00Z",
  "expires_at": "2025-07-05T11:00:00Z",
  "is_active": true,
  "total_accesses": 5,
  "recent_accesses": [
    {
      "accessed_at": "2025-07-05T10:45:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

## 🧪 Testing

### Test Logging Middleware

1. **Run comprehensive tests:**
```bash
cd logging_middleware
python test_logger.py
```

2. **Run simple test:**
```bash
python test_logging.py
```

### Test Backend

1. **Start the backend server**
2. **Test endpoints using curl or Postman**

Example:
```bash
# Create a short URL
curl -X POST http://localhost:5000/shorturls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "validity": 30}'

# Get all URLs
curl http://localhost:5000/urls

# Health check
curl http://localhost:5000/health
```

### Test Frontend

1. **Start both backend and frontend servers**
2. **Open http://localhost:5173 in your browser**
3. **Test URL shortening and management features**

## 📈 Logging Examples

### Backend Logging

The backend logs various events throughout the application lifecycle:

```python
# Database operations
log_info("backend", "db", "Database connection established")

# Request handling
log_info("backend", "handler", "URL shortening request received")

# Error handling
log_error("backend", "handler", "Invalid URL format received")

# Service events
log_info("backend", "service", "URL Shortener service started")
```

### Frontend Logging

The frontend logs user interactions and API calls:

```javascript
// Component events
await logInfo("frontend", "components", "URL form submitted");

// API calls
await logInfo("frontend", "api", "API request successful");

// User actions
await logDebug("frontend", "components", "Copy to clipboard action");

// Navigation
await logInfo("frontend", "page", "Tab navigation occurred");
```

## 🔍 Monitoring and Debugging

### Local Logging

The logging middleware creates local log files for debugging:
- `logging_middleware.log` - Detailed middleware logs
- Browser console - Frontend logging output

### Health Monitoring

The health check endpoint provides system status:
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-05T10:30:00Z",
  "database": "connected",
  "total_urls": 5
}
```

## 🚀 Deployment

### Backend Deployment

1. **Install production dependencies:**
```bash
pip install gunicorn
```

2. **Run with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend Deployment

1. **Build for production:**
```bash
npm run build
```

2. **Serve static files with a web server like nginx**

## 📝 License

This project is part of the URL Shortener assignment and follows the project's licensing terms.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add comprehensive logging
5. Test thoroughly
6. Submit a pull request

## 📞 Support

For issues related to:
- **Backend**: Check the Flask logs and database connectivity
- **Frontend**: Check browser console and network requests
- **Logging**: Check the logging middleware logs and API connectivity
- **Database**: Verify SQLite file permissions and schema

## 🎯 Key Features Summary

- ✅ **Full-stack URL shortener** with React + Flask
- ✅ **Comprehensive logging middleware** for both frontend and backend
- ✅ **Material-UI interface** with professional design
- ✅ **SQLite database** with analytics tracking
- ✅ **Custom shortcodes** and expiry management
- ✅ **Health monitoring** and error handling
- ✅ **API compliance** with evaluation service requirements
- ✅ **Extensive testing** and documentation 