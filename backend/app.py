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
    from register import make_api_request
except ImportError:
    # Fallback to simple logging if middleware is not available
    def make_api_request(url, method="POST", data=None, **kwargs):
        print(f"LOG: {json.dumps(data, indent=2)}")
        return {"success": True}

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    """Initialize the SQLite database with required tables."""
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
    
    # Add short_link column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE urls ADD COLUMN short_link TEXT')
    except sqlite3.OperationalError:
        # Column already exists
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
    
    conn.commit()
    conn.close()

def log_request(operation, details, success=True, error_message=None):
    """Log requests using the logging middleware."""
    log_data = {
        "operation": operation,
        "details": details,
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "error_message": error_message
    }
    
    # Use the logging middleware to log the request
    try:
        make_api_request(
            url="http://localhost:5000/log",  # Internal logging endpoint
            method="POST",
            data=log_data
        )
    except Exception as e:
        # Fallback to console if logging middleware is not available
        print(f"LOG: {json.dumps(log_data)}")
        print(f"Logging middleware error: {e}")

def generate_shortcode(length=6):
    """Generate a random alphanumeric shortcode."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_url(url):
    """Validate if the provided URL is valid."""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_valid_shortcode(shortcode):
    """Validate if the shortcode is alphanumeric and reasonable length."""
    if not shortcode:
        return False
    if len(shortcode) < 3 or len(shortcode) > 20:
        return False
    return shortcode.isalnum()

def shortcode_exists(shortcode):
    """Check if a shortcode already exists in the database."""
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM urls WHERE shortcode = ? AND is_active = 1', (shortcode,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

@app.route('/shorturls', methods=['POST'])
def create_short_url():
    """Create a new shortened URL."""
    try:
        data = request.get_json()
        
        if not data:
            log_request("create_short_url", {"error": "No JSON data provided"}, False, "No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract and validate required fields
        original_url = data.get('url')
        if not original_url:
            log_request("create_short_url", {"error": "URL is required"}, False, "URL is required")
            return jsonify({"error": "URL is required"}), 400
        
        if not is_valid_url(original_url):
            log_request("create_short_url", {"error": "Invalid URL format"}, False, "Invalid URL format")
            return jsonify({"error": "Invalid URL format"}), 400
        
        # Extract optional fields
        validity = data.get('validity', 30)  # Default to 30 minutes
        custom_shortcode = data.get('shortcode')
        
        # Validate validity
        if not isinstance(validity, int) or validity <= 0:
            log_request("create_short_url", {"error": "Validity must be a positive integer"}, False, "Invalid validity")
            return jsonify({"error": "Validity must be a positive integer"}), 400
        
        # Handle custom shortcode
        if custom_shortcode:
            if not is_valid_shortcode(custom_shortcode):
                log_request("create_short_url", {"error": "Invalid shortcode format"}, False, "Invalid shortcode format")
                return jsonify({"error": "Invalid shortcode format. Must be alphanumeric, 3-20 characters"}), 400
            
            if shortcode_exists(custom_shortcode):
                log_request("create_short_url", {"error": "Shortcode already exists"}, False, "Shortcode collision")
                return jsonify({"error": "Shortcode already exists"}), 409
            
            shortcode = custom_shortcode
        else:
            # Generate unique shortcode
            shortcode = generate_shortcode()
            while shortcode_exists(shortcode):
                shortcode = generate_shortcode()
        
        # Calculate expiry time
        expires_at = datetime.now() + timedelta(minutes=validity)
        
        # Generate the short link
        short_link = f"http://{request.host}/{shortcode}"
        
        # Save to database
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO urls (original_url, shortcode, short_link, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (original_url, shortcode, short_link, expires_at))
        conn.commit()
        conn.close()
        
        # Create response
        response_data = {
            "shortLink": short_link,
            "expiry": expires_at.isoformat() + "Z"
        }
        
        log_request("create_short_url", {
            "original_url": original_url,
            "shortcode": shortcode,
            "validity": validity,
            "short_link": short_link
        }, True)
        
        return jsonify(response_data), 201
        
    except Exception as e:
        log_request("create_short_url", {"error": str(e)}, False, str(e))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/<shortcode>', methods=['GET'])
def redirect_to_original(shortcode):
    """Redirect to the original URL."""
    try:
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT original_url, expires_at, is_active 
            FROM urls 
            WHERE shortcode = ?
        ''', (shortcode,))
        result = cursor.fetchone()
        
        if not result:
            log_request("redirect", {"shortcode": shortcode, "error": "Shortcode not found"}, False, "Shortcode not found")
            return jsonify({"error": "Shortcode not found"}), 404
        
        original_url, expires_at, is_active = result
        
        if not is_active:
            log_request("redirect", {"shortcode": shortcode, "error": "Link is inactive"}, False, "Link is inactive")
            return jsonify({"error": "Link is inactive"}), 410
        
        # Check if link has expired
        if datetime.now() > datetime.fromisoformat(expires_at):
            log_request("redirect", {"shortcode": shortcode, "error": "Link has expired"}, False, "Link expired")
            return jsonify({"error": "Link has expired"}), 410
        
        # Log analytics
        cursor.execute('''
            INSERT INTO analytics (shortcode, ip_address, user_agent)
            VALUES (?, ?, ?)
        ''', (shortcode, request.remote_addr, request.headers.get('User-Agent', '')))
        
        conn.commit()
        conn.close()
        
        log_request("redirect", {
            "shortcode": shortcode,
            "original_url": original_url,
            "ip_address": request.remote_addr
        }, True)
        
        return redirect(original_url, code=302)
        
    except Exception as e:
        log_request("redirect", {"shortcode": shortcode, "error": str(e)}, False, str(e))
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
