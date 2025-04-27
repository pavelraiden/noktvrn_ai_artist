"""
LLM Pipeline Module for Artist Profile Builder

This module manages the LLM-based generation and refinement of artist profiles
by extending initial user inputs into complete profiles through prompting and
iterative refinement.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import sys

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from llm_orchestrator
from llm_orchestrator.orchestrator import LLMOrchestrator
from llm_orchestrator.llm_interface import LLMInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.llm_pipeline")


class LLMPipelineError(Exception):
    """Exception raised for errors in the LLM pipeline."""
    pass


class ArtistProfileLLMPipeline:
    """
    Manages the LLM-based generation and refinement of artist profiles.
    """

    def __init__(self, llm_orchestrator: Optional[LLMOrchestrator] = None):
        """
        Initialize the LLM pipeline.
        
        Args:
            llm_orchestrator: Optional LLMOrchestrator instance. If not provided,
                              a new instance will be created.
        """
        self.llm_orchestrator = llm_orchestrator or LLMOrchestrator()
        self.session_id = None
        logger.info("Initialized ArtistProfileLLMPipeline")

    def build_context(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build context for LLM prompting from initial inputs.
        
        Args:
            initial_input: Dictionary containing the initial user inputs
            
        Returns:
            Dictionary containing the context for LLM prompting
        """
        logger.info("Building context from initial inputs")
        
        # Start with the initial input
        context = initial_input.copy()
        
        # Add additional context information
        context["generation_purpose"] = "artist_profile_creation"
        
        # Format lists as comma-separated strings for better prompting
        for key, value in context.items():
            if isinstance(value, list):
                context[key + "_text"] = ", ".join(value)
        
        logger.debug(f"Built context: {json.dumps(context, indent=2)}")
        return context

    def create_profile_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create a prompt for generating an artist profile.
        
        Args:
            context: Dictionary containing the context for LLM prompting
            
        Returns:
            String containing the prompt
        """
        logger.info("Creating profile generation prompt")
        
        # Extract key information from context
        stage_name = context.get("stage_name", "")
        genre = context.get("genre", "")
        subgenres_text = context.get("subgenres_text", "")
        style_description = context.get("style_description", "")
        voice_type = context.get("voice_type", "")
        personality_traits_text = context.get("personality_traits_text", "")
        target_audience = context.get("target_audience", "")
        visual_identity_prompt = context.get("visual_identity_prompt", "")
        
        # Optional fields
        real_name = context.get("real_name", "")
        backstory = context.get("backstory", "")
        influences_text = context.get("influences_text", "")
        notes = context.get("notes", "")
        
        # Build the prompt
        prompt = f"""
You are an expert music industry professional tasked with creating a detailed profile for a new AI-generated music artist.

# ARTIST INFORMATION PROVIDED:
- Stage Name: {stage_name}
- Genre: {genre}
- Subgenres: {subgenres_text}
- Style Description: {style_description}
- Voice Type: {voice_type}
- Personality Traits: {personality_traits_text}
- Target Audience: {target_audience}
- Visual Identity Concept: {visual_identity_prompt}
"""

        # Add optional information if provided
        if real_name:
            prompt += f"- Real Name: {real_name}\n"
        if backstory:
            prompt += f"- Backstory: {backstory}\n"
        if influences_text:
            prompt += f"- Influences: {influences_text}\n"
        if notes:
            prompt += f"- Additional Notes: {notes}\n"

        # Add instructions for generation
        prompt += """
# YOUR TASK:
Create a comprehensive artist profile by expanding on the provided information. Your response must be in valid JSON format with the following structure:

```json
{
  "stage_name": "The artist's stage name",
  "real_name": "The artist's real name (if different from stage name)",
  "genre": "Primary music genre",
  "subgenres": ["Subgenre 1", "Subgenre 2", "Subgenre 3"],
  "style_description": "Detailed description of the artist's musical style",
  "voice_type": "Description of the artist's voice",
  "personality_traits": ["Trait 1", "Trait 2", "Trait 3", "Trait 4", "Trait 5"],
  "target_audience": "Detailed description of the target audience",
  "visual_identity_prompt": "Detailed prompt for generating visual identity",
  "song_prompt_generator": "Template name for song prompt generation",
  "video_prompt_generator": "Template name for video prompt generation",
  "backstory": "Detailed fictional backstory for the artist",
  "influences": ["Influence 1", "Influence 2", "Influence 3"]
}
```

