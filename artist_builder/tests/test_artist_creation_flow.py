"""
Integration test for the Artist Creation System Phase 2.

This module tests the complete flow of the artist creation process,
from prompt generation to validation, feedback loop, and profile composition.
"""

import os
import sys
import unittest
import asyncio
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from artist_builder.prompts.artist_prompt_designer import ArtistPromptDesigner
from artist_builder.validators.prompt_validator import PromptValidator, ValidationResult
from artist_builder.validators.feedback_loop_checker import FeedbackLoopChecker, FeedbackLoopStatus
from artist_builder.composer.artist_profile_composer import ArtistProfileComposer
from llm_orchestrator.review_logger import ReviewLogger


class TestArtistCreationFlow(unittest.TestCase):
    """Test the complete artist creation flow."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create temporary directory for review logs
        self.temp_dir = "/tmp/test_artist_creation"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize components
        self.prompt_designer = ArtistPromptDesigner()
        self.prompt_validator = PromptValidator(
            min_length=50,
            confidence_threshold=0.7
        )
        self.feedback_loop_checker = FeedbackLoopChecker(
            max_iterations=3,
            success_threshold=0.8
        )
        self.review_logger = ReviewLogger(
            storage_dir=self.temp_dir
        )
        self.profile_composer = ArtistProfileComposer()
        
        # Test session ID
        self.session_id = "test_session_" + str(hash(self.__class__.__name__))
    
    def test_artist_creation_flow(self):
        """Test the complete artist creation flow."""
        # Step 1: Generate initial prompt
        artist_parameters = {
            "genre": "Dark Trap",
            "vibe": "Mysterious, Cold",
            "lifestyle": "Urban night life",
            "appearance": "Always wears a black hood and mask",
            "voice": "Deep and raspy"
        }
        
        prompt_package = self.prompt_designer.generate_prompt_for_review(artist_parameters)
        initial_prompt = prompt_package["generated_prompt"]
        
        # Verify prompt generation
        self.assertIsNotNone(initial_prompt)
        self.assertGreater(len(initial_prompt), 0)
        print(f"\nGenerated prompt: {initial_prompt[:100]}...")
        
        # Step 2: Start feedback loop
        iteration = 1
        current_prompt = initial_prompt
        final_prompt = None
        
        while self.feedback_loop_checker.should_continue() and iteration <= 3:
            print(f"\nIteration {iteration}:")
            
            # Log the prompt version
            prompt_id = self.review_logger.log_prompt_version(
                self.session_id, iteration, current_prompt
            )
            
            # Validate the prompt
            result, confidence_score, feedback = self.prompt_validator.validate_prompt(current_prompt)
            print(f"Validation result: {result.value}, Score: {confidence_score:.2f}")
            
            # Log validation result
            validation_id = self.review_logger.log_validation_result(
                self.session_id, iteration, prompt_id, 
                {"result": result.value, "confidence_score": confidence_score, "feedback": feedback}
            )
            
            # Track iteration in feedback loop checker
            self.feedback_loop_checker.track_iteration(
                iteration, confidence_score, result.value, feedback
            )
            
            # Log iteration summary
            self.review_logger.log_iteration_summary(
                self.session_id, iteration, prompt_id, None, validation_id,
                result.value, confidence_score
            )
            
            # If valid or max iterations reached, exit loop
            if result == ValidationResult.VALID or not self.feedback_loop_checker.should_continue():
                final_prompt = current_prompt
                break
            
            # Otherwise, improve the prompt (mock improvement for testing)
            current_prompt = self._improve_prompt(current_prompt, feedback)
            iteration += 1
        
        # Verify feedback loop
        status = self.feedback_loop_checker.get_status()
        print(f"\nFeedback loop status: {status['status']}")
        self.assertIsNotNone(status)
        self.assertIn(status["status"], [s.value for s in FeedbackLoopStatus])
        
        # If no valid prompt was generated, use the best one
        if final_prompt is None:
            best_iteration = self.feedback_loop_checker.get_best_iteration()
            if best_iteration:
                # Get the prompt from the review logger
                logs = self.review_logger.get_logs_by_session(self.session_id)
                prompts = logs.get("prompts", [])
                matching_prompts = [p for p in prompts if p.get("iteration") == best_iteration["iteration_number"]]
                if matching_prompts:
                    final_prompt = matching_prompts[0]["prompt"]
                else:
                    final_prompt = initial_prompt  # Fallback
            else:
                final_prompt = initial_prompt  # Fallback
        
        # Step 3: Compose artist profile
        profile = self.profile_composer.compose_profile(
            final_prompt, session_id=self.session_id
        )
        
        # Verify profile composition
        self.assertIsNotNone(profile)
        self.assertIn("name", profile)
        self.assertIn("genre", profile)
        self.assertIn("vibe", profile)
        print(f"\nComposed profile for artist: {profile['name']}")
        print(f"Genre: {profile['genre']}")
        print(f"Vibe: {profile['vibe']}")
        
        # Verify logs were created
        logs = self.review_logger.get_logs_by_session(self.session_id)
        self.assertIn("prompts", logs)
        self.assertIn("validations", logs)
        self.assertIn("summaries", logs)
        
        # Get iteration history
        history = self.review_logger.get_iteration_history(self.session_id)
        self.assertIn("iterations", history)
        self.assertGreaterEqual(len(history["iterations"]), 1)
    
    def _improve_prompt(self, prompt, feedback):
        """Mock function to improve a prompt based on feedback."""
        # This is a simplified mock implementation for testing
        # In a real system, this would use an LLM to improve the prompt
        
        improved_prompt = prompt
        
        # Add missing elements
        if "required_elements" in feedback and feedback["required_elements"]["status"] == "fail":
            missing = feedback["required_elements"].get("missing", [])
            if "voice" in missing:
                improved_prompt += " Their voice is deep and distinctive, adding character to their music."
            if "appearance" in missing:
                improved_prompt += " Their visual appearance is striking and memorable, with a unique style that sets them apart."
        
        # Improve length if needed
        if "length" in feedback and feedback["length"]["status"] == "fail":
            if feedback["length"].get("actual_length", 0) < self.prompt_validator.min_length:
                improved_prompt += " They have developed a loyal following through consistent releases and a strong social media presence. Their music resonates with listeners who appreciate authentic expression and innovative production techniques."
        
        # Add style keywords
        if "style" in feedback and feedback["style"]["status"] == "fail":
            improved_prompt += " Their creative approach is unique and innovative, producing distinctive tracks that stand out in the current music landscape."
        
        return improved_prompt
    
    def tearDown(self):
        """Clean up after the test."""
        # In a real test, we would remove the temporary directory
        # but for this example, we'll leave it for inspection
        pass


if __name__ == "__main__":
    unittest.main()
