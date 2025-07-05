# Logging Middleware

A comprehensive logging middleware system that sends logs to the evaluation service with proper validation and error handling.

## Features

- ✅ **Full API Compliance**: Matches the exact API structure required
- ✅ **Input Validation**: Validates stack, level, and package parameters
- ✅ **Error Handling**: Robust error handling with fallback logging
- ✅ **Performance Monitoring**: Tracks API call performance
- ✅ **Multiple Usage Patterns**: Supports both class-based and function-based usage
- ✅ **Comprehensive Testing**: Includes test suite for all scenarios

## Installation

```bash
cd logging_middleware
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from logger import Log

# Basic log
Log("backend", "info", "db", "Database connection established")

# Log with context
Log("frontend", "error", "api", "API request failed", 
    status_code=500, endpoint="/shorturls")
```

### Convenience Functions

```python
from logger import log_info, log_error, log_warn, log_debug, log_fatal

# Info level
log_info("backend", "service", "Service started", port=5000)

# Error level
log_error("frontend", "components", "Component failed to render", 
          component="UrlForm")

# Warning level
log_warn("backend", "db", "High memory usage", usage="85%")

# Debug level
log_debug("frontend", "state", "State updated", action="SET_URLS")

# Fatal level
log_fatal("backend", "db", "Database corruption detected")
```

### Class-based Usage

```python
from logger import LoggingMiddleware

logger = LoggingMiddleware()

# Use the logger instance
logger.info("backend", "handler", "Request processed", 
           request_id="req_123", duration_ms=150)
```

## Valid Parameters

### Stacks
- `"backend"`
- `"frontend"`

### Levels
- `"debug"`
- `"info"`
- `"warn"`
- `"error"`
- `"fatal"`

### Backend Packages
- `"cache"`
- `"controller"`
- `"cron_job"`
- `"db"`
- `"domain"`
- `"handler"`
- `"respoistory"`
- `"route"`
- `"service"`

### Frontend Packages
- `"api"`
- `"components"`
- `"hooks"`
- `"page"`
- `"state"`
- `"style"`

### Shared Packages (Both Backend and Frontend)
- `"auth"`
- `"config"`
- `"middleware"`
- `"utils"`

## API Structure

The middleware sends POST requests to `http://20.244.56.144/evaluation-service/logs` with the following structure:

```json
{
  "stack": "backend",
  "level": "error",
  "package": "handler",
  "message": "received string, expected bool"
}
```

## Response Format

Successful responses (Status 200):
```json
{
  "logID": "a4aad02e-19d0-4153-86d9-58bf55d7c402",
  "message": "log created successfully"
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_logger.py
```

The test suite covers:
- ✅ Valid logging scenarios
- ✅ Invalid input handling
- ✅ Performance testing
- ✅ All package types
- ✅ All log levels
- ✅ Convenience functions

## Error Handling

The middleware includes comprehensive error handling:

- **Validation Errors**: Invalid parameters are logged locally and return `None`
- **Network Errors**: Timeouts and connection failures are handled gracefully
- **API Errors**: Non-200 responses are logged with details
- **Unexpected Errors**: All exceptions are caught and logged

## Local Logging

The middleware also logs to a local file (`logging_middleware.log`) for debugging purposes. This includes:
- API call status and timing
- Validation errors
- Network errors
- Successful log creation confirmations

## Integration Examples

### Backend Integration (Flask)

```python
from logger import Log

@app.route('/shorturls', methods=['POST'])
def create_short_url():
    try:
        Log("backend", "info", "handler", "URL shortening request received")
        
        data = request.get_json()
        if not data:
            Log("backend", "error", "handler", "No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Process request...
        Log("backend", "info", "handler", "URL shortened successfully", 
            shortcode=shortcode)
        
    except Exception as e:
        Log("backend", "error", "handler", "Exception in URL shortening", 
            error=str(e))
        return jsonify({"error": "Internal server error"}), 500
```

### Frontend Integration (React)

```javascript
import { Log } from './logger';

// In a React component
const handleSubmit = async (formData) => {
  try {
    Log("frontend", "info", "components", "Form submission started", 
        formData: formData);
    
    const response = await fetch('/api/shorturls', {
      method: 'POST',
      body: JSON.stringify(formData)
    });
    
    if (response.ok) {
      Log("frontend", "info", "api", "API request successful", 
          status: response.status);
    } else {
      Log("frontend", "error", "api", "API request failed", 
          status: response.status, error: await response.text());
    }
  } catch (error) {
    Log("frontend", "error", "components", "Form submission failed", 
        error: error.message);
  }
};
```

## Performance Considerations

- **Timeout**: API calls have a 10-second timeout
- **Session Reuse**: Uses `requests.Session()` for connection pooling
- **Async Ready**: Can be easily adapted for async usage
- **Batch Logging**: Consider batching logs for high-volume scenarios

## Troubleshooting

### Common Issues

1. **Invalid Package Error**: Ensure the package is valid for your stack
2. **Network Timeout**: Check network connectivity to the evaluation service
3. **API Errors**: Verify the API endpoint is accessible

### Debug Mode

Enable detailed logging by checking the `logging_middleware.log` file for:
- API call details
- Validation errors
- Network issues
- Performance metrics

## License

This logging middleware is part of the URL Shortener project and follows the project's licensing terms. 