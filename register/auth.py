import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auth_requests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APIClient:
    """
    A client for making API requests with JSON format and handling responses.
    """
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL for API requests
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'APIClient/1.0'
        })
    
    def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an API request and return the response.
        
        Args:
            method (str): HTTP method (POST)
            endpoint (str): API endpoint path
            data (dict, optional): JSON data to send in request body
            params (dict, optional): Query parameters
            headers (dict, optional): Additional headers
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            dict: Response data and metadata
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        
        request_data = {
            'url': url,
            'method': method.upper(),
            'params': params or {},
            'headers': headers or {},
            'timeout': self.timeout,
            **kwargs
        }
        
        if data is not None:
            request_data['json'] = data
        
        logger.info(f"Making {method.upper()} request to: {url}")
        if data:
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            response = self.session.request(**request_data)
            
            logger.info(f"Response status: {response.status_code}")
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text}
            
            result = {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "url": url,
                "method": method.upper(),
                "request_data": data,
                "response_data": response_data,
                "headers": dict(response.headers),
                "timestamp": datetime.now().isoformat(),
                "elapsed_time": response.elapsed.total_seconds()
            }
            
            if result["success"]:
                logger.info(f"Request successful: {response.status_code}")
            else:
                logger.error(f"Request failed: {response.status_code} - {response.text}")
            
            return result
            
        except requests.RequestException as e:
            error_result = {
                "success": False,
                "error": str(e),
                "url": url,
                "method": method.upper(),
                "request_data": data,
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Request exception: {e}")
            return error_result
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self.make_request("POST", endpoint, data=data, **kwargs)

def make_api_request(
    url: str, 
    method: str = "POST", 
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to make a single API request.
    
    Args:
        url (str): Full URL to make request to
        method (str): HTTP method
        data (dict, optional): JSON data to send
        params (dict, optional): Query parameters
        headers (dict, optional): Additional headers
        
    Returns:
        dict: Response data and metadata
    """
    client = APIClient()
    return client.make_request(method, url, data=data, params=params, headers=headers)

def format_json_response(response_data: Dict[str, Any], pretty: bool = True) -> str:
    """
    Format response data as JSON string.
    
    Args:
        response_data (dict): Response data to format
        pretty (bool): Whether to format with indentation
        
    Returns:
        str: Formatted JSON string
    """
    if pretty:
        return json.dumps(response_data, indent=2, ensure_ascii=False)
    return json.dumps(response_data, ensure_ascii=False)

def authorize_user(
    email: str,
    name: str,
    roll_no: str,
    access_code: str,
    client_id: str,
    client_secret: str
) -> Dict[str, Any]:
    """
    Authorize a user with the evaluation service.
    
    Args:
        email (str): User's email address
        name (str): User's full name
        roll_no (str): User's roll number
        access_code (str): Access code for authorization
        client_id (str): Client ID from registration
        client_secret (str): Client secret from registration
        
    Returns:
        dict: Authorization response with user details
    """
    url = "http://20.244.56.144/evaluation-service/auth"
    
    authorization_data = {
        "email": email,
        "name": name,
        "rollNo": roll_no,
        "accessCode": access_code,
        "clientID": client_id,
        "clientSecret": client_secret
    }
    
    response = make_api_request(
        url=url,
        method="POST",
        data=authorization_data
    )
    
    return response

def save_authorization_details(response: Dict[str, Any], filename: str = "authorization_details.json") -> bool:
    """
    Save authorization response details to a file.
    
    Args:
        response (dict): The API response from authorization
        filename (str): Name of the file to save the details
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        if response.get("success") and response.get("response_data"):
            api_response = response["response_data"]

            details_to_save = {
                "email": api_response.get("email"),
                "name": api_response.get("name"),
                "rollNo": api_response.get("rollNo"),
                "accessCode": api_response.get("accessCode"),
                "clientID": api_response.get("clientID"),
                "clientSecret": api_response.get("clientSecret"),
                "authorization_timestamp": response.get("timestamp"),
                "status": "success" if response.get("success") else "failed"
            }
        else:
            details_to_save = {
                "error": response.get("error", "Unknown error"),
                "status_code": response.get("status_code"),
                "authorization_timestamp": response.get("timestamp"),
                "status": "failed"
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(details_to_save, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Authorization details saved to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save authorization details: {e}")
        return False

def authorize_and_save(
    email: str,
    name: str,
    roll_no: str,
    access_code: str,
    client_id: str,
    client_secret: str,
    filename: str = "authorization_details.json"
) -> Dict[str, Any]:
    """
    Authorize a user and save the response details to a file.
    
    Args:
        email (str): User's email address
        name (str): User's full name
        roll_no (str): User's roll number
        access_code (str): Access code for authorization
        client_id (str): Client ID from registration
        client_secret (str): Client secret from registration
        filename (str): Name of the file to save the details
        
    Returns:
        dict: Complete authorization response
    """
    response = authorize_user(
        email=email,
        name=name,
        roll_no=roll_no,
        access_code=access_code,
        client_id=client_id,
        client_secret=client_secret
    )
    
    save_success = save_authorization_details(response, filename)
    
    response["details_saved"] = save_success
    response["saved_filename"] = filename if save_success else None
    
    return response

if __name__ == "__main__":
    print("=== Example 1: User Authorization ===")
    
    authorization_response = authorize_and_save(
        email="221401016@rajalakshmi.edu.in",
        name="Bhuwan B",
        roll_no="221401016",
        access_code="cWyaXW",
        client_id="fd63f6b4-9366-4eee-a196-3591f7150918",
        client_secret="QGNWZwrezEjDbZQg"
    )
    
    print("Authorization Response:")
    print(format_json_response(authorization_response))
    
    print("\n=== Example 2: APIClient with POST ===")
    client = APIClient(base_url="h`ttps://jsonplaceholder.typicode.com")
    
    post_data = {
        "title": "Test Post",
        "body": "This is a test post",
        "userId": 1
    }
    
    response = client.post("/posts", data=post_data)
    print(format_json_response(response))
