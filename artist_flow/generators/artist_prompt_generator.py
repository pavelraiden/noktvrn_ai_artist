"""
Artist Prompt Generator Module

This module provides a comprehensive system for generating detailed prompts for AI artist creation
based on user-defined parameters. It creates rich, detailed prompts suitable for multi-agent
communication between LLMs in the artist creation process.

The module generates prompts covering various aspects of an artist's identity including:
- Artist name
- Artist style and mood
- Preferred genres
- Persona traits
- Target audience
- Visual identity
- Language for lyrics
- Themes and values
- Lifestyle and attitude
"""

from typing import Dict, List, Optional, Any, Union
import logging
import random
import os
import json
from pathlib import Path
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("artist_prompt_generator")

# Try to load environment variables if .env exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.info("dotenv not installed, skipping environment variable loading")


class ArtistPromptGenerator:
    """
    Generates comprehensive prompts for AI artist creation based on user parameters.
    
    This class provides methods to generate detailed prompts covering all aspects of
    an artist's identity, suitable for multi-agent LLM communication in the artist
    creation process.
    """
    
    def __init__(self, template_variety: int = 3, seed: Optional[int] = None):
        """
        Initialize the artist prompt generator.
        
        Args:
            template_variety: Number of template variations to use for each section
            seed: Optional random seed for reproducible generation
        """
        self.template_variety = template_variety
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            
        # Load genre database
        self.genre_elements = self._load_genre_database()
        
        # Load visual style database
        self.visual_elements = self._load_visual_database()
        
        logger.info("Initialized ArtistPromptGenerator")
    
    def _load_genre_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the genre database with musical elements for different genres.
        
        Returns:
            Dictionary mapping genre names to their musical elements
        """
        # Genre-specific elements dictionary
        genre_elements = {
            "trap": {
                "instruments": ["808 bass", "hi-hats", "snares", "synthesizers"],
                "tempo_range": (120, 160),
                "themes": ["street life", "ambition", "struggle", "success"],
                "mood": ["dark", "atmospheric", "intense", "moody"],
                "production": ["heavy bass", "layered beats", "vocal effects"],
                "audience": ["urban youth", "club-goers", "hip-hop fans"],
                "visual_aesthetic": ["urban", "night scenes", "luxury items", "street fashion"]
            },
            "dark trap": {
                "instruments": ["distorted 808s", "atmospheric pads", "minor keys", "deep bass"],
                "tempo_range": (110, 150),
                "themes": ["darkness", "inner demons", "night life", "isolation"],
                "mood": ["ominous", "mysterious", "haunting", "melancholic"],
                "production": ["reverb", "echo", "distortion", "ambient sounds"],
                "audience": ["alternative youth", "night owls", "introspective listeners"],
                "visual_aesthetic": ["dark imagery", "masks", "shadows", "monochrome"]
            },
            "phonk": {
                "instruments": ["cowbell", "memphis drums", "vinyl crackle", "pitched vocals"],
                "tempo_range": (130, 160),
                "themes": ["nostalgia", "retro", "driving", "night cruising"],
                "mood": ["eerie", "energetic", "hypnotic", "aggressive"],
                "production": ["chopped samples", "lo-fi elements", "heavy sidechaining"],
                "audience": ["car enthusiasts", "retro culture fans", "underground scene"],
                "visual_aesthetic": ["VHS effects", "90s aesthetics", "cars", "night drives"]
            },
            "lofi": {
                "instruments": ["mellow piano", "jazz samples", "vinyl crackle", "soft drums"],
                "tempo_range": (70, 90),
                "themes": ["relaxation", "study", "nostalgia", "introspection"],
                "mood": ["calm", "melancholic", "peaceful", "warm"],
                "production": ["sample-based", "vinyl effects", "subtle imperfections"],
                "audience": ["students", "relaxation seekers", "focus workers"],
                "visual_aesthetic": ["anime influences", "cozy spaces", "rain", "urban scenery"]
            },
            "edm": {
                "instruments": ["synthesizers", "drum machines", "vocal chops", "risers"],
                "tempo_range": (120, 150),
                "themes": ["celebration", "energy", "euphoria", "freedom"],
                "mood": ["uplifting", "energetic", "exciting", "positive"],
                "production": ["drops", "buildups", "layered synths", "clean mixing"],
                "audience": ["festival-goers", "club scene", "party crowd"],
                "visual_aesthetic": ["bright colors", "light shows", "festival imagery", "futuristic"]
            },
            "hip hop": {
                "instruments": ["drum breaks", "samples", "bass lines", "scratching"],
                "tempo_range": (85, 110),
                "themes": ["urban life", "social commentary", "personal growth", "storytelling"],
                "mood": ["confident", "reflective", "assertive", "authentic"],
                "production": ["sample-based", "boom bap", "layered vocals"],
                "audience": ["hip-hop culture enthusiasts", "urban youth", "lyric appreciators"],
                "visual_aesthetic": ["urban settings", "street art", "fashion", "cultural symbols"]
            },
            "ambient": {
                "instruments": ["synthesizer pads", "field recordings", "processed sounds", "drones"],
                "tempo_range": (60, 80),
                "themes": ["nature", "space", "meditation", "transcendence"],
                "mood": ["atmospheric", "ethereal", "spacious", "contemplative"],
                "production": ["reverb", "delay", "textural layers", "minimal percussion"],
                "audience": ["meditation practitioners", "focus workers", "relaxation seekers"],
                "visual_aesthetic": ["natural landscapes", "abstract visuals", "minimalist", "ethereal"]
            },
            "techno": {
                "instruments": ["analog synths", "drum machines", "acid lines", "industrial sounds"],
                "tempo_range": (120, 140),
                "themes": ["futurism", "technology", "machine aesthetics", "hypnotic states"],
                "mood": ["driving", "hypnotic", "mechanical", "intense"],
                "production": ["repetitive patterns", "layered percussion", "minimal elements"],
                "audience": ["club-goers", "electronic music enthusiasts", "underground scene"],
                "visual_aesthetic": ["industrial", "minimalist", "technological", "monochromatic"]
            },
            "pop": {
                "instruments": ["polished vocals", "synthesizers", "acoustic elements", "clean drums"],
                "tempo_range": (90, 120),
                "themes": ["love", "relationships", "self-empowerment", "celebration"],
                "mood": ["catchy", "upbeat", "emotional", "accessible"],
                "production": ["vocal-forward", "radio-ready", "hook-focused"],
                "audience": ["mainstream listeners", "radio audience", "diverse demographics"],
                "visual_aesthetic": ["polished", "colorful", "fashion-forward", "accessible"]
            },
            "indie": {
                "instruments": ["guitars", "organic drums", "analog synths", "raw vocals"],
                "tempo_range": (80, 130),
                "themes": ["authenticity", "personal experiences", "relationships", "social observations"],
                "mood": ["intimate", "thoughtful", "emotive", "genuine"],
                "production": ["organic", "less processed", "room sound", "imperfections"],
                "audience": ["alternative music fans", "college crowd", "thoughtful listeners"],
                "visual_aesthetic": ["artistic", "candid", "natural settings", "film photography"]
            }
        }
        
        # Check for environment variable with custom genre database path
        custom_db_path = os.getenv("ARTIST_GENRE_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, 'r') as f:
                    custom_genres = json.load(f)
                    # Merge with default genres, with custom genres taking precedence
                    genre_elements.update(custom_genres)
                    logger.info(f"Loaded custom genre database from {custom_db_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom genre database: {e}")
        
        return genre_elements
    
    def _load_visual_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the visual style database with elements for different artist styles.
        
        Returns:
            Dictionary mapping style keywords to their visual elements
        """
        # Common visual styles
        visual_elements = {
            "mysterious": {
                "colors": ["dark blue", "purple", "black", "silver"],
                "imagery": ["shadows", "fog", "silhouettes", "hidden faces"],
                "composition": ["asymmetrical", "obscured", "dramatic lighting"],
                "textures": ["smoky", "misty", "velvet", "metallic"],
                "fashion": ["hooded", "masked", "dark clothing", "accessories that hide identity"]
            },
            "cold": {
                "colors": ["ice blue", "white", "silver", "pale gray"],
                "imagery": ["frost", "minimalist", "geometric", "sharp edges"],
                "composition": ["sparse", "clean lines", "negative space"],
                "textures": ["icy", "smooth", "glass-like", "crystalline"],
                "fashion": ["monochromatic", "sleek", "minimal", "structured"]
            },
            "energetic": {
                "colors": ["bright red", "electric blue", "neon yellow", "orange"],
                "imagery": ["motion blur", "dynamic shapes", "action", "light streaks"],
                "composition": ["diagonal lines", "asymmetry", "movement"],
                "textures": ["glossy", "vibrant", "electric", "sharp"],
                "fashion": ["bold", "sporty", "statement pieces", "bright accents"]
            },
            "nostalgic": {
                "colors": ["sepia", "faded blue", "muted red", "cream"],
                "imagery": ["vintage objects", "film grain", "old photographs", "retro tech"],
                "composition": ["centered", "framed", "symmetrical"],
                "textures": ["worn", "grainy", "paper", "aged"],
                "fashion": ["vintage-inspired", "classic", "timeless pieces", "retro accessories"]
            },
            "futuristic": {
                "colors": ["neon blue", "purple", "black", "electric green"],
                "imagery": ["technology", "glitches", "holograms", "geometric patterns"],
                "composition": ["grid-based", "floating elements", "perspective"],
                "textures": ["glossy", "metallic", "digital", "glowing"],
                "fashion": ["avant-garde", "tech-inspired", "unconventional materials", "LED elements"]
            },
            "organic": {
                "colors": ["earth tones", "forest green", "terracotta", "natural blue"],
                "imagery": ["plants", "natural elements", "flowing forms", "handmade"],
                "composition": ["flowing", "natural balance", "asymmetrical"],
                "textures": ["rough", "tactile", "natural", "handcrafted"],
                "fashion": ["natural fabrics", "layered", "earthy tones", "handcrafted accessories"]
            },
            "aggressive": {
                "colors": ["red", "black", "dark gray", "acid green"],
                "imagery": ["sharp edges", "aggressive symbols", "intensity", "distortion"],
                "composition": ["dynamic", "confrontational", "imposing"],
                "textures": ["rough", "distressed", "industrial", "raw"],
                "fashion": ["edgy", "leather", "metal accents", "statement pieces"]
            },
            "dreamy": {
                "colors": ["pastel blue", "lavender", "soft pink", "mint green"],
                "imagery": ["clouds", "soft focus", "ethereal light", "floating elements"],
                "composition": ["soft edges", "layered", "dreamy blur"],
                "textures": ["soft", "airy", "translucent", "flowing"],
                "fashion": ["flowing fabrics", "soft layers", "delicate details", "ethereal"]
            }
        }
        
        # Check for environment variable with custom visual database path
        custom_db_path = os.getenv("ARTIST_VISUAL_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, 'r') as f:
                    custom_visuals = json.load(f)
                    # Merge with default visuals, with custom visuals taking precedence
                    visual_elements.update(custom_visuals)
                    logger.info(f"Loaded custom visual database from {custom_db_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom visual database: {e}")
        
        return visual_elements
    
    def _extract_genre_elements(self, genre: str) -> Dict[str, Any]:
        """
        Extract key musical and stylistic elements associated with a genre.
        
        Args:
            genre: Music genre name
            
        Returns:
            Dictionary of genre elements
        """
        # Normalize genre name for lookup
        normalized_genre = genre.lower()
        
        # Check for multi-word genres first
        if normalized_genre in self.genre_elements:
            return self.genre_elements[normalized_genre]
        
        # Try to match single words if full genre not found
        for key in self.genre_elements:
            if key in normalized_genre:
                return self.genre_elements[key]
        
        # Default elements if genre not recognized
        return {
            "instruments": ["synthesizers", "drums", "bass", "vocals"],
            "tempo_range": (90, 130),
            "themes": ["expression", "emotion", "experience", "storytelling"],
            "mood": ["expressive", "emotive", "atmospheric"],
            "production": ["professional", "balanced", "clear"],
            "audience": ["music enthusiasts", "genre explorers", "open-minded listeners"],
            "visual_aesthetic": ["distinctive", "authentic", "artistic", "professional"]
        }
    
    def _extract_visual_elements(self, style: str) -> Dict[str, Any]:
        """
        Extract key visual elements associated with an artist style.
        
        Args:
            style: Artist style description
            
        Returns:
            Dictionary of visual elements
        """
        # Extract style keywords
        style_keywords = [word.strip().lower() for word in style.split(",")]
        
        # Collect elements from matching styles
        combined_elements = {
            "colors": [],
            "imagery": [],
            "composition": [],
            "textures": [],
            "fashion": []
        }
        
        matches_found = False
        
        # Look for direct matches
        for keyword in style_keywords:
            if keyword in self.visual_elements:
                matches_found = True
                for category in combined_elements:
                    combined_elements[category].extend(self.visual_elements[keyword][category])
        
        # If no direct matches, look for partial matches
        if not matches_found:
            for keyword in style_keywords:
                for style_name, elements in self.visual_elements.items():
                    if keyword in style_name or style_name in keyword:
                        for category in combined_elements:
                            combined_elements[category].extend(elements[category])
        
        # If still no matches, use default elements
        if not any(combined_elements.values()):
            return {
                "colors": ["black", "white", "primary colors", "contrasting tones"],
                "imagery": ["abstract shapes", "symbolic elements", "representative icons"],
                "composition": ["balanced", "focused", "intentional"],
                "textures": ["mixed", "appropriate to genre", "distinctive"],
                "fashion": ["distinctive", "genre-appropriate", "personal style", "recognizable"]
            }
        
        # Remove duplicates while preserving order
        for category in combined_elements:
            seen = set()
            combined_elements[category] = [x for x in combined_elements[category] 
                                          if not (x in seen or seen.add(x))]
        
        return combined_elements
    
    def _extract_persona_traits(self, persona: str) -> List[str]:
        """
        Extract and expand persona traits from a comma-separated string.
        
        Args:
            persona: Comma-separated string of persona traits
            
        Returns:
            List of expanded persona traits with descriptions
        """
        # Common persona traits with expanded descriptions
        trait_expansions = {
            "mysterious": ["keeps personal details private", "reveals little about true identity", 
                          "creates intrigue through ambiguity", "communicates through art rather than words"],
            "energetic": ["brings high energy to performances", "creates dynamic, upbeat content", 
                         "maintains an active presence", "engages enthusiastically with audience"],
            "soft": ["presents a gentle, approachable persona", "creates calming, soothing content", 
                    "communicates with warmth and empathy", "avoids harsh or aggressive elements"],
            "aggressive": ["presents a bold, confrontational image", "pushes boundaries in content and style", 
                          "uses direct, powerful communication", "challenges conventions and expectations"],
            "intellectual": ["incorporates complex themes and references", "engages with philosophical concepts", 
                            "creates thought-provoking content", "appeals to analytical listeners"],
            "playful": ["incorporates humor and lightheartedness", "experiments with unexpected elements", 
                       "maintains a sense of fun and joy", "doesn't take themselves too seriously"],
            "authentic": ["presents a genuine, unfiltered image", "shares personal experiences and emotions", 
                         "maintains consistency between art and persona", "values honesty in expression"],
            "enigmatic": ["cultivates an air of mystery and intrigue", "leaves interpretation open to audience", 
                         "creates layered, symbolic content", "reveals identity gradually over time"],
            "rebellious": ["challenges mainstream conventions", "pushes against established norms", 
                          "represents counterculture values", "stands for alternative perspectives"],
            "spiritual": ["incorporates metaphysical or spiritual themes", "explores consciousness and meaning", 
                         "connects to deeper human experiences", "offers transcendent perspectives"]
        }
        
        # Extract traits from comma-separated string
        traits = [trait.strip().lower() for trait in persona.split(",")]
        
        # Collect expanded descriptions
        expanded_traits = []
        for trait in traits:
            if trait in trait_expansions:
                # Add the trait name and 2 random expansions
                expansions = random.sample(trait_expansions[trait], min(2, len(trait_expansions[trait])))
                expanded_traits.append(f"{trait.capitalize()}: {' and '.join(expansions)}")
            else:
                # For traits not in our database, just capitalize
                expanded_traits.append(trait.capitalize())
        
        return expanded_traits
    
    def generate_artist_prompt(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive prompt for creating an AI artist based on input parameters.
        
        Args:
            params: Dictionary containing artist parameters such as:
                - genre: Musical genre (e.g., "Dark Trap", "Phonk")
                - style: Artist's stylistic description (e.g., "Mysterious, Cold")
                - persona: Personality traits (e.g., "mysterious, energetic, soft")
                - target_audience: Target demographic (optional)
                - visual_identity: Visual style hints (optional)
                - lyrics_language: Language for lyrics (optional)
                - themes: Themes or values represented (optional)
                - lifestyle: Lifestyle/attitude hints (optional)
                - special_notes: Special notes for AI enhancement (optional)
                
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(f"Generating artist prompt for genre: {params.get('genre', 'Unknown')}")
        
        # Extract key parameters with defaults
        genre = params.get('genre', 'Electronic')
        style = params.get('style', 'Unique, Distinctive')
        persona = params.get('persona', 'Authentic')
        target_audience = params.get('target_audience', '')
        visual_identity = params.get('visual_identity', '')
        lyrics_language = params.get('lyrics_language', 'English')
        themes = params.get('themes', '')
        lifestyle = params.get('lifestyle', '')
        special_notes = params.get('special_notes', '')
        
        # Get genre-specific elements
        genre_elements = self._extract_genre_elements(genre)
        
        # Get visual elements based on style
        visual_elements = self._extract_visual_elements(style)
        
        # Get expanded persona traits
        persona_traits = self._extract_persona_traits(persona)
        
        # Determine target audience if not provided
        if not target_audience:
            target_audience = ", ".join(random.sample(genre_elements["audience"], 
                                                     min(2, len(genre_elements["audience"]))))
        
        # Determine themes if not provided
        if not themes:
            themes = ", ".join(random.sample(genre_elements["themes"], 
                                            min(3, len(genre_elements["themes"]))))
        
        # Build the comprehensive prompt
        prompt = f"""# Artist Creation Prompt

## Core Identity
Create a detailed profile for a new {genre} music artist with a {style} style. The artist should embody the following persona traits:
{chr(10).join(f"- {trait}" for trait in persona_traits)}

## Musical Identity
- **Primary Genre:** {genre}
- **Sub-genres/Influences:** Select appropriate sub-genres that complement the main style
- **Signature Sound:** Should feature {', '.join(random.sample(genre_elements["instruments"], min(3, len(genre_elements["instruments"]))))}
- **Production Style:** {', '.join(random.sample(genre_elements["production"], min(2, len(genre_elements["production"]))))}
- **Tempo Range:** Typically between {genre_elements["tempo_range"][0]}-{genre_elements["tempo_range"][1]} BPM
- **Mood:** {', '.join(random.sample(genre_elements["mood"], min(3, len(genre_elements["mood"]))))}

## Visual Identity
- **Color Palette:** {', '.join(random.sample(visual_elements["colors"], min(3, len(visual_elements["colors"]))))}
- **Imagery/Symbols:** {', '.join(random.sample(visual_elements["imagery"], min(3, len(visual_elements["imagery"]))))}
- **Visual Composition:** {', '.join(random.sample(visual_elements["composition"], min(2, len(visual_elements["composition"]))))}
- **Fashion/Style:** {', '.join(random.sample(visual_elements["fashion"], min(2, len(visual_elements["fashion"]))))}
"""

        # Add visual identity specifics if provided
        if visual_identity:
            prompt += f"- **Additional Visual Elements:** {visual_identity}\n"

        # Add target audience
        prompt += f"\n## Audience and Reach\n- **Target Audience:** {target_audience}\n"
        
        # Add lyrics language
        prompt += f"- **Lyrics Language:** {lyrics_language}\n"
        
        # Add themes
        prompt += f"\n## Thematic Elements\n- **Key Themes:** {themes}\n"
        
        # Add lifestyle if provided
        if lifestyle:
            prompt += f"\n## Lifestyle and Attitude\n- **Lifestyle:** {lifestyle}\n"
        
        # Add special notes if provided
        if special_notes:
            prompt += f"\n## Special Notes\n{special_notes}\n"
        
        # Add final instructions
        prompt += """
## Creation Instructions
1. Create a unique, memorable artist name that reflects the genre and style
2. Develop a cohesive artist identity where all elements work together
3. Ensure the artist has distinctive characteristics that make them stand out
4. Make the artist authentic and believable within their genre
5. Consider how this artist would evolve and grow over time

The final artist profile should be detailed, cohesive, and ready for multi-agent LLM communication in the artist creation process.
"""
        
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "genre": genre,
                "style": style,
                "persona": persona,
                "target_audience": target_audience,
                "visual_elements": visual_elements,
                "genre_elements": genre_elements,
                "timestamp": self._get_timestamp()
            }
        }
    
    def generate_artist_name_prompt(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a focused prompt specifically for creating an artist name.
        
        Args:
            params: Dictionary containing artist parameters such as:
                - genre: Musical genre
                - style: Artist's stylistic description
                - persona: Personality traits
                
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(f"Generating artist name prompt for genre: {params.get('genre', 'Unknown')}")
        
        # Extract key parameters with defaults
        genre = params.get('genre', 'Electronic')
        style = params.get('style', 'Unique, Distinctive')
        persona = params.get('persona', 'Authentic')
        
        # Get genre-specific elements
        genre_elements = self._extract_genre_elements(genre)
        
        # Build the name generation prompt
        prompt = f"""# Artist Name Generation

Create a unique, memorable name for a new {genre} music artist with a {style} style and {persona} persona.

## Genre Context
- **Primary Genre:** {genre}
- **Genre Mood:** {', '.join(random.sample(genre_elements["mood"], min(2, len(genre_elements["mood"]))))}
- **Genre Themes:** {', '.join(random.sample(genre_elements["themes"], min(2, len(genre_elements["themes"]))))}

## Style Guidelines
The name should:
- Reflect the {style} style and {persona} persona
- Be memorable and distinctive
- Work well for music platforms and social media
- Be easy to pronounce but unique enough to be searchable
- Capture the essence of the artist's musical identity

## Output Format
Generate 5 potential artist names with a brief explanation of each name's meaning or relevance to the specified genre and style.
"""
        
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "genre": genre,
                "style": style,
                "persona": persona,
                "timestamp": self._get_timestamp()
            }
        }
    
    def generate_visual_identity_prompt(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a focused prompt specifically for creating an artist's visual identity.
        
        Args:
            params: Dictionary containing artist parameters such as:
                - name: Artist name (optional)
                - genre: Musical genre
                - style: Artist's stylistic description
                - visual_identity: Additional visual elements (optional)
                
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(f"Generating visual identity prompt for genre: {params.get('genre', 'Unknown')}")
        
        # Extract key parameters with defaults
        name = params.get('name', 'the artist')
        genre = params.get('genre', 'Electronic')
        style = params.get('style', 'Unique, Distinctive')
        visual_identity = params.get('visual_identity', '')
        
        # Get genre-specific visual elements
        genre_elements = self._extract_genre_elements(genre)
        visual_aesthetic = genre_elements.get("visual_aesthetic", [])
        
        # Get style-based visual elements
        visual_elements = self._extract_visual_elements(style)
        
        # Build the visual identity prompt
        prompt = f"""# Visual Identity Creation

Develop a comprehensive visual identity for {name}, a {genre} artist with a {style} style.

## Core Visual Elements
- **Color Palette:** {', '.join(random.sample(visual_elements["colors"], min(3, len(visual_elements["colors"]))))}
- **Key Imagery/Symbols:** {', '.join(random.sample(visual_elements["imagery"], min(3, len(visual_elements["imagery"]))))}
- **Composition Style:** {', '.join(random.sample(visual_elements["composition"], min(2, len(visual_elements["composition"]))))}
- **Textures:** {', '.join(random.sample(visual_elements["textures"], min(2, len(visual_elements["textures"]))))}
"""

        # Add genre-specific visual aesthetic if available
        if visual_aesthetic:
            prompt += f"- **Genre Aesthetic:** {', '.join(random.sample(visual_aesthetic, min(3, len(visual_aesthetic))))}\n"
        
        # Add additional visual identity elements if provided
        if visual_identity:
            prompt += f"- **Additional Elements:** {visual_identity}\n"
        
        # Add detailed requirements
        prompt += """
## Visual Identity Components
1. **Artist Logo/Symbol:** Design a distinctive logo or symbol that represents the artist
2. **Typography:** Describe the font style and text treatment for the artist's name
3. **Cover Art Style:** Define the consistent visual approach for album/single covers
4. **Social Media Aesthetic:** Establish a cohesive look for social media presence
5. **Performance/Video Visual Style:** Describe the visual approach for performances or videos
6. **Photography Style:** Define the photographic treatment for artist images

## Output Format
Provide a detailed visual identity guide that could be used by designers to create consistent visual assets for the artist.
"""
        
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "name": name,
                "genre": genre,
                "style": style,
                "visual_elements": visual_elements,
                "timestamp": self._get_timestamp()
            }
        }
    
    def generate_backstory_prompt(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a focused prompt specifically for creating an artist's backstory.
        
        Args:
            params: Dictionary containing artist parameters such as:
                - name: Artist name (optional)
                - genre: Musical genre
                - style: Artist's stylistic description
                - persona: Personality traits
                - themes: Themes or values represented (optional)
                
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(f"Generating backstory prompt for genre: {params.get('genre', 'Unknown')}")
        
        # Extract key parameters with defaults
        name = params.get('name', 'the artist')
        genre = params.get('genre', 'Electronic')
        style = params.get('style', 'Unique, Distinctive')
        persona = params.get('persona', 'Authentic')
        themes = params.get('themes', '')
        
        # Get genre-specific elements
        genre_elements = self._extract_genre_elements(genre)
        
        # Determine themes if not provided
        if not themes:
            themes = ", ".join(random.sample(genre_elements["themes"], 
                                            min(3, len(genre_elements["themes"]))))
        
        # Get expanded persona traits
        persona_traits = self._extract_persona_traits(persona)
        
        # Build the backstory prompt
        prompt = f"""# Artist Backstory Creation

Develop a compelling backstory for {name}, a {genre} artist with a {style} style.

## Artist Characteristics
- **Persona:** 
{chr(10).join(f"  - {trait}" for trait in persona_traits)}
- **Musical Genre:** {genre}
- **Style:** {style}
- **Key Themes:** {themes}

## Backstory Elements to Develop
1. **Origin Story:** Where and how the artist began their musical journey
2. **Influences:** Key musical and non-musical influences that shaped their sound
3. **Evolution:** How their sound and artistic approach has evolved over time
4. **Philosophy:** Their artistic philosophy and approach to music creation
5. **Significant Moments:** Key events that defined their artistic direction
6. **Challenges:** Obstacles they've overcome in their artistic journey
7. **Vision:** Their artistic vision and what they aim to achieve with their music

## Guidelines
- The backstory should feel authentic and align with the {genre} genre
- Incorporate elements that reflect their {style} style
- Include details that explain why they create the type of music they do
- Develop a narrative that fans would find compelling and relatable
- Ensure the backstory supports and enhances the artist's musical identity

## Output Format
Create a detailed backstory narrative that could be used for artist bios, interviews, and promotional materials.
"""
        
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "name": name,
                "genre": genre,
                "style": style,
                "persona": persona,
                "themes": themes,
                "timestamp": self._get_timestamp()
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


# Factory function to create an artist prompt generator
def create_artist_prompt_generator(
    template_variety: int = 3,
    seed: Optional[int] = None
) -> ArtistPromptGenerator:
    """
    Factory function to create an artist prompt generator.
    
    Args:
        template_variety: Number of template variations to use
        seed: Optional random seed for reproducible generation
        
    Returns:
        An artist prompt generator instance
    """
    return ArtistPromptGenerator(
        template_variety=template_variety,
        seed=seed
    )


# Convenience function for generating artist prompts
def generate_artist_prompt(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive prompt for creating an AI artist based on input parameters.
    
    This is a convenience function that creates a generator instance and calls
    generate_artist_prompt on it.
    
    Args:
        params: Dictionary containing artist parameters such as:
            - genre: Musical genre (e.g., "Dark Trap", "Phonk")
            - style: Artist's stylistic description (e.g., "Mysterious, Cold")
            - persona: Personality traits (e.g., "mysterious, energetic, soft")
            - target_audience: Target demographic (optional)
            - visual_identity: Visual style hints (optional)
            - lyrics_language: Language for lyrics (optional)
            - themes: Themes or values represented (optional)
            - lifestyle: Lifestyle/attitude hints (optional)
            - special_notes: Special notes for AI enhancement (optional)
            
    Returns:
        Dictionary containing the generated prompt and metadata
    """
    generator = create_artist_prompt_generator()
    return generator.generate_artist_prompt(params)


# Example usage
if __name__ == "__main__":
    # Create a generator
    generator = create_artist_prompt_generator(seed=42)
    
    # Example parameters
    example_params = {
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "persona": "mysterious, energetic",
        "target_audience": "Young adults, night owls",
        "visual_identity": "Always wears a black hood and mask",
        "lyrics_language": "English",
        "themes": "Urban isolation, night life, inner struggles",
        "lifestyle": "Urban night life, digital nomad",
        "special_notes": "Should have a distinctive vocal processing effect"
    }
    
    # Generate a full artist prompt
    result = generator.generate_artist_prompt(example_params)
    
    # Print the result
    print("ARTIST PROMPT:")
    print(result["prompt"])
    
    # Generate a name prompt
    name_result = generator.generate_artist_name_prompt(example_params)
    
    # Print the name prompt
    print("\nNAME PROMPT:")
    print(name_result["prompt"])
