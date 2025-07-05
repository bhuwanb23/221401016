from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
import sqlite3
import uuid
import string
import random
from datetime import datetime, timedelta
import json
import sys
import os

# Add the logging middleware to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'logging_middleware'))

# Import the logging middleware
try:
    from logger import Log, log_info, log_error, log_warn, log_debug, log_fatal
    LOGGING_AVAILABLE = True
except ImportError:
    # Fallback to simple logging if middleware is not available
    def Log(stack, level, package, message, **kwargs):
        print(f"LOG: {json.dumps({'stack': stack, 'level': level, 'package': package, 'message': message, **kwargs}, indent=2)}")
        return {"success": True, "status_code": 200}
    
    def log_info(stack, package, message, **kwargs):
        return Log(stack, "info", package, message, **kwargs)
    
    def log_error(stack, package, message, **kwargs):
        return Log(stack, "error", package, message, **kwargs)
    
    def log_warn(stack, package, message, **kwargs):
        return Log(stack, "warn", package, message, **kwargs)
    
    def log_debug(stack, package, message, **kwargs):
        return Log(stack, "debug", package, message, **kwargs)
    
    def log_fatal(stack, package, message, **kwargs):
        return Log(stack, "fatal", package, message, **kwargs)
    
    LOGGING_AVAILABLE = True

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    """Initialize the SQLite database with required tables."""
    try:
        log_info("backend", "db", "Initializing database", db_file="url_shortener.db")
        
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        
        # Create URLs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                shortcode TEXT UNIQUE NOT NULL,
                short_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        log_debug("backend", "db", "URLs table created/verified")
        
        # Add short_link column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE urls ADD COLUMN short_link TEXT')
            log_info("backend", "db", "Added short_link column to existing database")
        except sqlite3.OperationalError:
            # Column already exists
            log_debug("backend", "db", "short_link column already exists")
            pass
        
        # Create analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shortcode TEXT NOT NULL,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (shortcode) REFERENCES urls (shortcode)
            )
        ''')
        log_debug("backend", "db", "Analytics table created/verified")
        
        conn.commit()
        conn.close()
        
        log_info("backend", "db", "Database initialization completed successfully")
        
    except Exception as e:
        log_fatal("backend", "db", "Database initialization failed", error=str(e))
        raise

def log_request(operation, details, success=True, error_message=None):
    """Log requests using the logging middleware."""
    try:
        if success:
            log_info("backend", "handler", f"Operation completed: {operation}", 
                    operation=operation, details=details)
        else:
            log_error("backend", "handler", f"Operation failed: {operation}", 
                     operation=operation, details=details, error=error_message)
    except Exception as e:
        # Fallback to console if logging middleware is not available
        print(f"LOG: {json.dumps({'operation': operation, 'details': details, 'success': success, 'error_message': error_message})}")
        print(f"Logging middleware error: {e}")

def generate_shortcode(length=6):
    """Generate a random alphanumeric shortcode."""
    try:
        characters = string.ascii_letters + string.digits
        shortcode = ''.join(random.choice(characters) for _ in range(length))
        log_debug("backend", "utils", "Generated shortcode", shortcode=shortcode, length=length)
        return shortcode
    except Exception as e:
        log_error("backend", "utils", "Failed to generate shortcode", error=str(e), length=length)
        raise

def is_valid_url(url):
    """Validate if the provided URL is valid."""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        is_valid = all([result.scheme, result.netloc])
        log_debug("backend", "utils", "URL validation result", url=url, is_valid=is_valid)
        return is_valid
    except Exception as e:
        log_error("backend", "utils", "URL validation failed", url=url, error=str(e))
        return False

def is_valid_shortcode(shortcode):
    """Validate if the shortcode is alphanumeric and reasonable length."""
    try:
        if not shortcode:
            log_debug("backend", "utils", "Shortcode validation failed", reason="empty_shortcode")
            return False
        if len(shortcode) < 3 or len(shortcode) > 20:
            log_debug("backend", "utils", "Shortcode validation failed", 
                     reason="invalid_length", length=len(shortcode))
            return False
        is_valid = shortcode.isalnum()
        log_debug("backend", "utils", "Shortcode validation result", 
                 shortcode=shortcode, is_valid=is_valid)
        return is_valid
    except Exception as e:
        log_error("backend", "utils", "Shortcode validation failed", 
                 shortcode=shortcode, error=str(e))
        return False

def shortcode_exists(shortcode):
    """Check if a shortcode already exists in the database."""
    try:
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM urls WHERE shortcode = ? AND is_active = 1', (shortcode,))
        result = cursor.fetchone()
        conn.close()
        
        exists = result is not None
        log_debug("backend", "db", "Shortcode existence check", 
                 shortcode=shortcode, exists=exists)
        return exists
    except Exception as e:
        log_error("backend", "db", "Failed to check shortcode existence", 
                 shortcode=shortcode, error=str(e))
        return False

@app.route('/shorturls', methods=['POST'])
def create_short_url():
    """Create a new shortened URL."""
    try:
        log_info("backend", "handler", "URL shortening request received", 
                method=request.method, endpoint="/shorturls", ip=request.remote_addr)
        
        data = request.get_json()
        
        if not data:
            log_error("backend", "handler", "No JSON data provided in request")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract and validate required fields
        original_url = data.get('url')
        if not original_url:
            log_error("backend", "handler", "URL field missing from request", 
                     received_data=data)
            return jsonify({"error": "URL is required"}), 400
        
        if not is_valid_url(original_url):
            log_error("backend", "handler", "Invalid URL format received", 
                     received_url=original_url)
            return jsonify({"error": "Invalid URL format"}), 400
        
        # Extract optional fields
        validity = data.get('validity', 30)  # Default to 30 minutes
        custom_shortcode = data.get('shortcode')
        
        log_debug("backend", "handler", "Request parameters extracted", 
                 original_url=original_url, validity=validity, 
                 has_custom_shortcode=bool(custom_shortcode))
        
        # Validate validity
        if not isinstance(validity, int) or validity <= 0:
            log_error("backend", "handler", "Invalid validity parameter", 
                     received_validity=validity, type=type(validity).__name__)
            return jsonify({"error": "Validity must be a positive integer"}), 400
        
        # Handle custom shortcode
        if custom_shortcode:
            log_debug("backend", "handler", "Processing custom shortcode", 
                     custom_shortcode=custom_shortcode)
            
            if not is_valid_shortcode(custom_shortcode):
                log_error("backend", "handler", "Invalid custom shortcode format", 
                         custom_shortcode=custom_shortcode)
                return jsonify({"error": "Invalid shortcode format. Must be alphanumeric, 3-20 characters"}), 400
            
            if shortcode_exists(custom_shortcode):
                log_error("backend", "handler", "Custom shortcode already exists", 
                         custom_shortcode=custom_shortcode)
                return jsonify({"error": "Shortcode already exists"}), 409
            
            shortcode = custom_shortcode
            log_info("backend", "handler", "Using custom shortcode", shortcode=shortcode)
        else:
            # Generate unique shortcode
            log_debug("backend", "handler", "Generating random shortcode")
            shortcode = generate_shortcode()
            attempts = 1
            while shortcode_exists(shortcode):
                shortcode = generate_shortcode()
                attempts += 1
                if attempts > 10:
                    log_error("backend", "handler", "Failed to generate unique shortcode after 10 attempts")
                    return jsonify({"error": "Failed to generate unique shortcode"}), 500
            
            log_info("backend", "handler", "Generated unique shortcode", 
                    shortcode=shortcode, attempts=attempts)
        
        # Calculate expiry time
        expires_at = datetime.now() + timedelta(minutes=validity)
        short_link = f"http://{request.host}/{shortcode}"
        
        log_debug("backend", "handler", "URL details prepared", 
                 shortcode=shortcode, expires_at=expires_at.isoformat(), 
                 short_link=short_link)
        
        # Save to database
        try:
            conn = sqlite3.connect('url_shortener.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO urls (original_url, shortcode, short_link, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (original_url, shortcode, short_link, expires_at))
            conn.commit()
            conn.close()
            
            log_info("backend", "db", "URL saved to database successfully", 
                    shortcode=shortcode, url_id=cursor.lastrowid)
            
        except Exception as db_error:
            log_fatal("backend", "db", "Failed to save URL to database", 
                     error=str(db_error), shortcode=shortcode)
            return jsonify({"error": "Failed to save URL"}), 500
        
        # Create response
        response_data = {
            "shortLink": short_link,
            "expiry": expires_at.isoformat() + "Z"
        }
        
        log_info("backend", "handler", "URL shortened successfully", 
                original_url=original_url, shortcode=shortcode, 
                short_link=short_link, validity_minutes=validity)
        
        return jsonify(response_data), 201
        
    except Exception as e:
        log_error("backend", "handler", "Unexpected error in URL shortening", 
                 error=str(e), traceback=str(e.__traceback__))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/<shortcode>', methods=['GET'])
def redirect_to_original(shortcode):
    """Redirect to the original URL."""
    try:
        log_info("backend", "handler", "URL redirect request received", 
                shortcode=shortcode, method=request.method, ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', 'Unknown'))
        
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT original_url, expires_at, is_active 
            FROM urls 
            WHERE shortcode = ?
        ''', (shortcode,))
        result = cursor.fetchone()
        
        if not result:
            log_error("backend", "handler", "Shortcode not found in database", 
                     shortcode=shortcode, ip=request.remote_addr)
            return jsonify({"error": "Shortcode not found"}), 404
        
        original_url, expires_at, is_active = result
        
        log_debug("backend", "handler", "URL lookup successful", 
                 shortcode=shortcode, original_url=original_url, 
                 is_active=bool(is_active), expires_at=expires_at)
        
        if not is_active:
            log_warn("backend", "handler", "Attempted access to inactive link", 
                    shortcode=shortcode, ip=request.remote_addr)
            return jsonify({"error": "Link is inactive"}), 410
        
        # Check if link has expired
        current_time = datetime.now()
        expiry_time = datetime.fromisoformat(expires_at)
        is_expired = current_time > expiry_time
        
        if is_expired:
            log_warn("backend", "handler", "Attempted access to expired link", 
                    shortcode=shortcode, ip=request.remote_addr, 
                    current_time=current_time.isoformat(), 
                    expiry_time=expiry_time.isoformat())
            return jsonify({"error": "Link has expired"}), 410
        
        # Log analytics
        try:
            cursor.execute('''
                INSERT INTO analytics (shortcode, ip_address, user_agent)
                VALUES (?, ?, ?)
            ''', (shortcode, request.remote_addr, request.headers.get('User-Agent', '')))
            
            conn.commit()
            log_debug("backend", "db", "Analytics logged successfully", 
                     shortcode=shortcode, ip=request.remote_addr)
            
        except Exception as analytics_error:
            log_error("backend", "db", "Failed to log analytics", 
                     shortcode=shortcode, error=str(analytics_error))
            # Don't fail the redirect for analytics errors
        
        conn.close()
        
        log_info("backend", "handler", "URL redirect successful", 
                shortcode=shortcode, original_url=original_url, 
                ip=request.remote_addr, redirect_code=302)
        
        return redirect(original_url, code=302)
        
    except Exception as e:
        log_error("backend", "handler", "Unexpected error in URL redirect", 
                 shortcode=shortcode, error=str(e), ip=request.remote_addr)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/analytics/<shortcode>', methods=['GET'])
