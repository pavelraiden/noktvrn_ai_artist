"""
Artist Prompt Designer

This module generates dynamic artist identity prompts based on various parameters
such as genre, vibe, lifestyle, appearance, and voice characteristics.

The generated prompts are designed to be reviewed by another LLM for refinement.
"""

import random
from typing import Dict, List, Optional, Any, Union


class ArtistPromptDesigner:
    """
    Generates artist identity prompts based on provided parameters.
    
    This class uses dynamic templating to create varied and creative prompts
    that describe an artist's identity, style, and characteristics.
    """
    
    def __init__(self):
        """Initialize the ArtistPromptDesigner with template components."""
        # Template components for different sections of the prompt
        self.intro_templates = [
            "Create a detailed profile for {genre} artist who embodies a {vibe} essence.",
            "Design a {genre} musician with a {vibe} persona.",
            "Develop a {genre} artist concept with {vibe} characteristics.",
            "Craft an identity for a {genre} creator with a distinctly {vibe} presence.",
            "Envision a {genre} performer who exudes {vibe} energy."
        ]
        
        self.lifestyle_templates = [
            "They thrive in {lifestyle} environments.",
            "Their life revolves around {lifestyle} culture.",
            "They're deeply connected to {lifestyle} scenes.",
            "Their authentic connection to {lifestyle} shapes their art.",
            "They're known for their involvement in {lifestyle} communities."
        ]
        
        self.appearance_templates = [
            "Visually, they're recognized by {appearance}.",
            "Their signature look includes {appearance}.",
            "Their image is defined by {appearance}.",
            "They're visually distinctive with {appearance}.",
            "Their aesthetic is characterized by {appearance}."
        ]
        
        self.voice_templates = [
            "Their voice is distinctively {voice}.",
            "They deliver lyrics with a {voice} vocal style.",
            "Their sound is characterized by {voice} vocals.",
            "Their {voice} voice is their trademark.",
            "Their vocal delivery is unmistakably {voice}."
        ]
        
        self.outro_templates = [
            "This artist represents the evolution of {genre} through a unique creative lens.",
            "Their work pushes the boundaries of {genre} while maintaining authenticity.",
            "They're positioned to redefine what {genre} means in today's musical landscape.",
            "Their artistic vision brings fresh perspective to the {genre} scene.",
            "They embody the future direction of {genre} while honoring its roots."
        ]
        
        # Genre-specific descriptors to enhance the prompt
        self.genre_descriptors = {
            "trap": ["bass-heavy", "atmospheric", "rhythmic", "hypnotic", "gritty"],
            "dark trap": ["ominous", "shadowy", "intense", "haunting", "brooding"],
            "phonk": ["nostalgic", "memphis-inspired", "cowbell-driven", "distorted", "sample-heavy"],
            "drill": ["raw", "unfiltered", "street", "aggressive", "authentic"],
            "hip hop": ["lyrical", "flow-focused", "beat-driven", "expressive", "rhythmic"],
            "lofi": ["mellow", "nostalgic", "relaxed", "atmospheric", "textured"],
            "electronic": ["synthesized", "progressive", "digital", "innovative", "layered"],
            "pop": ["catchy", "melodic", "accessible", "polished", "hook-driven"],
            "r&b": ["soulful", "emotional", "smooth", "groove-oriented", "expressive"],
            "alternative": ["unconventional", "boundary-pushing", "experimental", "unique", "genre-blending"]
        }
        
        # Vibe-specific elaborations
        self.vibe_elaborations = {
            "mysterious": ["enigmatic presence", "cryptic messaging", "veiled identity", "elusive persona", "secretive nature"],
            "cold": ["emotionally detached", "calculated precision", "icy demeanor", "clinical delivery", "detached observation"],
            "energetic": ["dynamic performance", "high-octane delivery", "vibrant presence", "electric energy", "animated expression"],
            "melancholic": ["introspective themes", "emotional depth", "wistful expression", "contemplative mood", "pensive delivery"],
            "aggressive": ["confrontational style", "forceful delivery", "intense presence", "dominant energy", "powerful impact"],
            "chill": ["relaxed approach", "laid-back attitude", "effortless cool", "unhurried delivery", "calm presence"],
            "ethereal": ["dreamlike quality", "otherworldly presence", "transcendent sound", "celestial vibe", "surreal aesthetic"],
            "raw": ["unfiltered expression", "authentic emotion", "unpolished edge", "genuine presence", "unrefined power"]
        }
        
        # Lifestyle context enhancers
        self.lifestyle_enhancers = {
            "urban": ["city streets", "concrete landscape", "metropolitan energy", "urban architecture", "city nightlife"],
            "night life": ["after-hours scene", "neon-lit venues", "nocturnal existence", "midnight culture", "darkness-embracing"],
            "underground": ["hidden venues", "word-of-mouth events", "exclusive circles", "beneath the mainstream", "cult following"],
            "luxury": ["high-end lifestyle", "exclusive access", "premium experiences", "opulent surroundings", "elite circles"],
            "street": ["neighborhood roots", "block culture", "community connected", "local scene", "grassroots presence"],
            "digital": ["online presence", "virtual communities", "digital platforms", "internet culture", "tech-savvy approach"],
            "nomadic": ["constantly moving", "location-independent", "journey-inspired", "travel-influenced", "borderless existence"],
            "spiritual": ["inner journey", "consciousness exploration", "meditative practice", "higher awareness", "soul-connected"]
        }

    def generate_prompt(self, parameters: Dict[str, str]) -> str:
        """
        Generate an artist identity prompt based on the provided parameters.
        
        Args:
            parameters: Dictionary containing artist parameters such as:
                - genre: Musical genre (e.g., "trap", "phonk")
                - vibe: Overall feeling/mood (e.g., "mysterious", "energetic")
                - lifestyle: Artist's lifestyle (e.g., "urban night life")
                - appearance: Visual characteristics (e.g., "black hood and mask")
                - voice: Vocal qualities (e.g., "deep and raspy")
                
        Returns:
            A dynamically generated artist identity prompt.
        """
        # Extract parameters with defaults for missing values
        genre_original = parameters.get("genre", "")
        genre_lower = genre_original.lower() if genre_original else ""
        
        vibe_original = parameters.get("vibe", "")
        vibe_lower = vibe_original.lower() if vibe_original else ""
        
        lifestyle = parameters.get("lifestyle", "")
        appearance = parameters.get("appearance", "")
        voice = parameters.get("voice", "")
        
        # Select random templates for each section
        intro = random.choice(self.intro_templates)
        lifestyle_template = random.choice(self.lifestyle_templates) if lifestyle else ""
        appearance_template = random.choice(self.appearance_templates) if appearance else ""
        voice_template = random.choice(self.voice_templates) if voice else ""
        outro = random.choice(self.outro_templates)
        
        # Format the templates with the provided parameters
        # Use original case for genre and vibe in the formatted text
        formatted_intro = intro.format(genre=genre_original, vibe=vibe_original)
        formatted_lifestyle = lifestyle_template.format(lifestyle=lifestyle) if lifestyle else ""
        formatted_appearance = appearance_template.format(appearance=appearance) if appearance else ""
        formatted_voice = voice_template.format(voice=voice) if voice else ""
        formatted_outro = outro.format(genre=genre_original)
        
        # Add genre-specific descriptors if available
        genre_desc = ""
        for genre_key in self.genre_descriptors:
            if genre_key in genre_lower:
                descriptors = self.genre_descriptors[genre_key]
                selected_descriptor = random.choice(descriptors)
                genre_desc = f" Their sound is distinctively {selected_descriptor}."
                break
        
        # Add vibe elaboration if available
        vibe_elab = ""
        for vibe_key in self.vibe_elaborations:
            if vibe_key in vibe_lower:
                elaborations = self.vibe_elaborations[vibe_key]
                selected_elaboration = random.choice(elaborations)
                vibe_elab = f" They're known for their {selected_elaboration}."
                break
        
        # Add lifestyle enhancer if available
        lifestyle_enhance = ""
        for key, enhancers in self.lifestyle_enhancers.items():
            if key in lifestyle.lower():
                selected_enhancer = random.choice(enhancers)
                lifestyle_enhance = f" This connects them to {selected_enhancer}."
                break
        
        # Combine all sections into a cohesive prompt
        sections = [
            formatted_intro,
            formatted_lifestyle + lifestyle_enhance if formatted_lifestyle else "",
            formatted_appearance if formatted_appearance else "",
            formatted_voice if formatted_voice else "",
            genre_desc,
            vibe_elab,
            formatted_outro
        ]
        
        # Filter out empty sections and join with spaces
        prompt = " ".join(filter(None, sections))
        
        return prompt
    
    def generate_prompt_for_review(self, parameters: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate an artist identity prompt formatted for LLM review.
        
        Args:
            parameters: Dictionary containing artist parameters.
                
        Returns:
            A dictionary containing the generated prompt and metadata for review.
        """
        prompt = self.generate_prompt(parameters)
        
        # Create a structured output for the reviewing LLM
        review_package = {
            "prompt_type": "artist_identity",
            "parameters": parameters,
            "generated_prompt": prompt,
            "review_instructions": "Review this artist identity prompt for coherence, creativity, and alignment with the specified parameters. Suggest improvements if needed.",
            "version": "1.0"
        }
        
        return review_package


# Example usage
if __name__ == "__main__":
    designer = ArtistPromptDesigner()
    
    # Example parameters
    example_params = {
        "genre": "Dark Trap",
        "vibe": "Mysterious, Cold",
        "lifestyle": "Urban night life",
        "appearance": "Always wears a black hood and mask",
        "voice": "Deep and raspy"
    }
    
    # Generate a prompt
    prompt = designer.generate_prompt(example_params)
    print("Generated Prompt:")
    print(prompt)
    
    # Generate a prompt for review
    review_package = designer.generate_prompt_for_review(example_params)
    print("\nPrompt Package for Review:")
    import json
    print(json.dumps(review_package, indent=2))
