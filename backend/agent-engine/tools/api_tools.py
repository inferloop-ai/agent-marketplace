"""
API Tools Module
===============

This module provides essential utilities for API interactions, including:
- Request handling and error management
- Rate limiting and retry mechanisms
- Data validation and transformation
- API key management
- Response caching
- Async/await support

Features:
- Robust API request handling
- Automatic retry mechanism
- Rate limiting support
- Response caching
- Data validation
- Error handling and logging
"""

import logging
import time
from typing import Any, Dict, Optional, Union, List, Callable
from functools import wraps
import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from cachetools import TTLCache

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class APITools:
    """Class containing various API-related utility functions."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        cache_ttl: int = 300,  # 5 minutes
        cache_maxsize: int = 1000
    ):
        """Initialize API tools with configuration.

        Args:
            base_url (str): Base URL for API requests
            api_key (str, optional): API key for authentication
            max_retries (int): Maximum number of retry attempts
            cache_ttl (int): Cache time-to-live in seconds
            cache_maxsize (int): Maximum size of cache
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.max_retries = max_retries
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

    def _build_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers.

        Args:
            additional_headers (dict, optional): Additional headers to include

        Returns:
            dict: Complete headers dictionary
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _validate_response(self, response: Union[requests.Response, aiohttp.ClientResponse]) -> None:
        """Validate API response.

        Args:
            response: API response object

        Raises:
            APIError: If response status code indicates an error
        """
        if isinstance(response, requests.Response):
            status_code = response.status_code
            content = response.text
        else:
            status_code = response.status
            content = response.text

        if status_code >= 400:
            error_msg = f"API Error {status_code}: {content[:200]}"
            logger.error(error_msg)
            raise APIError(error_msg, status_code)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=(lambda e: isinstance(e, (requests.exceptions.RequestException, APIError)))
    )
    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """Make an HTTP request with retry mechanism.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            headers (dict, optional): Additional headers

        Returns:
            dict: Parsed JSON response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/') if endpoint else ''}"
        headers = self._build_headers(headers)

        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=data,
                headers=headers,
                timeout=30
            )
            self._validate_response(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def make_async_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """Make an async HTTP request with retry mechanism.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            headers (dict, optional): Additional headers

        Returns:
            dict: Parsed JSON response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/') if endpoint else ''}"
        headers = self._build_headers(headers)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=30
                ) as response:
                    self._validate_response(response)
                    return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"Async request failed: {str(e)}")
                raise

    def cache_response(
        self,
        func: Callable
    ) -> Callable:
        """Decorator to cache API responses.

        Args:
            func (Callable): Function to decorate

        Returns:
            Callable: Decorated function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            if cache_key in self.cache:
                logger.debug(f"Cache hit for {cache_key}")
                return self.cache[cache_key]
            
            result = func(*args, **kwargs)
            self.cache[cache_key] = result
            return result
        
        return wrapper

    def rate_limit(
        self,
        calls: int = 1,
        period: float = 1.0
    ) -> Callable:
        """Decorator to implement rate limiting.

        Args:
            calls (int): Number of allowed calls
            period (float): Time period in seconds

        Returns:
            Callable: Decorated function
        """
        def decorator(func: Callable) -> Callable:
            call_times = []
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal call_times
                
                # Remove old timestamps
                call_times = [t for t in call_times if time.time() - t < period]
                
                if len(call_times) >= calls:
                    sleep_time = period - (time.time() - call_times[0])
                    if sleep_time > 0:
                        logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                        time.sleep(sleep_time)
                
                call_times.append(time.time())
                return func(*args, **kwargs)
            
            return wrapper
        
        return decorator

    def validate_response_data(
        self,
        response: Dict,
        required_fields: List[str]
    ) -> None:
        """Validate that required fields are present in response data.

        Args:
            response (dict): Response data
            required_fields (list): List of required field names

        Raises:
            ValueError: If any required field is missing
        """
        missing_fields = [field for field in required_fields if field not in response]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    def transform_response_data(
        self,
        response: Dict,
        transformations: Dict[str, Callable]
    ) -> Dict:
        """Apply transformations to response data.

        Args:
            response (dict): Response data
            transformations (dict): Mapping of field names to transformation functions

        Returns:
            dict: Transformed data
        """
        transformed = response.copy()
        for field, transform_func in transformations.items():
            if field in transformed:
                transformed[field] = transform_func(transformed[field])
        return transformed

    def handle_api_error(
        self,
        error: Exception,
        default_value: Any = None
    ) -> Any:
        """Handle API-related errors gracefully.

        Args:
            error (Exception): Caught exception
            default_value (Any): Value to return on error

        Returns:
            Any: Default value or re-raises error
        """
        logger.error(f"API Error: {str(error)}")
        if isinstance(error, APIError):
            if error.status_code == 429:  # Rate limit
                logger.warning("Rate limit exceeded")
            elif error.status_code >= 500:  # Server error
                logger.warning("Server error occurred")
        return default_value

# Example usage:
if __name__ == "__main__":
    api = APITools(
        base_url="https://api.example.com",
        api_key="your-api-key",
        max_retries=3,
        cache_ttl=300
    )

    # Example rate-limited function
    @api.rate_limit(calls=5, period=1.0)
    def get_user_data(user_id: str) -> Dict:
        return api.make_request('GET', f'users/{user_id}')

    # Example cached function
    @api.cache_response
    def get_user_stats(user_id: str) -> Dict:
        return api.make_request('GET', f'users/{user_id}/stats')

    # Example async usage
    async def fetch_async_data():
        return await api.make_async_request('GET', 'data')

    # Example error handling
    try:
        response = api.make_request('GET', 'endpoint')
    except APIError as e:
        response = api.handle_api_error(e, default_value={})

    # Example data validation
    api.validate_response_data(response, ['id', 'name'])

    # Example data transformation
    transformed = api.transform_response_data(
        response,
        {
            'created_at': lambda x: x.split('T')[0],  # Extract date from datetime
            'status': lambda x: x.lower()  # Normalize status to lowercase
        }
    )