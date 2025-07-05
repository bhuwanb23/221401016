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
        logging.FileHandler('api_requests.log'),
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
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
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
        # Construct full URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        
        # Prepare request data
        request_data = {
            'url': url,
            'method': method.upper(),
            'params': params or {},
            'headers': headers or {},
            'timeout': self.timeout,
            **kwargs
        }
        
        # Add JSON data if provided
        if data is not None:
            request_data['json'] = data
        
        # Log the request
        logger.info(f"Making {method.upper()} request to: {url}")
        if data:
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            # Make the request
            response = self.session.request(**request_data)
            
            # Log response status
            logger.info(f"Response status: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text}
            
            # Create result dictionary
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
            
            # Log success or error
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

# Example usage and utility functions
def make_api_request(
    url: str, 
    method: str = "GET", 
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

def register_user(
    email: str,
    name: str,
    mobile: str,
    github_username: str,
    roll_no: str,
    access_code: str
) -> Dict[str, Any]:
    """
    Register a user with the evaluation service.
    
    Args:
        email (str): User's email address
        name (str): User's full name
        mobile (str): User's mobile number (sent as "mobileNo")
        github_username (str): User's GitHub username (sent as "githubUsername")
        roll_no (str): User's roll number (sent as "rollNo")
        access_code (str): Access code for registration (sent as "accessCode")
        
    Returns:
        dict: Registration response with user details
    """
    # Registration URL
    url = "http://20.244.56.144/evaluation-service/register"
    
    # Prepare registration data
    registration_data = {
        "email": email,
        "name": name,
        "mobileNo": mobile,
        "githubUsername": github_username,
        "rollNo": roll_no,
        "accessCode": access_code
    }
    
    # Make the registration request
    response = make_api_request(
        url=url,
        method="POST",
        data=registration_data
    )
    
    return response

def save_registration_details(response: Dict[str, Any], filename: str = "registration_details.json") -> bool:
    """
    Save registration response details to a file.
    
    Args:
        response (dict): The API response from registration
        filename (str): Name of the file to save the details
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Extract the important details from response
        if response.get("success") and response.get("response_data"):
            # Get the actual response data from the API
            api_response = response["response_data"]
            
            # Create a clean details object with only the required fields
            details_to_save = {
                "email": api_response.get("email"),
                "name": api_response.get("name"),
                "roll_no": api_response.get("roll_no"),
                "access_code": api_response.get("access_code"),
                "client_id": api_response.get("client_id"),
                "client_secret": api_response.get("client_secret"),
                "registration_timestamp": response.get("timestamp"),
                "status": "success" if response.get("success") else "failed"
            }
        else:
            # If registration failed, save error details
            details_to_save = {
                "error": response.get("error", "Unknown error"),
                "status_code": response.get("status_code"),
                "registration_timestamp": response.get("timestamp"),
                "status": "failed"
            }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(details_to_save, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Registration details saved to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save registration details: {e}")
        return False

def register_and_save(
    email: str,
    name: str,
    mobile: str,
    github_username: str,
    roll_no: str,
    access_code: str,
    filename: str = "registration_details.json"
) -> Dict[str, Any]:
    """
    Register a user and save the response details to a file.
    
    Args:
        email (str): User's email address
        name (str): User's full name
        mobile (str): User's mobile number
        github_username (str): User's GitHub username
        roll_no (str): User's roll number
        access_code (str): Access code for registration
        filename (str): Name of the file to save the details
        
    Returns:
        dict: Complete registration response
    """
    # Make the registration request
    response = register_user(
        email=email,
        name=name,
        mobile=mobile,
        github_username=github_username,
        roll_no=roll_no,
        access_code=access_code
    )
    
    # Save the details to file
    save_success = save_registration_details(response, filename)
    
    # Add save status to response
    response["details_saved"] = save_success
    response["saved_filename"] = filename if save_success else None
    
    return response

# Example usage
if __name__ == "__main__":
    # Example 1: Registration with the evaluation service
    print("=== Example 1: User Registration ===")
    
    # Sample registration data
    # Note: Replace with your actual details for real registration
    registration_response = register_and_save(
        email="221401016@rajalakshmi.edu.in",
        name="Bhuwan B",
        mobile="6382403822",
        github_username="bhuwanb23",
        roll_no="221401016",
        access_code="cWyaXW"
    )
    
    print("Registration Response:")
    print(format_json_response(registration_response))
    
    # Example 2: Using the APIClient class for POST requests
    print("\n=== Example 2: APIClient with POST ===")
    client = APIClient(base_url="https://jsonplaceholder.typicode.com")
    
    post_data = {
        "title": "Test Post",
        "body": "This is a test post",
        "userId": 1
    }
    
    response = client.post("/posts", data=post_data)
    print(format_json_response(response))
