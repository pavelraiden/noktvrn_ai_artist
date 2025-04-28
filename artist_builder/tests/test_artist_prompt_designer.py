"""
Test cases for the ArtistPromptDesigner class.

This module contains test cases to validate the functionality of the
artist_prompt_designer.py module.
"""

import sys
import os
import unittest
import json
from pathlib import Path

# Add the parent directory to the path to import the module
sys.path.append(str(Path(__file__).parent.parent))
from prompts.artist_prompt_designer import ArtistPromptDesigner


class TestArtistPromptDesigner(unittest.TestCase):
    """Test cases for the ArtistPromptDesigner class."""

    def setUp(self):
        """Set up the test environment."""
        self.designer = ArtistPromptDesigner()

        # Test parameters for various scenarios
        self.complete_params = {
            "genre": "Dark Trap",
            "vibe": "Mysterious, Cold",
            "lifestyle": "Urban night life",
            "appearance": "Always wears a black hood and mask",
            "voice": "Deep and raspy",
        }

        self.minimal_params = {"genre": "Phonk", "vibe": "Aggressive"}

        self.alternative_params = {
            "genre": "Alternative",
            "vibe": "Ethereal",
            "lifestyle": "Nomadic",
            "appearance": "Colorful, eccentric clothing",
            "voice": "Soft and whispery",
        }

        self.empty_params = {}

    def test_generate_prompt_complete(self):
        """Test prompt generation with complete parameters."""
        prompt = self.designer.generate_prompt(self.complete_params)

        # Check that the prompt is not empty
        self.assertTrue(prompt)

        # Check that all parameters are included in the prompt
        self.assertIn("Dark Trap", prompt)

        # Check for vibe - either "Mysterious" or "Cold" should be present
        self.assertTrue(
            "Mysterious" in prompt or "Cold" in prompt,
            f"Neither 'Mysterious' nor 'Cold' found in: {prompt}",
        )

        self.assertIn("night life", prompt.lower())
        self.assertIn("hood and mask", prompt.lower())
        self.assertIn("raspy", prompt.lower())

        print("\nComplete Parameters Prompt:")
        print(prompt)

    def test_generate_prompt_minimal(self):
        """Test prompt generation with minimal parameters."""
        prompt = self.designer.generate_prompt(self.minimal_params)

        # Check that the prompt is not empty
        self.assertTrue(prompt)

        # Check that provided parameters are included
        self.assertIn("Phonk", prompt)
        self.assertIn("Aggressive", prompt)

        # Check that missing parameters don't cause issues
        self.assertNotIn("None", prompt)

        print("\nMinimal Parameters Prompt:")
        print(prompt)

    def test_generate_prompt_alternative(self):
        """Test prompt generation with alternative genre parameters."""
        prompt = self.designer.generate_prompt(self.alternative_params)

        # Check that the prompt is not empty
        self.assertTrue(prompt)

        # Check that all parameters are included in the prompt
        self.assertIn("Alternative", prompt)
        self.assertIn("Ethereal", prompt)
        self.assertIn("Nomadic", prompt)
        self.assertIn("eccentric clothing", prompt.lower())
        self.assertIn("whispery", prompt.lower())

        print("\nAlternative Parameters Prompt:")
        print(prompt)

    def test_generate_prompt_empty(self):
        """Test prompt generation with empty parameters."""
        prompt = self.designer.generate_prompt(self.empty_params)

        # Check that the prompt is not empty even with empty parameters
        self.assertTrue(prompt)

        # Check that it doesn't contain formatting placeholders
        self.assertNotIn("{genre}", prompt)
        self.assertNotIn("{vibe}", prompt)

        print("\nEmpty Parameters Prompt:")
        print(prompt)

    def test_generate_prompt_for_review(self):
        """Test generating a prompt package for LLM review."""
        review_package = self.designer.generate_prompt_for_review(self.complete_params)

        # Check that the review package has the expected structure
        self.assertIn("prompt_type", review_package)
        self.assertIn("parameters", review_package)
        self.assertIn("generated_prompt", review_package)
        self.assertIn("review_instructions", review_package)
        self.assertIn("version", review_package)

        # Check that the parameters are correctly included
        self.assertEqual(review_package["parameters"], self.complete_params)

        # Check that the generated prompt is not empty
        self.assertTrue(review_package["generated_prompt"])

        print("\nReview Package:")
        print(json.dumps(review_package, indent=2))

    def test_multiple_generations(self):
        """Test that multiple generations produce different prompts."""
        prompts = []
        for _ in range(5):
            prompts.append(self.designer.generate_prompt(self.complete_params))

        # Check that at least some of the prompts are different
        unique_prompts = set(prompts)
        self.assertGreater(
            len(unique_prompts),
            1,
            "Multiple generations should produce at least some different prompts",
        )

        print(f"\nGenerated {len(unique_prompts)} unique prompts out of 5 generations")


if __name__ == "__main__":
    unittest.main()
