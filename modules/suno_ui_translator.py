# modules/suno/suno_ui_translator.py

import logging
from typing import Dict, Any, List

# Placeholder for the actual browser automation driver (e.g., Selenium, Playwright, or a custom BAS interface)
# This would handle the low-level browser interactions.
class MockBASDriver:
    def __init__(self):
        self.current_url = ""
        logger.info("MockBASDriver initialized.")

    async def navigate(self, url: str):
        logger.info(f"[MockBASDriver] Navigating to: {url}")
        self.current_url = url
        await asyncio.sleep(1) # Simulate page load
        return {"success": True, "url": url}

    async def click(self, selector: str):
        logger.info(f"[MockBASDriver] Clicking element: {selector}")
        await asyncio.sleep(0.5) # Simulate click
        return {"success": True, "selector": selector}

    async def input_text(self, selector: str, text: str, clear_first: bool = True):
        if clear_first:
            logger.info(f"[MockBASDriver] Clearing input: {selector}")
            await asyncio.sleep(0.2)
        logger.info(f"[MockBASDriver] Inputting text into {selector}: 	'{text[:30]}...	'" )
        await asyncio.sleep(0.5) # Simulate typing
        return {"success": True, "selector": selector, "text": text}

    async def select_option(self, selector: str, value: str):
        logger.info(f"[MockBASDriver] Selecting option 	'{value}	' in dropdown: {selector}")
        await asyncio.sleep(0.5) # Simulate selection
        return {"success": True, "selector": selector, "value": value}

    async def get_element_text(self, selector: str) -> str:
        logger.info(f"[MockBASDriver] Getting text from: {selector}")
        await asyncio.sleep(0.3)
        # Simulate finding text - replace with actual logic
        if selector == "#credits_remaining":
            return "9750 Credits"
        elif selector == ".song-list-item a[href*='/song/']": # Match selector used below
            # Simulate finding the link of the *latest* generated song
            return "https://suno.com/song/mock-generated-song-id-12345"
        return f"Text from {selector}"

    async def take_screenshot(self, filename: str):
        logger.info(f"[MockBASDriver] Taking screenshot: {filename}")
        # Simulate saving a file
        # In a real scenario, ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("Mock screenshot data")
        await asyncio.sleep(1)
        return {"success": True, "filepath": filename}

# --- End of Mock Driver ---

import asyncio # Import added for async functions in MockBASDriver
import os # Added for take_screenshot

logger = logging.getLogger(__name__)

class SunoUITranslatorError(Exception):
    """Custom exception for UI Translator errors."""
    pass

