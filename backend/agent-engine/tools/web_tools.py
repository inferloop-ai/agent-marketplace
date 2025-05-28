"""
Web Tools Module
===============

This module provides essential utilities for web operations, including:
- URL handling and validation
- HTTP requests
- Web scraping
- HTML parsing
- Content extraction
- Rate limiting
- Caching
- Async/await support
- Error handling

Features:
- Robust HTTP request handling
- HTML parsing and manipulation
- Content extraction utilities
- Rate limiting support
- Response caching
- URL validation
- Async operations
- Error handling and logging
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Generator
from urllib.parse import urlparse, urljoin, urlsplit
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class WebError(Exception):
    """Custom exception for web-related errors."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

class WebTools:
    """Class containing various web utility functions."""

    def __init__(
        self,
        cache_ttl: int = 300,  # 5 minutes
        cache_maxsize: int = 1000,
        max_retries: int = 3,
        timeout: int = 30,
        user_agent: str = "Mozilla/5.0"
    ):
        """Initialize web tools with configuration.

        Args:
            cache_ttl (int): Cache time-to-live in seconds
            cache_maxsize (int): Maximum size of cache
            max_retries (int): Maximum number of retry attempts
            timeout (int): Request timeout in seconds
            user_agent (str): User agent string
        """
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self.max_retries = max_retries
        self.timeout = timeout
        self.user_agent = user_agent
        self._session = None

    def _get_session(self) -> requests.Session:
        """Get or create a requests session with retry configuration.

        Returns:
            requests.Session: Configured session
        """
        if self._session is None:
            session = requests.Session()
            retry_strategy = Retry(
                total=self.max_retries,
                status_forcelist=[429, 500, 502, 503, 504],
                backoff_factor=1
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self._session = session
        return self._session

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate a URL format.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize a URL by removing fragments and query parameters.

        Args:
            url (str): URL to normalize

        Returns:
            str: Normalized URL
        """
        parts = urlsplit(url)
        return urlunsplit((
            parts.scheme,
            parts.netloc,
            parts.path,
            '',  # Empty query
            ''   # Empty fragment
        ))

    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from a URL.

        Args:
            url (str): URL to extract domain from

        Returns:
            str: Domain name
        """
        parsed = urlparse(url)
        return parsed.netloc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=(lambda e: isinstance(e, (requests.exceptions.RequestException, WebError)))
    )
    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cache: bool = True
    ) -> requests.Response:
        """Make an HTTP GET request with retry mechanism.

        Args:
            url (str): URL to request
            params (dict, optional): Query parameters
            headers (dict, optional): Request headers
            cache (bool): Whether to use caching

        Returns:
            requests.Response: HTTP response

        Raises:
            WebError: If request fails
        """
        if cache:
            cache_key = f"get_{url}_{params}_{headers}"
            if cache_key in self.cache:
                return self.cache[cache_key]

        try:
            headers = headers or {}
            headers['User-Agent'] = self.user_agent
            
            response = self._get_session().get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if cache:
                self.cache[cache_key] = response
            
            return response
        except requests.exceptions.RequestException as e:
            raise WebError(f"HTTP request failed: {e}", e)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=(lambda e: isinstance(e, (requests.exceptions.RequestException, WebError)))
    )
    async def async_get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """Make an asynchronous HTTP GET request.

        Args:
            url (str): URL to request
            params (dict, optional): Query parameters
            headers (dict, optional): Request headers

        Returns:
            Any: Response data

        Raises:
            WebError: If request fails
        """
        try:
            headers = headers or {}
            headers['User-Agent'] = self.user_agent
            
            async with ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            raise WebError(f"Async request failed: {e}", e)

    def parse_html(
        self,
        html: str,
        parser: str = 'html.parser'
    ) -> BeautifulSoup:
        """Parse HTML content.

        Args:
            html (str): HTML content
            parser (str): HTML parser to use

        Returns:
            BeautifulSoup: Parsed HTML
        """
        try:
            return BeautifulSoup(html, parser)
        except Exception as e:
            raise WebError(f"Error parsing HTML: {e}", e)

    def extract_text(
        self,
        html: str,
        exclude_tags: Optional[List[str]] = None
    ) -> str:
        """Extract text from HTML content.

        Args:
            html (str): HTML content
            exclude_tags (list, optional): Tags to exclude

        Returns:
            str: Extracted text
        """
        try:
            soup = self.parse_html(html)
            if exclude_tags:
                for tag in exclude_tags:
                    for element in soup.find_all(tag):
                        element.decompose()
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            raise WebError(f"Error extracting text: {e}", e)

    def extract_links(
        self,
        html: str,
        base_url: str,
        filter_domain: bool = True
    ) -> List[str]:
        """Extract links from HTML content.

        Args:
            html (str): HTML content
            base_url (str): Base URL for relative links
            filter_domain (bool): Whether to filter by domain

        Returns:
            list: List of extracted links
        """
        try:
            soup = self.parse_html(html)
            domain = self.extract_domain(base_url)
            links = []

            for a in soup.find_all('a', href=True):
                href = a['href']
                if not href:
                    continue

                # Handle relative URLs
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)

                # Filter by domain if requested
                if filter_domain and domain != self.extract_domain(href):
                    continue

                links.append(href)

            return links
        except Exception as e:
            raise WebError(f"Error extracting links: {e}", e)

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

    def cache_response(
        self,
        func: Callable
    ) -> Callable:
        """Decorator to cache web responses.

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

    def handle_web_error(
        self,
        error: Exception,
        default_value: Any = None
    ) -> Any:
        """Handle web-related errors gracefully.

        Args:
            error (Exception): Caught exception
            default_value (Any): Value to return on error

        Returns:
            Any: Default value or re-raises error
        """
        logger.error(f"Web Error: {str(error)}")
        if isinstance(error, WebError):
            if error.original_error and isinstance(error.original_error, requests.exceptions.Timeout):
                logger.warning("Request timeout occurred")
            elif error.original_error and isinstance(error.original_error, requests.exceptions.ConnectionError):
                logger.warning("Connection error occurred")
        return default_value

# Example usage:
if __name__ == "__main__":
    # Initialize web tools
    wt = WebTools(
        cache_ttl=300,
        max_retries=3,
        timeout=30
    )

    # Example rate-limited function
    @wt.rate_limit(calls=5, period=1.0)
    def fetch_data(url: str) -> Dict:
        response = wt.get(url)
        return response.json()

    # Example cached function
    @wt.cache_response
    def get_user_data(user_id: str) -> Dict:
        return wt.get(f'https://api.example.com/users/{user_id}').json()

    # Example async usage
    async def fetch_async_data():
        data = await wt.async_get('https://api.example.com/data')
        return data

    # Example HTML parsing
    html = wt.get('https://example.com').text
    soup = wt.parse_html(html)
    text = wt.extract_text(html, exclude_tags=['script', 'style'])
    links = wt.extract_links(html, 'https://example.com')

    # Example error handling
    try:
        response = wt.get('https://invalid-url')
    except WebError as e:
        response = wt.handle_web_error(e, default_value={})