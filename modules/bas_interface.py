# modules/bas_interface.py

import abc
from typing import Dict, Any


class BASDriverInterface(abc.ABC):
    """Abstract Base Class defining the interface for a Browser Automation Studio (BAS) driver.

    This interface standardizes the methods needed for UI automation tasks,
    allowing different driver implementations (mock, real BAS, Selenium, etc.)
    to be used interchangeably.
    """

    @abc.abstractmethod
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate the browser to the specified URL.

        Args:
            url: The target URL.

        Returns:
            A dictionary indicating success status and potentially other details.
            Example: {"success": True, "url": url}
        """
        pass

    @abc.abstractmethod
    async def click(self, selector: str) -> Dict[str, Any]:
        """Click on a UI element identified by the selector.

        Args:
            selector: A string (e.g., CSS selector, XPath) identifying the element.

        Returns:
            A dictionary indicating success status.
            Example: {"success": True, "selector": selector}
        """
        pass

    @abc.abstractmethod
    async def input_text(
        self, selector: str, text: str, clear_first: bool = True
    ) -> Dict[str, Any]:
        """Input text into an element identified by the selector.

        Args:
            selector: A string identifying the input element.
            text: The text to input.
            clear_first: Whether to clear the field before inputting text.

        Returns:
            A dictionary indicating success status.
            Example: {"success": True, "selector": selector, "text_length": len(text)}
        """
        pass

    @abc.abstractmethod
    async def select_option(self, selector: str, value: str) -> Dict[str, Any]:
        """Select an option in a dropdown/select element.

        Args:
            selector: A string identifying the select element.
            value: The value or text of the option to select.

        Returns:
            A dictionary indicating success status.
            Example: {"success": True, "selector": selector, "value": value}
        """
        pass

    @abc.abstractmethod
    async def get_element_text(self, selector: str) -> str:
        """Retrieve the text content of an element.

        Args:
            selector: A string identifying the element.

        Returns:
            The text content of the element.

        Raises:
            ElementNotFoundError: If the element cannot be found.
            # Other driver-specific exceptions
        """
        pass

    @abc.abstractmethod
    async def take_screenshot(self, filename: str) -> Dict[str, Any]:
        """Take a screenshot of the current browser view and save it.

        Args:
            filename: The absolute path where the screenshot should be saved.

        Returns:
            A dictionary indicating success status and the filepath.
            Example: {"success": True, "filepath": filename}
        """
        pass

    # Optional: Add methods for login, waiting for elements, executing JS, etc.
    # async def login(self, credentials: Dict[str, str]) -> Dict[str, Any]:
    #     pass
    #
    # async def wait_for_element(self, selector: str, timeout: int = 30) -> Dict[str, Any]:
    #     pass