# IMPORTANT GUIDELINES:
1. Maintain consistency with the provided information
2. Expand brief descriptions into detailed ones
3. Add depth to the artist's character and style
4. Ensure the backstory aligns with the personality traits
5. Make sure all fields are filled with appropriate content
6. For song_prompt_generator and video_prompt_generator, use template names that reflect the artist's style
7. Return ONLY the JSON object, no additional text

Your response must be a valid JSON object that can be parsed programmatically.
"""
        
        return prompt

    def create_refinement_prompt(self, profile_draft: Dict[str, Any], feedback: List[str]) -> str:
        """
        Create a prompt for refining an artist profile based on feedback.
        
        Args:
            profile_draft: Dictionary containing the draft profile
            feedback: List of feedback items to address
            
        Returns:
            String containing the prompt
        """
        logger.info("Creating profile refinement prompt")
        
        # Convert profile draft to JSON string
        profile_json = json.dumps(profile_draft, indent=2)
        
        # Build the prompt
        prompt = f"""
You are an expert music industry professional tasked with refining an AI-generated music artist profile.

# CURRENT ARTIST PROFILE DRAFT:
```json
{profile_json}
```

# FEEDBACK TO ADDRESS:
"""
        
        # Add each feedback item
        for i, item in enumerate(feedback, 1):
            prompt += f"{i}. {item}\n"
        
        # Add instructions for refinement
        prompt += """
# YOUR TASK:
Refine the artist profile by addressing all the feedback items. Your response must be in valid JSON format with the same structure as the current draft.

# IMPORTANT GUIDELINES:
1. Address ALL feedback items
2. Maintain consistency across all fields
3. Ensure the profile remains coherent and realistic
4. Make sure all fields are filled with appropriate content
5. Return ONLY the JSON object, no additional text

