"""
Track Prompt Generator Module

This module provides a modular and flexible system for generating detailed prompts for AI-written songs
based on an artist's style, mood, and audience. It creates well-structured, detailed prompts suitable
for LLM songwriters (GPT, Claude, Grok, etc).

The module generates prompts covering various aspects of a track including:
- Desired song mood and emotion
- Tempo
- Genre and subgenres
- Special lyrical themes
- Key musical cues
- Structure indications (drops, transitions, bass-heavy sections)
- Language for lyrics
- Target audience emotion
- Stylistic notes
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
logger = logging.getLogger("track_prompt_generator")

# Try to load environment variables if .env exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.info("dotenv not installed, skipping environment variable loading")


class TrackPromptGenerator:
    """
    Generates detailed prompts for AI-written songs based on artist profiles.
    
    This class provides methods to generate well-structured prompts covering all aspects
    of a track, suitable for LLM songwriters (GPT, Claude, Grok, etc).
    """
    
    def __init__(self, template_variety: int = 3, seed: Optional[int] = None):
        """
        Initialize the track prompt generator.
        
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
        
        # Load mood database
        self.mood_elements = self._load_mood_database()
        
        # Load tempo database
        self.tempo_elements = self._load_tempo_database()
        
        logger.info("Initialized TrackPromptGenerator")
    
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
                "structure": ["bass drops", "beat switches", "vocal hooks", "ad-libs"],
                "audience_emotion": ["confidence", "intensity", "swagger", "determination"]
            },
            "dark trap": {
                "instruments": ["distorted 808s", "atmospheric pads", "minor keys", "deep bass"],
                "tempo_range": (110, 150),
                "themes": ["darkness", "inner demons", "night life", "isolation"],
                "mood": ["ominous", "mysterious", "haunting", "melancholic"],
                "production": ["reverb", "echo", "distortion", "ambient sounds"],
                "structure": ["atmospheric intros", "heavy drops", "dark breakdowns", "eerie outros"],
                "audience_emotion": ["introspection", "darkness", "emotional release", "night drive vibes"]
            },
            "phonk": {
                "instruments": ["cowbell", "memphis drums", "vinyl crackle", "pitched vocals"],
                "tempo_range": (130, 160),
                "themes": ["nostalgia", "retro", "driving", "night cruising"],
                "mood": ["eerie", "energetic", "hypnotic", "aggressive"],
                "production": ["chopped samples", "lo-fi elements", "heavy sidechaining"],
                "structure": ["sample intros", "cowbell patterns", "vocal chops", "beat switches"],
                "audience_emotion": ["night driving", "adrenaline rush", "nostalgic energy", "workout intensity"]
            },
            "lofi": {
                "instruments": ["mellow piano", "jazz samples", "vinyl crackle", "soft drums"],
                "tempo_range": (70, 90),
                "themes": ["relaxation", "study", "nostalgia", "introspection"],
                "mood": ["calm", "melancholic", "peaceful", "warm"],
                "production": ["sample-based", "vinyl effects", "subtle imperfections"],
                "structure": ["smooth loops", "gentle transitions", "ambient sections", "subtle variations"],
                "audience_emotion": ["relaxation", "focus", "gentle nostalgia", "rainy day vibes"]
            },
            "edm": {
                "instruments": ["synthesizers", "drum machines", "vocal chops", "risers"],
                "tempo_range": (120, 150),
                "themes": ["celebration", "energy", "euphoria", "freedom"],
                "mood": ["uplifting", "energetic", "exciting", "positive"],
                "production": ["drops", "buildups", "layered synths", "clean mixing"],
                "structure": ["intro", "buildup", "drop", "breakdown", "second buildup", "final drop", "outro"],
                "audience_emotion": ["euphoria", "dancing energy", "festival excitement", "hands in the air moments"]
            },
            "hip hop": {
                "instruments": ["drum breaks", "samples", "bass lines", "scratching"],
                "tempo_range": (85, 110),
                "themes": ["urban life", "social commentary", "personal growth", "storytelling"],
                "mood": ["confident", "reflective", "assertive", "authentic"],
                "production": ["sample-based", "boom bap", "layered vocals"],
                "structure": ["intro", "verses", "hooks", "bridge", "outro"],
                "audience_emotion": ["head nodding", "lyrical appreciation", "street confidence", "cultural connection"]
            },
            "ambient": {
                "instruments": ["synthesizer pads", "field recordings", "processed sounds", "drones"],
                "tempo_range": (60, 80),
                "themes": ["nature", "space", "meditation", "transcendence"],
                "mood": ["atmospheric", "ethereal", "spacious", "contemplative"],
                "production": ["reverb", "delay", "textural layers", "minimal percussion"],
                "structure": ["gradual evolution", "textural shifts", "atmospheric development", "subtle movements"],
                "audience_emotion": ["meditation", "deep relaxation", "mental journey", "background immersion"]
            },
            "techno": {
                "instruments": ["analog synths", "drum machines", "acid lines", "industrial sounds"],
                "tempo_range": (120, 140),
                "themes": ["futurism", "technology", "machine aesthetics", "hypnotic states"],
                "mood": ["driving", "hypnotic", "mechanical", "intense"],
                "production": ["repetitive patterns", "layered percussion", "minimal elements"],
                "structure": ["long intros", "gradual builds", "percussion drops", "hypnotic loops"],
                "audience_emotion": ["trance-like dancing", "club immersion", "rhythmic hypnosis", "body movement"]
            },
            "pop": {
                "instruments": ["polished vocals", "synthesizers", "acoustic elements", "clean drums"],
                "tempo_range": (90, 120),
                "themes": ["love", "relationships", "self-empowerment", "celebration"],
                "mood": ["catchy", "upbeat", "emotional", "accessible"],
                "production": ["vocal-forward", "radio-ready", "hook-focused"],
                "structure": ["intro", "verse", "pre-chorus", "chorus", "verse", "pre-chorus", "chorus", "bridge", "final chorus"],
                "audience_emotion": ["singing along", "emotional connection", "relatability", "memorability"]
            },
            "indie": {
                "instruments": ["guitars", "organic drums", "analog synths", "raw vocals"],
                "tempo_range": (80, 130),
                "themes": ["authenticity", "personal experiences", "relationships", "social observations"],
                "mood": ["intimate", "thoughtful", "emotive", "genuine"],
                "production": ["organic", "less processed", "room sound", "imperfections"],
                "structure": ["verse", "chorus", "verse", "chorus", "bridge", "final chorus"],
                "audience_emotion": ["emotional resonance", "authenticity appreciation", "lyrical connection", "indie credibility"]
            }
        }
        
        # Check for environment variable with custom genre database path
        custom_db_path = os.getenv("TRACK_GENRE_DB_PATH")
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
    
    def _load_mood_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the mood database with elements for different emotional states.
        
        Returns:
            Dictionary mapping mood names to their elements
        """
        # Mood-specific elements dictionary
        mood_elements = {
            "melancholic": {
                "description": "A sad, reflective, or wistful state of mind",
                "musical_elements": ["minor keys", "slow tempo", "emotional vocals", "sparse instrumentation"],
                "lyrical_themes": ["loss", "nostalgia", "regret", "longing", "memories"],
                "production_techniques": ["reverb", "ambient sounds", "acoustic elements", "space between notes"],
                "audience_response": ["introspection", "emotional release", "crying in the car", "quiet reflection"]
            },
            "energetic": {
                "description": "Full of energy, enthusiasm, and dynamic power",
                "musical_elements": ["upbeat tempo", "strong percussion", "bright synths", "powerful vocals"],
                "lyrical_themes": ["motivation", "celebration", "action", "living in the moment"],
                "production_techniques": ["layered sounds", "drops", "buildups", "dynamic range"],
                "audience_response": ["dancing", "workout energy", "party atmosphere", "movement"]
            },
            "dark": {
                "description": "Ominous, mysterious, or sinister in tone",
                "musical_elements": ["minor keys", "deep bass", "atmospheric sounds", "tense progressions"],
                "lyrical_themes": ["struggle", "inner demons", "night", "conflict", "darkness"],
                "production_techniques": ["distortion", "reverb", "low-end focus", "sparse arrangements"],
                "audience_response": ["intensity", "head nodding", "emotional heaviness", "night vibes"]
            },
            "uplifting": {
                "description": "Inspiring, encouraging, or emotionally elevating",
                "musical_elements": ["major keys", "bright sounds", "upbeat rhythm", "soaring melodies"],
                "lyrical_themes": ["hope", "overcoming", "inspiration", "positivity", "growth"],
                "production_techniques": ["layered harmonies", "crescendos", "bright mixing", "clarity"],
                "audience_response": ["emotional uplift", "motivation", "positive energy", "inspiration"]
            },
            "nostalgic": {
                "description": "Evoking fond memories of the past",
                "musical_elements": ["vintage sounds", "familiar progressions", "warm tones", "retro instruments"],
                "lyrical_themes": ["memories", "childhood", "past eras", "simpler times", "reflection"],
                "production_techniques": ["vinyl effects", "tape saturation", "period-specific sounds", "retro processing"],
                "audience_response": ["reminiscing", "emotional connection", "comfort", "time travel feeling"]
            },
            "aggressive": {
                "description": "Forceful, intense, and powerful in delivery",
                "musical_elements": ["distorted sounds", "heavy percussion", "shouted vocals", "intense dynamics"],
                "lyrical_themes": ["conflict", "power", "defiance", "struggle", "intensity"],
                "production_techniques": ["distortion", "compression", "layered intensity", "dynamic impact"],
                "audience_response": ["rage workout", "mosh pit energy", "aggressive head nodding", "intensity"]
            },
            "chill": {
                "description": "Relaxed, laid-back, and easy-going",
                "musical_elements": ["mid-tempo beats", "smooth sounds", "relaxed vocals", "gentle progressions"],
                "lyrical_themes": ["relaxation", "good vibes", "taking it easy", "peace of mind"],
                "production_techniques": ["space in the mix", "smooth transitions", "warm tones", "balanced elements"],
                "audience_response": ["relaxation", "head nodding", "easy listening", "background enjoyment"]
            },
            "ethereal": {
                "description": "Delicate, light, and otherworldly",
                "musical_elements": ["ambient sounds", "floating melodies", "gentle textures", "atmospheric layers"],
                "lyrical_themes": ["dreams", "spirituality", "transcendence", "nature", "cosmos"],
                "production_techniques": ["reverb", "delay", "layered textures", "spatial effects"],
                "audience_response": ["dreamy state", "floating feeling", "meditative experience", "transcendence"]
            }
        }
        
        # Check for environment variable with custom mood database path
        custom_db_path = os.getenv("TRACK_MOOD_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, 'r') as f:
                    custom_moods = json.load(f)
                    # Merge with default moods, with custom moods taking precedence
                    mood_elements.update(custom_moods)
                    logger.info(f"Loaded custom mood database from {custom_db_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom mood database: {e}")
        
        return mood_elements
    
    def _load_tempo_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the tempo database with elements for different tempo ranges.
        
        Returns:
            Dictionary mapping tempo categories to their elements
        """
        # Tempo-specific elements dictionary
        tempo_elements = {
            "slow": {
                "bpm_range": (60, 90),
                "description": "Relaxed, deliberate pace with space between elements",
                "suitable_moods": ["melancholic", "chill", "ethereal", "nostalgic"],
                "musical_characteristics": ["longer notes", "more space", "sustained sounds", "deliberate phrasing"],
                "production_techniques": ["reverb", "ambient space", "longer decay times", "breathing room"]
            },
            "medium": {
                "bpm_range": (90, 120),
                "description": "Moderate, balanced pace with natural movement",
                "suitable_moods": ["nostalgic", "chill", "uplifting", "dark"],
                "musical_characteristics": ["balanced rhythms", "moderate energy", "versatile phrasing", "natural flow"],
                "production_techniques": ["balanced mix", "moderate dynamics", "versatile approaches", "natural feel"]
            },
            "fast": {
                "bpm_range": (120, 180),
                "description": "Energetic, driving pace with forward momentum",
                "suitable_moods": ["energetic", "aggressive", "uplifting", "dark"],
                "musical_characteristics": ["shorter notes", "quick phrases", "rapid changes", "driving rhythms"],
                "production_techniques": ["tight timing", "sharp attacks", "quick transitions", "dynamic impact"]
            }
        }
        
        # Check for environment variable with custom tempo database path
        custom_db_path = os.getenv("TRACK_TEMPO_DB_PATH")
        if custom_db_path and os.path.exists(custom_db_path):
            try:
                with open(custom_db_path, 'r') as f:
                    custom_tempos = json.load(f)
                    # Merge with default tempos, with custom tempos taking precedence
                    tempo_elements.update(custom_tempos)
                    logger.info(f"Loaded custom tempo database from {custom_db_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom tempo database: {e}")
        
        return tempo_elements
    
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
            "structure": ["intro", "verse", "chorus", "bridge", "outro"],
            "audience_emotion": ["connection", "enjoyment", "appreciation", "engagement"]
        }
    
    def _extract_mood_elements(self, mood: str) -> Dict[str, Any]:
        """
        Extract key elements associated with a mood.
        
        Args:
            mood: Mood description
            
        Returns:
            Dictionary of mood elements
        """
        # Extract mood keywords
        mood_keywords = [word.strip().lower() for word in mood.split(",")]
        
        # Collect elements from matching moods
        combined_elements = {
            "description": [],
            "musical_elements": [],
            "lyrical_themes": [],
            "production_techniques": [],
            "audience_response": []
        }
        
        matches_found = False
        
        # Look for direct matches
        for keyword in mood_keywords:
            if keyword in self.mood_elements:
                matches_found = True
                for category in combined_elements:
                    if isinstance(self.mood_elements[keyword][category], list):
                        combined_elements[category].extend(self.mood_elements[keyword][category])
                    else:
                        combined_elements["description"].append(self.mood_elements[keyword][category])
        
        # If no direct matches, look for partial matches
        if not matches_found:
            for keyword in mood_keywords:
                for mood_name, elements in self.mood_elements.items():
                    if keyword in mood_name or mood_name in keyword:
                        for category in combined_elements:
                            if isinstance(elements[category], list):
                                combined_elements[category].extend(elements[category])
                            else:
                                combined_elements["description"].append(elements[category])
        
        # If still no matches, use default elements
        if not any(combined_elements.values()):
            return {
                "description": ["Distinctive emotional quality"],
                "musical_elements": ["appropriate instrumentation", "fitting chord progressions", "suitable melody style"],
                "lyrical_themes": ["emotion-appropriate topics", "thematically consistent content"],
                "production_techniques": ["mood-enhancing production", "appropriate effects", "suitable mix balance"],
                "audience_response": ["emotional connection", "mood-appropriate reaction"]
            }
        
        # Remove duplicates while preserving order
        for category in combined_elements:
            seen = set()
            combined_elements[category] = [x for x in combined_elements[category] 
                                          if not (x in seen or seen.add(x))]
        
        return combined_elements
    
    def _extract_tempo_elements(self, tempo: str) -> Dict[str, Any]:
        """
        Extract key elements associated with a tempo category.
        
        Args:
            tempo: Tempo category (slow, medium, fast)
            
        Returns:
            Dictionary of tempo elements
        """
        # Normalize tempo for lookup
        normalized_tempo = tempo.lower().strip()
        
        # Direct lookup
        if normalized_tempo in self.tempo_elements:
            return self.tempo_elements[normalized_tempo]
        
        # Try to match based on partial matches
        for tempo_name, elements in self.tempo_elements.items():
            if tempo_name in normalized_tempo or normalized_tempo in tempo_name:
                return elements
        
        # Default to medium if no match found
        return self.tempo_elements["medium"]
    
    def generate_track_prompt(
        self,
        artist_profile: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive prompt for creating an AI-written song based on artist profile.
        
        Args:
            artist_profile: Dictionary containing the artist's profile information including:
                - name: Artist name
                - genre: Musical genre
                - style: Artistic style
                - themes: Thematic elements
                - sound: Sound characteristics
            overrides: Optional dictionary with specific overrides for this track:
                - mood: Desired song mood and emotion
                - tempo: Tempo category (slow, medium, fast)
                - themes: Special lyrical themes
                - audience_emotion: Target audience emotion
                - stylistic_notes: Additional stylistic guidance
                
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(f"Generating track prompt for artist: {artist_profile.get('name', 'Unknown')}")
        
        # Initialize overrides if None
        if overrides is None:
            overrides = {}
        
        # Extract key elements from the profile
        artist_name = artist_profile.get('name', 'Artist')
        genre = artist_profile.get('genre', 'Electronic')
        style = artist_profile.get('style', 'Unique')
        
        # Get mood from overrides or derive from artist style
        mood = overrides.get('mood', '')
        if not mood and 'style' in artist_profile:
            mood = artist_profile.get('style', '')
        
        # Get tempo from overrides or derive from genre
        tempo_category = overrides.get('tempo', '')
        if not tempo_category:
            genre_elements = self._extract_genre_elements(genre)
            tempo_range = genre_elements.get('tempo_range', (90, 130))
            avg_tempo = (tempo_range[0] + tempo_range[1]) / 2
            
            if avg_tempo < 90:
                tempo_category = "slow"
            elif avg_tempo < 120:
                tempo_category = "medium"
            else:
                tempo_category = "fast"
        
        # Get themes from overrides or artist profile
        themes = overrides.get('themes', '')
        if not themes:
            if 'themes' in artist_profile:
                themes = artist_profile.get('themes', '')
            elif 'thematic_elements' in artist_profile and 'lyrical_themes' in artist_profile['thematic_elements']:
                themes = ', '.join(artist_profile['thematic_elements']['lyrical_themes'])
            else:
                # Use genre-based themes
                genre_elements = self._extract_genre_elements(genre)
                themes = ', '.join(random.sample(genre_elements['themes'], min(2, len(genre_elements['themes']))))
        
        # Get lyrics language from overrides or artist profile
        lyrics_language = overrides.get('lyrics_language', '')
        if not lyrics_language:
            lyrics_language = artist_profile.get('lyrics_language', 'English')
        
        # Get audience emotion from overrides or derive from genre
        audience_emotion = overrides.get('audience_emotion', '')
        if not audience_emotion:
            genre_elements = self._extract_genre_elements(genre)
            if 'audience_emotion' in genre_elements:
                audience_emotion = ', '.join(random.sample(genre_elements['audience_emotion'], 
                                                         min(2, len(genre_elements['audience_emotion']))))
            else:
                audience_emotion = "emotional connection, engagement"
        
        # Get stylistic notes from overrides
        stylistic_notes = overrides.get('stylistic_notes', '')
        
        # Extract elements from databases
        genre_elements = self._extract_genre_elements(genre)
        mood_elements = self._extract_mood_elements(mood)
        tempo_elements = self._extract_tempo_elements(tempo_category)
        
        # Build the comprehensive prompt
        prompt = f"""# Track Creation Prompt for {artist_name}

## Core Track Identity
Create a {genre} track with a {mood} mood and {tempo_category} tempo for artist {artist_name}.

## Musical Direction
- **Genre/Style:** {genre} with {style} aesthetic
- **Mood/Emotion:** {mood} - {', '.join(mood_elements['description'][:1])}
- **Tempo:** {tempo_category.capitalize()} ({tempo_elements['bpm_range'][0]}-{tempo_elements['bpm_range'][1]} BPM) - {tempo_elements['description']}
- **Key Musical Elements:** {', '.join(random.sample(genre_elements['instruments'], min(3, len(genre_elements['instruments']))))}
- **Production Style:** {', '.join(random.sample(genre_elements['production'], min(2, len(genre_elements['production']))))}

## Lyrical Direction
- **Language:** {lyrics_language}
- **Themes:** {themes}
- **Lyrical Approach:** {', '.join(random.sample(mood_elements['lyrical_themes'], min(3, len(mood_elements['lyrical_themes']))))}

## Track Structure
"""

        # Add structure based on genre
        structure_elements = genre_elements.get('structure', [])
        if structure_elements:
            structure_samples = random.sample(structure_elements, min(4, len(structure_elements)))
            prompt += f"- **Key Sections:** Include {', '.join(structure_samples)}\n"
            
            # Add typical song structure based on genre
            if genre.lower() in ["pop", "indie", "hip hop"]:
                prompt += "- **Suggested Structure:** Intro → Verse → Pre-Chorus → Chorus → Verse → Pre-Chorus → Chorus → Bridge → Final Chorus → Outro\n"
            elif genre.lower() in ["edm", "techno", "trap", "dark trap", "phonk"]:
                prompt += "- **Suggested Structure:** Intro → Build-up → Drop → Breakdown → Second Build-up → Main Drop → Outro\n"
            elif genre.lower() in ["ambient", "lofi"]:
                prompt += "- **Suggested Structure:** Atmospheric Intro → Main Theme → Subtle Variation → Gentle Evolution → Peaceful Conclusion\n"
            else:
                prompt += "- **Suggested Structure:** Intro → Main Section → Bridge/Variation → Climax → Conclusion\n"
        
        # Add audience emotion
        prompt += f"\n## Audience Impact\n- **Target Emotional Response:** {audience_emotion}\n"
        
        # Add production techniques
        production_techniques = random.sample(mood_elements['production_techniques'], 
                                             min(3, len(mood_elements['production_techniques'])))
        prompt += f"- **Production Techniques:** {', '.join(production_techniques)}\n"
        
        # Add stylistic notes if provided
        if stylistic_notes:
            prompt += f"\n## Stylistic Notes\n{stylistic_notes}\n"
        
        # Add final instructions
        prompt += """
## Creation Instructions
1. Create lyrics that authentically represent the artist's style and the specified themes
2. Develop a musical structure that fits the genre conventions while remaining distinctive
3. Ensure the track evokes the target emotional response in the audience
4. Balance familiarity with innovation to create something both accessible and unique
5. Consider how this track would fit within the artist's broader catalog

The final track should be detailed, cohesive, and ready for production.
"""
        
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "artist_name": artist_name,
                "genre": genre,
                "mood": mood,
                "tempo": tempo_category,
                "themes": themes,
                "audience_emotion": audience_emotion,
                "timestamp": self._get_timestamp()
            }
        }
    
    def generate_lyrics_prompt(
        self,
        artist_profile: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a focused prompt specifically for creating lyrics for a track.
        
        Args:
            artist_profile: Dictionary containing the artist's profile information
            overrides: Optional dictionary with specific overrides for this track
                
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(f"Generating lyrics prompt for artist: {artist_profile.get('name', 'Unknown')}")
        
        # Initialize overrides if None
        if overrides is None:
            overrides = {}
        
        # Extract key elements from the profile
        artist_name = artist_profile.get('name', 'Artist')
        genre = artist_profile.get('genre', 'Electronic')
        style = artist_profile.get('style', 'Unique')
        
        # Get mood from overrides or derive from artist style
        mood = overrides.get('mood', '')
        if not mood and 'style' in artist_profile:
            mood = artist_profile.get('style', '')
        
        # Get themes from overrides or artist profile
        themes = overrides.get('themes', '')
        if not themes:
            if 'themes' in artist_profile:
                themes = artist_profile.get('themes', '')
            elif 'thematic_elements' in artist_profile and 'lyrical_themes' in artist_profile['thematic_elements']:
                themes = ', '.join(artist_profile['thematic_elements']['lyrical_themes'])
            else:
                # Use genre-based themes
                genre_elements = self._extract_genre_elements(genre)
                themes = ', '.join(random.sample(genre_elements['themes'], min(2, len(genre_elements['themes']))))
        
        # Get lyrics language from overrides or artist profile
        lyrics_language = overrides.get('lyrics_language', '')
        if not lyrics_language:
            lyrics_language = artist_profile.get('lyrics_language', 'English')
        
        # Get track title if provided
        track_title = overrides.get('track_title', '')
        
        # Extract elements from databases
        mood_elements = self._extract_mood_elements(mood)
        
        # Build the lyrics prompt
        prompt = f"""# Lyrics Creation Prompt for {artist_name}

## Artist Context
Create lyrics for a {genre} track by {artist_name}, who has a {style} style.

## Lyrical Direction
- **Language:** {lyrics_language}
- **Primary Themes:** {themes}
- **Emotional Tone:** {mood}
- **Lyrical Approach:** {', '.join(random.sample(mood_elements['lyrical_themes'], min(3, len(mood_elements['lyrical_themes']))))}
"""

        # Add track title if provided
        if track_title:
            prompt += f"- **Track Title:** \"{track_title}\"\n"
        
        # Add structure guidance
        prompt += """
## Structural Elements
- **Chorus:** Create a memorable, impactful chorus that captures the essence of the track
- **Verses:** Develop verses that build the narrative or emotional journey
- **Pre-Chorus:** (If appropriate) Build tension leading into the chorus
- **Bridge:** (If appropriate) Provide contrast or deeper insight
- **Outro:** Consider how the lyrics should conclude

## Stylistic Guidance
"""
        
        # Add genre-specific lyrical guidance
        if genre.lower() in ["trap", "dark trap", "phonk"]:
            prompt += "- Use impactful, concise phrases with memorable hooks\n"
            prompt += "- Include space for ad-libs and vocal effects\n"
            prompt += "- Balance repetition with progression\n"
        elif genre.lower() in ["pop", "edm"]:
            prompt += "- Focus on universal themes with broad appeal\n"
            prompt += "- Create a strong, memorable chorus with potential for sing-along\n"
            prompt += "- Use accessible language with emotional impact\n"
        elif genre.lower() in ["hip hop"]:
            prompt += "- Develop a narrative flow with attention to wordplay\n"
            prompt += "- Balance storytelling with rhythmic considerations\n"
            prompt += "- Consider internal rhyme schemes and flow patterns\n"
        elif genre.lower() in ["indie"]:
            prompt += "- Focus on authentic, personal perspectives\n"
            prompt += "- Use imagery and metaphor to convey emotion\n"
            prompt += "- Balance accessibility with artistic expression\n"
        else:
            prompt += "- Create lyrics that authentically represent the artist's style\n"
            prompt += "- Balance emotional impact with artistic expression\n"
            prompt += "- Consider how the lyrics will complement the musical elements\n"
        
        # Add final instructions
        prompt += """
## Output Format
Provide complete lyrics including:
1. Clear section labels (Intro, Verse 1, Chorus, etc.)
2. All lyrics formatted as they would appear in a lyric sheet
3. Notes on any specific delivery techniques (if relevant)

The lyrics should authentically represent the artist's style while addressing the specified themes and emotional tone.
"""
        
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "artist_name": artist_name,
                "genre": genre,
                "mood": mood,
                "themes": themes,
                "lyrics_language": lyrics_language,
                "timestamp": self._get_timestamp()
            }
        }
    
    def generate_melody_prompt(
        self,
        artist_profile: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a focused prompt specifically for creating a melody for a track.
        
        Args:
            artist_profile: Dictionary containing the artist's profile information
            overrides: Optional dictionary with specific overrides for this track
                
        Returns:
            Dictionary containing the generated prompt and metadata
        """
        logger.info(f"Generating melody prompt for artist: {artist_profile.get('name', 'Unknown')}")
        
        # Initialize overrides if None
        if overrides is None:
            overrides = {}
        
        # Extract key elements from the profile
        artist_name = artist_profile.get('name', 'Artist')
        genre = artist_profile.get('genre', 'Electronic')
        style = artist_profile.get('style', 'Unique')
        
        # Get mood from overrides or derive from artist style
        mood = overrides.get('mood', '')
        if not mood and 'style' in artist_profile:
            mood = artist_profile.get('style', '')
        
        # Get tempo from overrides or derive from genre
        tempo_category = overrides.get('tempo', '')
        if not tempo_category:
            genre_elements = self._extract_genre_elements(genre)
            tempo_range = genre_elements.get('tempo_range', (90, 130))
            avg_tempo = (tempo_range[0] + tempo_range[1]) / 2
            
            if avg_tempo < 90:
                tempo_category = "slow"
            elif avg_tempo < 120:
                tempo_category = "medium"
            else:
                tempo_category = "fast"
        
        # Extract elements from databases
        genre_elements = self._extract_genre_elements(genre)
        mood_elements = self._extract_mood_elements(mood)
        tempo_elements = self._extract_tempo_elements(tempo_category)
        
        # Build the melody prompt
        prompt = f"""# Melody Creation Prompt for {artist_name}

## Musical Context
Create a melody for a {genre} track by {artist_name}, who has a {style} style.

## Melodic Direction
- **Genre/Style:** {genre} with {style} aesthetic
- **Mood/Emotion:** {mood}
- **Tempo:** {tempo_category.capitalize()} ({tempo_elements['bpm_range'][0]}-{tempo_elements['bpm_range'][1]} BPM)
- **Musical Elements:** {', '.join(random.sample(mood_elements['musical_elements'], min(3, len(mood_elements['musical_elements']))))}

## Melodic Structure
- **Hook/Chorus Melody:** Create a memorable, distinctive melody for the main hook/chorus
- **Verse Melody:** Develop complementary melodies for verses that build toward the chorus
- **Bridge/Breakdown:** Consider contrasting melodic elements for variation
- **Intro/Outro:** How the melody should be introduced and concluded

## Technical Considerations
"""
        
        # Add genre-specific melodic guidance
        if genre.lower() in ["trap", "dark trap", "phonk"]:
            prompt += "- Consider minor scales or modes (e.g., Phrygian, Locrian) for darker atmosphere\n"
            prompt += "- Use space and repetition effectively\n"
            prompt += "- Focus on memorable, simple motifs that can be varied\n"
        elif genre.lower() in ["pop", "edm"]:
            prompt += "- Prioritize catchiness and memorability in the chorus\n"
            prompt += "- Consider major scales for uplifting sections, minor for emotional contrast\n"
            prompt += "- Create clear melodic arcs with resolution\n"
        elif genre.lower() in ["hip hop"]:
            prompt += "- Design melodies that complement vocal flow and cadence\n"
            prompt += "- Use melodic elements that support rather than compete with vocals\n"
            prompt += "- Consider sample-inspired melodic approaches if appropriate\n"
        elif genre.lower() in ["ambient", "lofi"]:
            prompt += "- Focus on atmosphere and texture over traditional melodic development\n"
            prompt += "- Use space and sustain to create mood\n"
            prompt += "- Consider non-traditional scales or modal approaches\n"
        else:
            prompt += "- Create melodies that authentically represent the genre and artist style\n"
            prompt += "- Balance memorability with artistic expression\n"
            prompt += "- Consider how the melody will complement other musical elements\n"
        
        # Add final instructions
        prompt += """
## Output Format
Describe the melody in detail, including:
1. Key/scale recommendations
2. Melodic contour and movement
3. Rhythmic characteristics
4. Emotional qualities
5. How it should evolve throughout the track

The melody should authentically represent the artist's style while evoking the specified mood and fitting within the genre conventions.
"""
        
        # Return the prompt with metadata
        return {
            "prompt": prompt,
            "metadata": {
                "artist_name": artist_name,
                "genre": genre,
                "mood": mood,
                "tempo": tempo_category,
                "timestamp": self._get_timestamp()
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


# Factory function to create a track prompt generator
def create_track_prompt_generator(
    template_variety: int = 3,
    seed: Optional[int] = None
) -> TrackPromptGenerator:
    """
    Factory function to create a track prompt generator.
    
    Args:
        template_variety: Number of template variations to use
        seed: Optional random seed for reproducible generation
        
    Returns:
        A track prompt generator instance
    """
    return TrackPromptGenerator(
        template_variety=template_variety,
        seed=seed
    )


# Convenience function for generating track prompts
def generate_track_prompt(
    artist_profile: Dict[str, Any],
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive prompt for creating an AI-written song based on artist profile.
    
    This is a convenience function that creates a generator instance and calls
    generate_track_prompt on it.
    
    Args:
        artist_profile: Dictionary containing the artist's profile information
        overrides: Optional dictionary with specific overrides for this track
            
    Returns:
        Dictionary containing the generated prompt and metadata
    """
    generator = create_track_prompt_generator()
    return generator.generate_track_prompt(artist_profile, overrides)


# Example usage
if __name__ == "__main__":
    # Create a generator
    generator = create_track_prompt_generator(seed=42)
    
    # Example artist profile
    example_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
        "themes": "Urban isolation, night life, inner struggles",
        "lyrics_language": "English"
    }
    
    # Example overrides
    example_overrides = {
        "mood": "melancholic, dark",
        "tempo": "medium",
        "audience_emotion": "crying in the car, night drive vibes",
        "stylistic_notes": "Should have a nostalgic quality reminiscent of early 2000s mixtape style"
    }
    
    # Generate a track prompt
    result = generator.generate_track_prompt(example_profile, example_overrides)
    
    # Print the result
    print("TRACK PROMPT:")
    print(result["prompt"])
    
    # Generate a lyrics prompt
    lyrics_result = generator.generate_lyrics_prompt(example_profile, example_overrides)
    
    # Print the lyrics prompt
    print("\nLYRICS PROMPT:")
    print(lyrics_result["prompt"])