def get_analytics(shortcode):
    """Get analytics for a specific shortcode."""
    try:
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        
        # Get URL info
        cursor.execute('''
            SELECT original_url, created_at, expires_at, is_active
            FROM urls 
            WHERE shortcode = ?
        ''', (shortcode,))
        url_info = cursor.fetchone()
        
        if not url_info:
            log_request("analytics", {"shortcode": shortcode, "error": "Shortcode not found"}, False, "Shortcode not found")
            return jsonify({"error": "Shortcode not found"}), 404
        
        original_url, created_at, expires_at, is_active = url_info
        
        # Get access count
        cursor.execute('''
            SELECT COUNT(*) FROM analytics WHERE shortcode = ?
        ''', (shortcode,))
        access_count = cursor.fetchone()[0]
        
        # Get recent accesses
        cursor.execute('''
            SELECT accessed_at, ip_address, user_agent
            FROM analytics 
            WHERE shortcode = ?
            ORDER BY accessed_at DESC
            LIMIT 10
        ''', (shortcode,))
        recent_accesses = cursor.fetchall()
        
        conn.close()
        
        analytics_data = {
            "shortcode": shortcode,
            "original_url": original_url,
            "created_at": created_at,
            "expires_at": expires_at,
            "is_active": bool(is_active),
            "total_accesses": access_count,
            "recent_accesses": [
                {
                    "accessed_at": access[0],
                    "ip_address": access[1],
                    "user_agent": access[2]
                }
                for access in recent_accesses
            ]
        }
        
        log_request("analytics", {
            "shortcode": shortcode,
            "access_count": access_count
        }, True)
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        log_request("analytics", {"shortcode": shortcode, "error": str(e)}, False, str(e))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/urls', methods=['GET'])
def get_all_urls():
    """Get all URLs from the database."""
    try:
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        
        # Get all URLs with their analytics
        cursor.execute('''
            SELECT 
                u.id,
                u.original_url,
                u.shortcode,
                u.short_link,
                u.created_at,
                u.expires_at,
                u.is_active,
                COUNT(a.id) as access_count
            FROM urls u
            LEFT JOIN analytics a ON u.shortcode = a.shortcode
            GROUP BY u.id, u.original_url, u.shortcode, u.short_link, u.created_at, u.expires_at, u.is_active
            ORDER BY u.created_at DESC
        ''')
        
        urls = cursor.fetchall()
        conn.close()
        
        # Format the response
        urls_data = []
        for url in urls:
            url_id, original_url, shortcode, short_link, created_at, expires_at, is_active, access_count = url
            
            # Check if URL is expired
            is_expired = datetime.now() > datetime.fromisoformat(expires_at)
            
            # Use stored short_link or generate if not available (for backward compatibility)
            if not short_link:
                short_link = f"http://{request.host}/{shortcode}"
            
            urls_data.append({
                "id": url_id,
                "original_url": original_url,
                "shortcode": shortcode,
                "short_link": short_link,
                "created_at": created_at,
                "expires_at": expires_at,
                "is_active": bool(is_active),
                "is_expired": is_expired,
                "access_count": access_count
            })
        
        log_request("get_all_urls", {
            "total_urls": len(urls_data)
        }, True)
        
        return jsonify({
            "urls": urls_data,
            "total_count": len(urls_data)
        }), 200
        
    except Exception as e:
        log_request("get_all_urls", {"error": str(e)}, False, str(e))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    log_request("health_check", {}, True)
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    init_db()
    log_request("server_start", {"message": "URL Shortener service started"}, True)
    app.run(debug=True, host='0.0.0.0', port=5000)
