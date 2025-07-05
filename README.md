# URL Shortener Microservice

A full-stack HTTP URL Shortener Microservice built with React (Material-UI) frontend and Flask backend, featuring comprehensive logging middleware integration.

## Features

- **URL Shortening**: Create short, shareable links with custom validity periods
- **Custom Shortcodes**: Option to provide custom shortcodes (3-20 alphanumeric characters)
- **Analytics**: Track link usage with detailed analytics
- **Logging Integration**: Extensive logging using custom middleware
- **Modern UI**: Beautiful Material-UI based React frontend
- **RESTful API**: Clean, well-documented API endpoints
- **Database**: SQLite database for data persistence
- **Error Handling**: Robust error handling with appropriate HTTP status codes

## Project Structure

```
placement/
├── backend/
│   ├── app.py              # Flask backend application
│   ├── requirements.txt    # Python dependencies
│   └── url_shortener.db    # SQLite database (created automatically)
├── website/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Custom styles
│   │   └── main.jsx        # React entry point
│   ├── package.json        # Node.js dependencies
│   └── index.html          # HTML template
├── logging_middleware/
│   └── register.py         # Logging middleware
└── register/
    └── auth.py             # Authorization module
```

## API Endpoints

### 1. Create Short URL
- **Method**: POST
- **URL**: `http://localhost:5000/shorturls`
- **Request Body**:
```json
{
  "url": "https://example.com/very-long-url",
  "validity": 30,
  "shortcode": "abcd1"
}
```
- **Response** (201):
```json
{
  "shortLink": "http://localhost:5000/abcd1",
  "expiry": "2025-01-01T00:30:00Z"
}
```

### 2. Redirect to Original URL
- **Method**: GET
- **URL**: `http://localhost:5000/{shortcode}`
- **Response**: 302 redirect to original URL

### 3. Get Analytics
- **Method**: GET
- **URL**: `http://localhost:5000/analytics/{shortcode}`
- **Response** (200):
```json
{
  "shortcode": "abcd1",
  "original_url": "https://example.com/very-long-url",
  "created_at": "2025-01-01T00:00:00",
  "expires_at": "2025-01-01T00:30:00",
  "is_active": true,
  "total_accesses": 5,
  "recent_accesses": [...]
}
```

### 4. Health Check
- **Method**: GET
- **URL**: `http://localhost:5000/health`
- **Response** (200):
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00"
}
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment** (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the Flask server**:
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. **Navigate to website directory**:
```bash
cd website
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start the development server**:
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## Usage

1. **Open the application** in your browser at `http://localhost:5173`

2. **Create a short URL**:
   - Enter a long URL
   - Set validity period (default: 30 minutes)
   - Optionally provide a custom shortcode
   - Click "Create Short URL"

3. **Use the short URL**:
   - Copy the generated short link
   - Share it with others
   - Click the link to redirect to the original URL

4. **View analytics**:
   - Click the analytics icon next to your short URL
   - View total accesses, recent visits, and other metrics

## Logging

The application uses a custom logging middleware that logs all operations including:
- URL creation
- Redirects
- Analytics requests
- Errors and exceptions

Logs are saved to:
- `api_requests.log` - API request logs
- `auth_requests.log` - Authorization logs
- Console output for debugging

## Database

The application uses SQLite with two main tables:

### URLs Table
- `id`: Primary key
- `original_url`: The original long URL
- `shortcode`: Unique shortcode for the URL
- `created_at`: Creation timestamp
- `expires_at`: Expiration timestamp
- `is_active`: Whether the link is active

### Analytics Table
- `id`: Primary key
- `shortcode`: Foreign key to URLs table
- `accessed_at`: Access timestamp
- `ip_address`: IP address of the visitor
- `user_agent`: User agent string

## Error Handling

The application handles various error scenarios:
- **400**: Invalid request data
- **404**: Shortcode not found
- **409**: Shortcode collision
- **410**: Link expired or inactive
- **500**: Internal server error

## Features Implemented

✅ **Mandatory Logging Integration**: Uses custom logging middleware  
✅ **Microservice Architecture**: Single Flask microservice  
✅ **Authentication**: Pre-authorized access (no login required)  
✅ **Short Link Uniqueness**: Globally unique shortcodes  
✅ **Default Validity**: 30 minutes default expiry  
✅ **Custom Shortcodes**: Optional user-provided shortcodes  
✅ **Redirection**: Proper HTTP redirects  
✅ **Error Handling**: Comprehensive error handling  
✅ **Analytics**: Basic analytical capabilities  
✅ **Material-UI**: Modern React UI with Material-UI  
✅ **RESTful API**: All required endpoints implemented  

## Development

### Adding New Features
1. Backend: Add new routes in `backend/app.py`
2. Frontend: Add new components in `website/src/`
3. Database: Add new tables/columns as needed
4. Logging: Use the `log_request()` function for all operations

### Testing
- Backend: Use tools like Postman or curl to test API endpoints
- Frontend: Use browser developer tools for debugging
- Database: Use SQLite browser to inspect data

## Deployment

### Backend Deployment
1. Set up a production WSGI server (e.g., Gunicorn)
2. Configure environment variables
3. Set up reverse proxy (e.g., Nginx)
4. Use production database (e.g., PostgreSQL)

### Frontend Deployment
1. Build the React app: `npm run build`
2. Serve static files with a web server
3. Configure API endpoint URLs for production

## License

This project is created for educational and evaluation purposes. 