class SunoUITranslator:
    """Translates high-level commands into specific Suno UI actions using BAS.

    Relies on a mapping defined by UI analysis (screenshots, specs).
    """

    def __init__(self, bas_driver: Any):
        """Initializes the UI Translator.

        Args:
            bas_driver: An instance of the browser automation driver.
        """
        self.driver = bas_driver
        # Define UI element selectors based on analysis of screenshots/specs
        # This mapping is crucial and needs to be accurate.
        self.selectors = {
            "login_button": "//button[contains(text(), 'Sign in')]", # Example XPath
            "create_page_nav": "a[href='/create/']", # Example CSS selector
            "lyrics_input": "textarea[placeholder*='your own lyrics']",
            "style_input": "textarea[placeholder*='Enter style description']",
            "by_line_toggle": "button[aria-label='By Line']", # Needs verification
            "full_song_toggle": "button[aria-label='Full Song']", # Needs verification
            "model_dropdown": "button[aria-haspopup='listbox']", # Example, needs verification
            "model_option_v4.5": "li[role='option']:contains('v4.5')", # Example, needs verification
            "model_option_remi": "li[role='option']:contains('ReMi')", # Example, needs verification
            "model_option_classic": "li[role='option']:contains('Classic')", # Example, needs verification
            "persona_add_button": "button[aria-label='Add Persona']", # Needs verification
            "create_persona_button": "button:contains('Create New Persona')", # Needs verification
            "workspace_dropdown": "div[role='combobox']", # Example, needs verification
            "workspace_option": "li[role='option']:contains('{workspace_name}')", # Needs verification
            "song_title_input": "input[placeholder='Enter song title']",
            "create_button": "button:contains('Create')",
            "generated_song_link": ".song-list-item a[href*='/song/']", # Example, needs refinement - target latest song
            "credits_display": "#credits_remaining", # Example, needs verification
            # Add more selectors based on screenshots and spec
        }
        logger.info("Suno UI Translator initialized.")

    async def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a single UI action using the BAS driver.

        Args:
            action: A dictionary describing the action (e.g.,
                    {'action': 'click', 'target': 'login_button'},
                    {'action': 'input', 'target': 'lyrics_input', 'value': 'Hello'},
                    {'action': 'select', 'target': 'model_dropdown', 'value': 'v4.5'},
                    {'action': 'navigate', 'url': 'https://suno.com/'},
                    {'action': 'get_text', 'target': 'credits_display'},
                    {'action': 'screenshot', 'filename': 'step1.png'})

        Returns:
            A dictionary containing the result of the action.
        """
        action_type = action.get("action")
        target_key = action.get("target") # Logical name from self.selectors
        selector = self.selectors.get(target_key) if target_key else None
        value = action.get("value")
        url = action.get("url")
        filename = action.get("filename")

        logger.debug(f"Executing action: {action_type}, Target: {target_key}, Selector: {selector}, Value: {value}")

        try:
            if action_type == "navigate":
                if not url:
                    raise SunoUITranslatorError(f"Missing 'url' for navigate action.")
                return await self.driver.navigate(url)
            elif action_type == "click":
                if not selector:
                    raise SunoUITranslatorError(f"Missing or invalid 'target' key: {target_key}")
                return await self.driver.click(selector)
            elif action_type == "input":
                if not selector:
                    raise SunoUITranslatorError(f"Missing or invalid 'target' key: {target_key}")
                if value is None:
                    raise SunoUITranslatorError(f"Missing 'value' for input action.")
                return await self.driver.input_text(selector, value)
            elif action_type == "select": # Assuming dropdown selection
                if not selector:
                    raise SunoUITranslatorError(f"Missing or invalid 'target' key: {target_key}")
                if value is None:
                    raise SunoUITranslatorError(f"Missing 'value' for select action.")
                # This might involve multiple steps: click dropdown, then click option
                # Simplified here - real implementation depends on BAS driver capabilities
                # Example: Find the specific option selector based on value
                option_selector_key = f"model_option_{value}" # Needs robust mapping
                option_selector = self.selectors.get(option_selector_key)
                if not option_selector:
                     raise SunoUITranslatorError(f"Invalid 'value' for select action: {value}")
                await self.driver.click(selector) # Open dropdown
                await asyncio.sleep(0.5) # Wait for options
                return await self.driver.click(option_selector) # Click the option
            elif action_type == "get_text":
                if not selector:
                    raise SunoUITranslatorError(f"Missing or invalid 'target' key: {target_key}")
                text_content = await self.driver.get_element_text(selector)
                return {"success": True, "text": text_content}
            elif action_type == "screenshot":
                if not filename:
                    raise SunoUITranslatorError(f"Missing 'filename' for screenshot action.")
                return await self.driver.take_screenshot(filename)
            else:
                raise SunoUITranslatorError(f"Unsupported action type: {action_type}")

        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            # Don't raise here, return failure status for feedback loop
            return {"success": False, "error": str(e), "action": action}

    def translate_prompt_to_actions(self, prompt: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Translates a high-level generation prompt into a sequence of UI actions.

        Args:
            prompt: The structured generation prompt.

        Returns:
            A list of action dictionaries for execute_action.
        """
        actions = []
        actions.append({"action": "navigate", "url": "https://suno.com/create/"})

        # --- Model Selection ---
        model = prompt.get("model", "v4.5") # Default to v4.5
        # Use specific model selector key
        model_target_key = f"model_option_{model}"
        if model_target_key not in self.selectors:
            logger.warning(f"Model '{model}' not found in selectors, defaulting to v4.5")
            model = "v4.5"
            model_target_key = "model_option_v4.5"
        
        actions.append({"action": "click", "target": "model_dropdown"}) # Open dropdown
        actions.append({"action": "click", "target": model_target_key}) # Select model
        # TODO: Add check/fallback if model is unavailable (needs driver support)

        # --- Lyrics Input ---
        lyrics = prompt.get("lyrics")
        lyrics_mode = prompt.get("lyrics_mode", "Full Song") # Default
        if lyrics:
            if lyrics_mode == "By Line":
                actions.append({"action": "click", "target": "by_line_toggle"})
                # TODO: Implement line-by-line input logic if needed
                # This might involve multiple input actions based on lyric structure
                actions.append({"action": "input", "target": "lyrics_input", "value": lyrics})
            else: # Full Song
                actions.append({"action": "click", "target": "full_song_toggle"})
                actions.append({"action": "input", "target": "lyrics_input", "value": lyrics})
        else:
            # Handle instrumental? Toggle might be needed.
            pass

        # --- Style Description ---
        style = prompt.get("style")
        if style:
            actions.append({"action": "input", "target": "style_input", "value": style})

        # --- Persona ---
        persona = prompt.get("persona")
        if persona:
            actions.append({"action": "click", "target": "persona_add_button"})
            # TODO: Logic to select existing or create new persona
            # actions.append({'action': 'click', 'target': 'create_persona_button'})
            # actions.append({'action': 'input', 'target': 'persona_name_input', 'value': persona})
            logger.warning("Persona selection/creation logic not fully implemented.")

        # --- Workspace ---
        workspace = prompt.get("workspace")
        if workspace:
            actions.append({"action": "click", "target": "workspace_dropdown"})
            # TODO: Logic to select workspace
            logger.warning("Workspace selection logic not fully implemented.")

        # --- Song Title ---
        title = prompt.get("title")
        if title:
            actions.append({"action": "input", "target": "song_title_input", "value": title})

        # --- Create ---
        actions.append({"action": "click", "target": "create_button"})

        # --- Wait / Check for result (handled by orchestrator/feedback loop) ---

        logger.info(f"Translated prompt into {len(actions)} actions.")
        return actions

    async def extract_final_output(self, last_action_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts the final result (e.g., song URL, ID) after successful execution.

        Args:
            last_action_results: Results from the final successful sequence of actions.

        Returns:
            Dictionary containing the extracted output metadata.
            Example: {
                "status": "completed" | "extraction_failed",
                "suno_song_url": "https://suno.com/song/...",
                "suno_song_id": "...",
                "error": "..." # if extraction failed
            }
        """
        logger.info("Attempting to extract final output from Suno UI...")
        output = {"status": "extraction_failed"}
        try:
            # --- Refined Extraction Logic --- 
            # This needs robust logic to find the *correct* generated song link.
            # It might involve waiting for elements, checking timestamps, or matching titles if possible.
            # Using the mock driver's simplified get_element_text for now.
            song_link_selector = self.selectors["generated_song_link"]
            song_url = await self.driver.get_element_text(song_link_selector)

            if song_url and "suno.com/song/" in song_url:
                output["suno_song_url"] = song_url
                # Extract ID from URL (example)
                try:
                    output["suno_song_id"] = song_url.split("/song/")[-1]
                except Exception:
                    logger.warning(f"Could not extract Suno song ID from URL: {song_url}")
                    output["suno_song_id"] = None
                
                output["status"] = "completed"
                logger.info(f"Extracted final output: URL={output['suno_song_url']}, ID={output['suno_song_id']}")
            else:
                logger.error(f"Could not find or parse valid song URL using selector: {song_link_selector}")
                output["error"] = "Failed to find or parse generated song URL."

        except Exception as e:
            logger.error(f"Failed to extract final output due to error: {e}")
            output["error"] = str(e)
        
        return output

# Example usage (for testing purposes)
async def main():
    logging.basicConfig(level=logging.INFO)
    mock_driver = MockBASDriver()
    translator = SunoUITranslator(mock_driver)

    test_prompt = {
        "lyrics": "Verse 1\nSunshine and code\nChorus\nCompile it all",
        "style": "Lo-fi hip hop, chill beats",
        "model": "v4.5",
        "title": "Coding Chill"
    }

    actions = translator.translate_prompt_to_actions(test_prompt)
    print("--- Generated Actions ---")
    for act in actions:
        print(act)

    print("\n--- Executing Actions ---")
    results = []
    for act in actions:
        result = await translator.execute_action(act)
        print(f"Result: {result}")
        if not result.get("success"):
            print("Action failed, stopping execution.")
            break
        results.append(result)
    else:
        print("\n--- Extracting Final Output ---")
        final_output = await translator.extract_final_output(results)
        print(f"Final Output: {json.dumps(final_output, indent=2)}")

if __name__ == "__main__":
    import json # Added for example usage
    asyncio.run(main())

