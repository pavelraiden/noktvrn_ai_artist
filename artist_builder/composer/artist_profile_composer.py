"""
Artist Profile Composer Module

This module provides functionality for assembling complete artist profiles
based on validated prompts, preparing them for storage and further use.
"""

import re
import json
import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("artist_profile_composer")


class ArtistProfileComposer:
    """
    Assembles complete artist profiles based on validated prompts.
    
    This class extracts information from prompts to create structured artist
    profiles with name, genre, vibe, backstory, style, and visual description.
    """
    
    def __init__(
        self,
        default_genre: str = "Electronic",
        name_generator: Optional[callable] = None,
        enhance_profiles: bool = True
    ):
        """
        Initialize a new artist profile composer.
        
        Args:
            default_genre: Default genre if none is extracted
            name_generator: Function to generate artist names (uses mock if None)
            enhance_profiles: Whether to enhance profiles with additional details
        """
        self.default_genre = default_genre
        self.name_generator = name_generator or self._mock_name_generator
        self.enhance_profiles = enhance_profiles
        
        # Initialize genre keywords for extraction
        self.genre_keywords = {
            "trap": ["trap", "808", "hi-hat", "dark trap", "mumble"],
            "electronic": ["electronic", "edm", "synth", "techno", "house", "dubstep"],
            "hip hop": ["hip hop", "hip-hop", "rap", "beats", "rhymes"],
            "pop": ["pop", "catchy", "mainstream", "chart", "radio"],
            "rock": ["rock", "guitar", "band", "alternative", "indie"],
            "r&b": ["r&b", "rnb", "soul", "rhythm and blues", "smooth"],
            "jazz": ["jazz", "improvisation", "saxophone", "trumpet", "swing"],
            "classical": ["classical", "orchestra", "symphony", "composer", "piano"],
            "country": ["country", "folk", "acoustic", "rural", "western"],
            "metal": ["metal", "heavy", "thrash", "death metal", "hardcore"]
        }
        
        # Initialize vibe keywords for extraction
        self.vibe_keywords = {
            "mysterious": ["mysterious", "enigmatic", "cryptic", "secretive", "unknown"],
            "energetic": ["energetic", "lively", "dynamic", "vibrant", "upbeat"],
            "melancholic": ["melancholic", "sad", "somber", "gloomy", "depressive"],
            "aggressive": ["aggressive", "intense", "fierce", "powerful", "strong"],
            "chill": ["chill", "relaxed", "calm", "laid-back", "mellow"],
            "futuristic": ["futuristic", "sci-fi", "technological", "advanced", "cyber"],
            "nostalgic": ["nostalgic", "retro", "vintage", "throwback", "classic"],
            "spiritual": ["spiritual", "mystical", "transcendent", "ethereal", "cosmic"],
            "romantic": ["romantic", "passionate", "sensual", "intimate", "loving"],
            "rebellious": ["rebellious", "defiant", "revolutionary", "anti-establishment", "punk"]
        }
        
        logger.info("Initialized artist profile composer")
    
    def compose_profile(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose a complete artist profile based on a prompt.
        
        Args:
            prompt: The validated artist prompt
            session_id: The ID of the session (for tracking)
            metadata: Additional metadata for the profile
            
        Returns:
            A complete artist profile
        """
        # Extract components from the prompt
        components = self.extract_components(prompt)
        
        # Generate a name if not extracted
        if not components.get("name"):
            components["name"] = self.name_generator(components)
        
        # Enhance the profile if enabled
        if self.enhance_profiles:
            components = self.enhance_profile(components)
        
        # Create the profile
        profile = {
            "id": f"artist_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
            "name": components["name"],
            "genre": components["genre"],
            "vibe": components["vibe"],
            "backstory": components["backstory"],
            "style": components["style"],
            "visual": components["visual"],
            "voice": components["voice"],
            "created_at": datetime.now().isoformat(),
            "source_prompt": prompt,
            "session_id": session_id,
            "metadata": metadata or {}
        }
        
        # Format for storage
        formatted_profile = self.format_for_storage(profile)
        
        logger.info(f"Composed profile for artist '{profile['name']}' with genre '{profile['genre']}'")
        return formatted_profile
    
    def extract_components(self, prompt: str) -> Dict[str, Any]:
        """
        Extract profile components from a prompt.
        
        Args:
            prompt: The artist prompt
            
        Returns:
            A dictionary of extracted components
        """
        prompt_lower = prompt.lower()
        
        # Initialize components with default values
        components = {
            "name": self._extract_name(prompt),
            "genre": self._extract_genre(prompt_lower),
            "vibe": self._extract_vibe(prompt_lower),
            "backstory": "",
            "style": "",
            "visual": "",
            "voice": ""
        }
        
        # Extract backstory (sentences containing background, story, history, etc.)
        backstory_sentences = []
        for sentence in re.split(r'[.!?]+', prompt):
            sentence = sentence.strip()
            if sentence and any(keyword in sentence.lower() for keyword in ["background", "story", "history", "life", "journey", "past"]):
                backstory_sentences.append(sentence)
        
        if backstory_sentences:
            components["backstory"] = ". ".join(backstory_sentences) + "."
        else:
            # If no explicit backstory, use the first 1-2 sentences as backstory
            sentences = [s.strip() for s in re.split(r'[.!?]+', prompt) if s.strip()]
            if sentences:
                components["backstory"] = ". ".join(sentences[:min(2, len(sentences))]) + "."
        
        # Extract style (sentences containing style, music, sound, etc.)
        style_sentences = []
        for sentence in re.split(r'[.!?]+', prompt):
            sentence = sentence.strip()
            if sentence and any(keyword in sentence.lower() for keyword in ["style", "music", "sound", "track", "beat", "melody", "song"]):
                style_sentences.append(sentence)
        
        if style_sentences:
            components["style"] = ". ".join(style_sentences) + "."
        
        # Extract visual description (sentences containing appearance, looks, wears, etc.)
        visual_sentences = []
        for sentence in re.split(r'[.!?]+', prompt):
            sentence = sentence.strip()
            if sentence and any(keyword in sentence.lower() for keyword in ["appearance", "looks", "wears", "dressed", "visual", "image", "mask", "hood", "face"]):
                visual_sentences.append(sentence)
        
        if visual_sentences:
            components["visual"] = ". ".join(visual_sentences) + "."
        
        # Extract voice description (sentences containing voice, vocal, speaks, etc.)
        voice_sentences = []
        for sentence in re.split(r'[.!?]+', prompt):
            sentence = sentence.strip()
            if sentence and any(keyword in sentence.lower() for keyword in ["voice", "vocal", "speaks", "sound", "tone", "raspy", "deep", "high"]):
                voice_sentences.append(sentence)
        
        if voice_sentences:
            components["voice"] = ". ".join(voice_sentences) + "."
        
        return components
    
    def enhance_profile(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a profile with additional details.
        
        Args:
            components: The extracted profile components
            
        Returns:
            Enhanced profile components
        """
        enhanced = components.copy()
        
        # Enhance backstory if missing or too short
        if not enhanced["backstory"] or len(enhanced["backstory"]) < 50:
            genre = enhanced["genre"]
            vibe = enhanced["vibe"]
            
            backstory_templates = [
                f"A rising {genre} artist known for their {vibe} sound. They emerged from the underground scene and quickly gained a following through social media and word of mouth.",
                f"Born into a musical family, this {genre} artist developed their {vibe} style through years of experimentation and personal experiences.",
                f"After years of producing tracks in their bedroom studio, this {genre} artist broke through with their distinctive {vibe} sound that resonated with listeners.",
                f"Influenced by the {genre} legends that came before them, this artist brings a fresh {vibe} perspective to the genre, blending traditional elements with modern production."
            ]
            
            enhanced["backstory"] = random.choice(backstory_templates)
        
        # Enhance style if missing or too short
        if not enhanced["style"] or len(enhanced["style"]) < 50:
            genre = enhanced["genre"]
            vibe = enhanced["vibe"]
            
            style_templates = [
                f"Their music combines {vibe} atmospheres with hard-hitting {genre} beats, creating a unique sound that stands out in the current scene.",
                f"Known for blending traditional {genre} elements with {vibe} influences, resulting in a distinctive sound that defies easy categorization.",
                f"Their production style features intricate {genre} rhythms layered with {vibe} melodies and textures, creating depth and complexity.",
                f"Their tracks are characterized by {vibe} themes and innovative {genre} production techniques, pushing the boundaries of the genre."
            ]
            
            enhanced["style"] = random.choice(style_templates)
        
        # Enhance visual if missing or too short
        if not enhanced["visual"] or len(enhanced["visual"]) < 50:
            vibe = enhanced["vibe"]
            
            visual_templates = [
                f"Their visual aesthetic reflects their {vibe} sound, often appearing in carefully curated outfits that enhance their artistic persona.",
                f"Their image is as {vibe} as their music, with a distinctive visual style that has become part of their brand identity.",
                f"They maintain a {vibe} visual presence across all platforms, with consistent imagery that reinforces their artistic vision.",
                f"Their {vibe} appearance is an integral part of their artistic expression, complementing the themes in their music."
            ]
            
            enhanced["visual"] = random.choice(visual_templates)
        
        # Enhance voice if missing or too short
        if not enhanced["voice"] or len(enhanced["voice"]) < 50:
            vibe = enhanced["vibe"]
            
            voice_templates = [
                f"Their vocal delivery is distinctly {vibe}, with a tone that perfectly complements their production style.",
                f"Their voice carries a {vibe} quality that has become their signature sound, instantly recognizable to fans.",
                f"Their {vibe} vocal style adds depth to their tracks, conveying emotion that resonates with listeners.",
                f"Their voice has a {vibe} character that stands out in the current music landscape, adding a unique dimension to their work."
            ]
            
            enhanced["voice"] = random.choice(voice_templates)
        
        return enhanced
    
    def format_for_storage(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a profile for storage and further use.
        
        Args:
            profile: The artist profile
            
        Returns:
            Formatted profile ready for storage
        """
        # Create a copy to avoid modifying the original
        formatted = profile.copy()
        
        # Add additional fields for storage and processing
        formatted["version"] = "1.0"
        formatted["last_updated"] = datetime.now().isoformat()
        formatted["status"] = "active"
        
        # Add a summary for quick reference
        formatted["summary"] = self._generate_summary(profile)
        
        # Add tags for searchability
        formatted["tags"] = self._generate_tags(profile)
        
        return formatted
    
    def _extract_name(self, prompt: str) -> str:
        """
        Extract artist name from prompt if present.
        
        Args:
            prompt: The artist prompt
            
        Returns:
            Extracted name or empty string
        """
        # Look for name patterns
        name_patterns = [
            r'named "([^"]+)"',
            r'called "([^"]+)"',
            r'name is "([^"]+)"',
            r'artist "([^"]+)"',
            r'artist named "([^"]+)"',
            r'artist called "([^"]+)"'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_genre(self, prompt_lower: str) -> str:
        """
        Extract genre from prompt.
        
        Args:
            prompt_lower: The lowercase artist prompt
            
        Returns:
            Extracted genre or default genre
        """
        # Check for explicit genre mentions
        for genre, keywords in self.genre_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return genre.title()
        
        return self.default_genre
    
    def _extract_vibe(self, prompt_lower: str) -> str:
        """
        Extract vibe from prompt.
        
        Args:
            prompt_lower: The lowercase artist prompt
            
        Returns:
            Extracted vibe or default vibe
        """
        vibes = []
        
        # Check for explicit vibe mentions
        for vibe, keywords in self.vibe_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    vibes.append(vibe)
                    break  # Only count each vibe once
        
        if vibes:
            return ", ".join(vibe.title() for vibe in vibes[:3])  # Limit to top 3 vibes
        
        # Default vibe based on genre
        genre = self._extract_genre(prompt_lower)
        default_vibes = {
            "Trap": "Dark, Intense",
            "Electronic": "Energetic, Futuristic",
            "Hip Hop": "Confident, Urban",
            "Pop": "Upbeat, Catchy",
            "Rock": "Rebellious, Passionate",
            "R&B": "Smooth, Sensual",
            "Jazz": "Sophisticated, Improvisational",
            "Classical": "Elegant, Emotional",
            "Country": "Authentic, Storytelling",
            "Metal": "Aggressive, Powerful"
        }
        
        return default_vibes.get(genre, "Unique, Creative")
    
    def _mock_name_generator(self, components: Dict[str, Any]) -> str:
        """
        Generate a mock artist name based on profile components.
        
        Args:
            components: The profile components
            
        Returns:
            Generated artist name
        """
        # Get genre and vibe for context
        genre = components["genre"].lower()
        vibe = components["vibe"].lower()
        
        # Name patterns based on genre
        genre_prefixes = {
            "trap": ["lil", "young", "yung", "big", "king", "queen", "dr", "mc"],
            "electronic": ["dj", "producer", "project", "system", "digital", "cyber"],
            "hip hop": ["mc", "dj", "the", "sir", "lady", "grand"],
            "pop": ["", "the", "miss", "mister", "baby"],
            "rock": ["the", "", "captain", "dr", "saint"],
            "r&b": ["", "the", "miss", "mr", "lady", "soul"],
            "jazz": ["", "the", "professor", "maestro", "quartet"],
            "classical": ["maestro", "virtuoso", "professor", "dr", ""],
            "country": ["", "the", "ol'", "little", "big"],
            "metal": ["", "lord", "dark", "death", "black", "blood"]
        }
        
        # Name elements based on vibe
        vibe_elements = {
            "mysterious": ["shadow", "ghost", "enigma", "mystery", "secret", "unknown", "cipher", "phantom"],
            "energetic": ["spark", "volt", "energy", "power", "force", "rush", "surge", "blast"],
            "melancholic": ["tear", "sorrow", "blue", "gray", "rain", "cloud", "mist", "shade"],
            "aggressive": ["rage", "fury", "anger", "beast", "savage", "fierce", "brutal", "vicious"],
            "chill": ["wave", "breeze", "calm", "cool", "smooth", "easy", "flow", "drift"],
            "futuristic": ["cyber", "tech", "future", "neon", "digital", "virtual", "binary", "quantum"],
            "nostalgic": ["retro", "vintage", "classic", "old", "memory", "past", "golden", "legacy"],
            "spiritual": ["soul", "spirit", "divine", "sacred", "holy", "mystic", "ethereal", "astral"],
            "romantic": ["heart", "love", "passion", "desire", "romance", "kiss", "embrace", "touch"],
            "rebellious": ["rebel", "riot", "anarchy", "chaos", "wild", "free", "resist", "defy"]
        }
        
        # Get relevant prefixes and elements
        prefixes = genre_prefixes.get(genre, ["", "the", "dj"])
        
        # Extract vibe keywords
        vibe_keywords = []
        for v in vibe.split(","):
            v = v.strip().lower()
            if v in vibe_elements:
                vibe_keywords.extend(vibe_elements[v])
        
        # If no matching vibes, use a default set
        if not vibe_keywords:
            vibe_keywords = ["star", "beat", "sound", "track", "note", "rhythm", "melody", "harmony"]
        
        # Generate name components
        prefix = random.choice(prefixes)
        element = random.choice(vibe_keywords)
        
        # Add a suffix sometimes
        suffixes = ["", "", "", "x", "z", "beats", "sound", "official", "music", str(random.randint(1, 999))]
        suffix = random.choice(suffixes)
        
        # Format the name
        if prefix:
            name = f"{prefix} {element}"
        else:
            name = element
            
        if suffix:
            if suffix.isdigit():
                name = f"{name}{suffix}"
            else:
                name = f"{name} {suffix}"
        
        # Capitalize appropriately
        name_parts = name.split()
        name = " ".join(part.capitalize() for part in name_parts)
        
        # Sometimes stylize with special characters
        if random.random() < 0.3:
            stylizations = [
                lambda n: n.replace("a", "4").replace("e", "3").replace("i", "1").replace("o", "0"),
                lambda n: n.replace(" ", ""),
                lambda n: n.replace("s", "$").replace("a", "@"),
                lambda n: n.lower(),
                lambda n: n.upper(),
                lambda n: "".join(c for c in n if c.isalnum() or c.isspace())
            ]
            name = random.choice(stylizations)(name)
        
        return name
    
    def _generate_summary(self, profile: Dict[str, Any]) -> str:
        """
        Generate a summary of the artist profile.
        
        Args:
            profile: The artist profile
            
        Returns:
            A summary string
        """
        return f"{profile['name']} is a {profile['genre']} artist with a {profile['vibe']} vibe."
    
    def _generate_tags(self, profile: Dict[str, Any]) -> List[str]:
        """
        Generate tags for the artist profile.
        
        Args:
            profile: The artist profile
            
        Returns:
            A list of tags
        """
        tags = []
        
        # Add genre tags
        genre = profile["genre"].lower()
        tags.append(genre)
        
        # Add genre-specific tags
        genre_tags = {
            "trap": ["808", "beats", "dark", "bass"],
            "electronic": ["edm", "synth", "beats", "dance"],
            "hip hop": ["rap", "beats", "rhymes", "flow"],
            "pop": ["catchy", "mainstream", "radio", "hits"],
            "rock": ["guitar", "band", "alternative", "indie"],
            "r&b": ["soul", "rhythm", "blues", "smooth"],
            "jazz": ["improvisation", "saxophone", "trumpet", "swing"],
            "classical": ["orchestra", "symphony", "composer", "piano"],
            "country": ["folk", "acoustic", "rural", "western"],
            "metal": ["heavy", "thrash", "hardcore", "intense"]
        }
        
        if genre in genre_tags:
            tags.extend(genre_tags[genre])
        
        # Add vibe tags
        for vibe in profile["vibe"].lower().split(","):
            vibe = vibe.strip()
            if vibe:
                tags.append(vibe)
        
        # Add name as a tag
        tags.append(profile["name"].lower().replace(" ", ""))
        
        # Remove duplicates and return
        return list(set(tags))


# Example usage
if __name__ == "__main__":
    # Create a composer
    composer = ArtistProfileComposer()
    
    # Example prompt
    example_prompt = """
    A mysterious dark trap artist who thrives in the urban night scene. 
    Their music combines haunting melodies with heavy bass, creating a unique atmospheric sound.
    Always seen wearing a black hood and mask, their identity remains hidden, adding to their enigmatic presence.
    Their deep, raspy voice delivers lyrics about city life and personal struggles, resonating with listeners
    who connect with the authentic emotion in their music.
    """
    
    # Compose a profile
    profile = composer.compose_profile(example_prompt, session_id="test_session_123")
    
    # Print the profile
    print(json.dumps(profile, indent=2))
