import requests
import logging
import json

logger = logging.getLogger(__name__)

class ApiClientError(Exception):
    """Base exception for API client errors."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class BaseApiClient:
    """Base class for interacting with external APIs."""

    def __init__(self, base_url: str, api_key: str):
        """Initializes the BaseApiClient.

        Args:
            base_url: The base URL for the API.
            api_key: The API key for authentication.
        """
        if not base_url:
            raise ValueError("Base URL cannot be empty.")
        if not api_key:
            raise ValueError("API key cannot be empty.")
            
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        logger.info(f"{self.__class__.__name__} initialized for base URL: {self.base_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Makes an HTTP request to the API.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            endpoint: API endpoint path (relative to base_url).
            **kwargs: Additional arguments passed to requests.request.

        Returns:
            The requests.Response object.

        Raises:
            ApiClientError: If the request fails or returns an error status code.
        """
        # Fixed syntax error: Added missing closing parenthesis for lstrip
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.headers.copy()
        
        # Allow overriding headers per request if needed
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Redact sensitive info for logging
        log_headers = headers.copy()
        if "Authorization" in log_headers:
            log_headers["Authorization"] = "Bearer [REDACTED]"
            
        log_data = kwargs.get("json") or kwargs.get("data")
        if isinstance(log_data, dict):
             log_data_str = json.dumps(log_data) # Ensure dicts are logged as JSON strings
        elif isinstance(log_data, str):
             log_data_str = log_data
        else:
             log_data_str = "(Non-serializable data)"

        logger.debug(f"Making {method} request to {url}")
        logger.debug(f"Headers: {log_headers}")
        if log_data:
             logger.debug(f"Payload: {log_data_str}")

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            logger.debug(f"Response Status Code: {response.status_code}")
            # Log response body only if debugging is needed and content is not too large
            # logger.debug(f"Response Body: {response.text[:500]}...") 

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}", exc_info=True)
            raise ApiClientError(f"Request failed: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during the request: {e}", exc_info=True)
            raise ApiClientError(f"An unexpected error occurred: {e}") from e

    def _get(self, endpoint: str, params: dict | None = None, **kwargs) -> dict:
        """Performs a GET request.

        Args:
            endpoint: API endpoint path.
            params: Dictionary of URL parameters.
            **kwargs: Additional arguments for _request.

        Returns:
            The JSON response as a dictionary.
        """
        response = self._request("GET", endpoint, params=params, **kwargs)
        try:
            return response.json()
        except json.JSONDecodeError as e:
             logger.error(f"Failed to decode JSON response from GET {endpoint}: {response.text[:500]}...", exc_info=True)
             raise ApiClientError(f"Invalid JSON response: {e}") from e

    def _post(self, endpoint: str, json_data: dict | None = None, data: dict | None = None, **kwargs) -> dict:
        """Performs a POST request.

        Args:
            endpoint: API endpoint path.
            json_data: Dictionary to be sent as JSON payload.
            data: Dictionary to be sent as form data.
            **kwargs: Additional arguments for _request.

        Returns:
            The JSON response as a dictionary.
        """
        response = self._request("POST", endpoint, json=json_data, data=data, **kwargs)
        try:
            # Handle cases where POST might return empty body on success (e.g., 204 No Content)
            if response.status_code == 204:
                return {}
            return response.json()
        except json.JSONDecodeError as e:
             logger.error(f"Failed to decode JSON response from POST {endpoint}: {response.text[:500]}...", exc_info=True)
             raise ApiClientError(f"Invalid JSON response: {e}") from e


