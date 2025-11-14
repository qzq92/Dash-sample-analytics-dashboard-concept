"""
OneMap API Authentication Module
Handles token acquisition and caching for OneMap API requests.
Reference: https://www.onemap.gov.sg/apidocs/authentication
"""
import requests
import os
import time
from typing import Optional
from dotenv import load_dotenv
load_dotenv(override=True)

# Token cache
_token_cache: Optional[str] = None
_token_expiry: float = 0.0
_token_lock = False  # Simple flag to prevent concurrent token requests
_original_api_key: Optional[str] = None  # Store original API key for token refresh


def get_onemap_token() -> Optional[str]:
    """
    Get a valid OneMap API access token, refreshing if necessary.
    
    This function caches the token and automatically refreshes it when it expires.
    The token is cached until expiry to minimize API calls.
    
    Returns:
        Access token string, or None if token acquisition fails
    """
    global _token_cache, _token_expiry, _token_lock
    
    # Check if we have a valid cached token (with 60 second buffer before expiry)
    current_time = time.time()
    if _token_cache and current_time < (_token_expiry - 60):
        print("Received token_cache")
        return _token_cache
    
    # Prevent concurrent token requests
    if _token_lock:
        # Wait a bit and retry
        time.sleep(0.5)
        if _token_cache and current_time < (_token_expiry - 60):
            print("Received token_cache from concurrent request")
            return _token_cache
        return None
    
    _token_lock = True
    
    try:
        global _original_api_key
        
        # Get email and password from environment variables
        email = os.getenv("ONEMAP_EMAIL")
        password = os.getenv("ONEMAP_EMAIL_PASSWORD")
        
        # Get API key from environment - check if it's already a token or the original API key
        env_value = os.getenv("ONEMAP_API_KEY")
        
        # If we don't have the original API key stored, assume ONEMAP_API_KEY is the API key
        # Otherwise, use the stored original API key
        api_key = _original_api_key if _original_api_key else env_value
        
        
        # Store the original API key if not already stored
        if not _original_api_key and api_key:
            _original_api_key = api_key
        
        # Build payload with email, password, and optionally API key
        payload = {}
        
        if email:
            payload['email'] = email
        
        if password:
            payload['password'] = password
        
        if api_key:
            payload['apikey'] = api_key
        
        # Check if we have at least email and password, or API key
        if not email or not password:
            if not api_key:
                print("Warning: ONEMAP_API_EMAIL, ONEMAP_API_PASSWORD, or ONEMAP_API_KEY not found in environment variables")
                return None
        
        # OneMap authentication endpoint
        token_url = "https://www.onemap.gov.sg/api/auth/post/getToken"
        
        # Request token using POST with email, password, and optionally API key
        print("Requesting token using POST with email, password, and optionally API key")
        response = requests.request(
            "POST",
            token_url,
            json=payload
        )
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Extract token and expiry information
            access_token = token_data.get('access_token')
            expiry_timestamp = token_data.get('expiry_timestamp')

            #print(f"Access token: {access_token}")
            #print(f"Expiry timestamp: {expiry_timestamp}")
            
            
            if access_token:
                # Cache the token and calculate expiry time in unix seconds
                _token_cache = access_token
                # Save the access token to OS environment variable (not .env file)
                # This sets it for the current process and all child processes
                os.environ["ONEMAP_API_KEY"] = access_token
                
                print("OneMap API token acquired successfully")
                print("Token saved to OS environment variable ONEMAP_API_KEY (not .env file).")
                return access_token
            
            print("Error: No access_token in OneMap API response")
            return None
        
        print(f"Error acquiring OneMap API token: status={response.status_code}, body={response.text[:200]}")
        return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error requesting OneMap API token: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_onemap_token: {e}")
        return None
    finally:
        _token_lock = False


def initialize_onemap_token() -> bool:
    """
    Initialize OneMap API token on application startup.
    
    This should be called when the application starts to pre-fetch the token.
    
    Returns:
        True if token was successfully acquired, False otherwise
    """
    token = get_onemap_token()
    return token is not None


def get_valid_token() -> Optional[str]:
    """
    Get a valid token, ensuring it's not expired.
    This is an alias for get_onemap_token() for clarity.
    
    Returns:
        Valid access token string, or None if unavailable
    """
    return get_onemap_token()


def clear_token_cache():
    """
    Clear the cached token (useful for testing or forced refresh).
    Note: We keep _original_api_key so we can still refresh tokens.
    """
    global _token_cache, _token_expiry
    _token_cache = None
    _token_expiry = 0.0