Your response must be a valid JSON object that can be parsed programmatically.
"""
        
        return prompt

    def generate_profile_draft(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an initial artist profile draft from user inputs.
        
        Args:
            initial_input: Dictionary containing the initial user inputs
            
        Returns:
            Dictionary containing the generated profile draft
        """
        logger.info("Generating initial profile draft")
        
        try:
            # Build context for prompting
            context = self.build_context(initial_input)
            
            # Create prompt
            prompt = self.create_profile_prompt(context)
            
            # Generate profile using LLM
            self.session_id = self.llm_orchestrator.create_session("artist_profile_generation")
            response = self.llm_orchestrator.generate_text(
                prompt=prompt,
                session_id=self.session_id,
                max_tokens=2048,
                temperature=0.7
            )
            
            # Extract JSON from response
            profile_draft = self.extract_json_from_response(response)
            
            logger.info("Successfully generated profile draft")
            return profile_draft
            
        except Exception as e:
            logger.error(f"Error generating profile draft: {e}")
            raise LLMPipelineError(f"Failed to generate profile draft: {e}")

    def refine_profile(self, profile_draft: Dict[str, Any], feedback: List[str]) -> Dict[str, Any]:
        """
        Refine an artist profile draft based on feedback.
        
        Args:
            profile_draft: Dictionary containing the draft profile
            feedback: List of feedback items to address
            
        Returns:
            Dictionary containing the refined profile
        """
        logger.info(f"Refining profile draft with {len(feedback)} feedback items")
        
        try:
            # Create refinement prompt
            prompt = self.create_refinement_prompt(profile_draft, feedback)
            
            # Generate refined profile using LLM
            response = self.llm_orchestrator.generate_text(
                prompt=prompt,
                session_id=self.session_id,
                max_tokens=2048,
                temperature=0.5  # Lower temperature for refinement
            )
            
            # Extract JSON from response
            refined_profile = self.extract_json_from_response(response)
            
            logger.info("Successfully refined profile")
            return refined_profile
            
        except Exception as e:
            logger.error(f"Error refining profile: {e}")
            raise LLMPipelineError(f"Failed to refine profile: {e}")

    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON object from LLM response.
        
        Args:
            response: String containing the LLM response
            
        Returns:
            Dictionary containing the extracted JSON object
        """
        logger.debug("Extracting JSON from LLM response")
        
        try:
            # Look for JSON block in markdown format
            if "```json" in response:
                # Extract content between ```json and ```
                start_idx = response.find("```json") + 7
                end_idx = response.find("```", start_idx)
                json_str = response[start_idx:end_idx].strip()
            elif "```" in response:
                # Extract content between ``` and ```
                start_idx = response.find("```") + 3
                end_idx = response.find("```", start_idx)
                json_str = response[start_idx:end_idx].strip()
            else:
                # Assume the entire response is JSON
                json_str = response.strip()
            
            # Parse JSON
            data = json.loads(json_str)
            
            logger.debug("Successfully extracted JSON from response")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting JSON from response: {e}")
            logger.error(f"Response: {response}")
            raise LLMPipelineError(f"Failed to extract JSON from LLM response: {e}")

    def generate_complete_profile(self, initial_input: Dict[str, Any], max_refinement_iterations: int = 3) -> Dict[str, Any]:
        """
        Generate a complete artist profile through initial generation and iterative refinement.
        
        Args:
            initial_input: Dictionary containing the initial user inputs
            max_refinement_iterations: Maximum number of refinement iterations
            
        Returns:
            Dictionary containing the complete artist profile
        """
        logger.info(f"Generating complete profile with up to {max_refinement_iterations} refinement iterations")
        
        # Generate initial profile draft
        profile = self.generate_profile_draft(initial_input)
        
        # Iterative refinement
        for iteration in range(max_refinement_iterations):
            # Check for issues that need refinement
            feedback = self.identify_refinement_needs(profile, initial_input)
            
            # If no issues, we're done
            if not feedback:
                logger.info(f"Profile complete after {iteration} refinement iterations")
                break
                
            logger.info(f"Refinement iteration {iteration + 1}/{max_refinement_iterations}: {len(feedback)} issues to address")
            
            # Refine the profile
            profile = self.refine_profile(profile, feedback)
        
        return profile

    def identify_refinement_needs(self, profile: Dict[str, Any], initial_input: Dict[str, Any]) -> List[str]:
        """
        Identify aspects of the profile that need refinement.
        
        Args:
            profile: Dictionary containing the current profile
            initial_input: Dictionary containing the initial user inputs
            
        Returns:
            List of feedback items for refinement
        """
        feedback = []
        
        # Check for missing required fields
        required_fields = [
            "stage_name", "genre", "subgenres", "style_description", 
            "voice_type", "personality_traits", "target_audience", 
            "visual_identity_prompt", "song_prompt_generator", 
            "video_prompt_generator", "backstory"
        ]
        
        for field in required_fields:
            if field not in profile or not profile[field]:
                feedback.append(f"The '{field}' field is missing or empty. Please provide appropriate content.")
        
        # Check for consistency with initial input
        for field in initial_input:
            if field in profile:
                # For list fields, check that all initial items are included
                if isinstance(initial_input[field], list) and isinstance(profile[field], list):
                    for item in initial_input[field]:
                        if item not in profile[field]:
                            feedback.append(f"The '{field}' list should include '{item}' from the initial input.")
                # For string fields, check that they match or are expanded versions
                elif isinstance(initial_input[field], str) and isinstance(profile[field], str):
                    if initial_input[field] and not initial_input[field].lower() in profile[field].lower():
                        feedback.append(f"The '{field}' should incorporate '{initial_input[field]}' from the initial input.")
        
        # Check for field quality
        if "backstory" in profile and len(profile["backstory"]) < 100:
            feedback.append("The backstory is too brief. Please provide a more detailed backstory.")
            
        if "style_description" in profile and len(profile["style_description"]) < 50:
            feedback.append("The style description is too brief. Please provide a more detailed description.")
            
        if "personality_traits" in profile and len(profile["personality_traits"]) < 3:
            feedback.append("Please provide at least 3 personality traits.")
        
        return feedback


def main():
    """Main function for testing the LLM pipeline."""
    # Example initial input
    initial_input = {
        "stage_name": "Neon Horizon",
        "genre": "Electronic",
        "subgenres": ["Synthwave", "Chillwave"],
        "style_description": "Retro-futuristic electronic music with nostalgic 80s influences",
        "voice_type": "Ethereal female vocals with vocoder effects",
        "personality_traits": ["Mysterious", "Introspective"],
        "target_audience": "25-35 year old electronic music fans",
        "visual_identity_prompt": "Neon cityscape at night with purple and blue color palette"
    }
    
    try:
        # Initialize pipeline
        pipeline = ArtistProfileLLMPipeline()
        
        # Generate complete profile
        profile = pipeline.generate_complete_profile(initial_input)
        
        # Print the result
        print(json.dumps(profile, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
