"""
Artist Compatibility Analyzer Module

This module determines how compatible trends are with an artist's identity,
ensuring that evolution maintains authenticity and coherence.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.trend_analyzer.compatibility")


class CompatibilityAnalyzerError(Exception):
    """Exception raised for errors in the compatibility analysis."""
    pass


class ArtistCompatibilityAnalyzer:
    """
    Determines how compatible trends are with an artist's identity.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the compatibility analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.compatibility_threshold = self.config.get("compatibility_threshold", 0.5)
        self.genre_weight = self.config.get("genre_weight", 0.4)
        self.style_weight = self.config.get("style_weight", 0.3)
        self.personality_weight = self.config.get("personality_weight", 0.3)
        
        # Load compatibility matrices if provided
        self.genre_compatibility = self.config.get("genre_compatibility", {})
        self.style_compatibility = self.config.get("style_compatibility", {})
        
        # Load default compatibility matrices if not provided
        if not self.genre_compatibility:
            self._load_default_compatibility_matrices()
        
        logger.info(f"Initialized ArtistCompatibilityAnalyzer with threshold {self.compatibility_threshold}")

    def analyze_trend_compatibility(self, artist_profile: Dict[str, Any], processed_trends: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how compatible trends are with an artist's identity.
        
        Args:
            artist_profile: The artist's profile
            processed_trends: Processed trend data
            
        Returns:
            Dictionary containing compatibility analysis
        """
        try:
            logger.info(f"Analyzing trend compatibility for artist {artist_profile.get('stage_name', 'Unknown')}")
            
            # Extract artist attributes
            artist_genre = artist_profile.get("genre", "Unknown")
            artist_subgenres = artist_profile.get("subgenres", [])
            artist_style_tags = artist_profile.get("style_tags", [])
            artist_personality = artist_profile.get("personality_traits", [])
            
            # Initialize result structure
            compatibility_analysis = {
                "timestamp": datetime.now().isoformat(),
                "artist_id": artist_profile.get("artist_id", "unknown"),
                "artist_name": artist_profile.get("stage_name", "Unknown"),
                "genre": artist_genre,
                "compatible_trends": [],
                "partially_compatible_trends": [],
                "incompatible_trends": [],
                "overall_compatibility_score": 0.0,
                "evolution_recommendations": []
            }
            
            # Analyze subgenre compatibility
            self._analyze_subgenre_compatibility(
                compatibility_analysis, 
                artist_genre, 
                artist_subgenres, 
                processed_trends
            )
            
            # Analyze technique compatibility
            self._analyze_technique_compatibility(
                compatibility_analysis, 
                artist_genre, 
                artist_style_tags, 
                processed_trends
            )
            
            # Analyze theme compatibility
            self._analyze_theme_compatibility(
                compatibility_analysis, 
                artist_personality, 
                processed_trends
            )
            
            # Analyze visual compatibility
            self._analyze_visual_compatibility(
                compatibility_analysis, 
                artist_style_tags, 
                processed_trends
            )
            
            # Calculate overall compatibility score
            compatibility_analysis["overall_compatibility_score"] = self._calculate_overall_compatibility(
                compatibility_analysis
            )
            
            # Generate evolution recommendations
            compatibility_analysis["evolution_recommendations"] = self._generate_evolution_recommendations(
                compatibility_analysis, 
                artist_profile
            )
            
            logger.info(f"Completed compatibility analysis with score {compatibility_analysis['overall_compatibility_score']}")
            return compatibility_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trend compatibility: {str(e)}")
            raise CompatibilityAnalyzerError(f"Failed to analyze trend compatibility: {str(e)}")

    def _analyze_subgenre_compatibility(
        self, 
        analysis: Dict[str, Any], 
        artist_genre: str, 
        artist_subgenres: List[str], 
        processed_trends: Dict[str, Any]
    ) -> None:
        """
        Analyze compatibility of trending subgenres with the artist.
        
        Args:
            analysis: The analysis dictionary to update
            artist_genre: The artist's main genre
            artist_subgenres: The artist's subgenres
            processed_trends: Processed trend data
        """
        trending_subgenres = processed_trends.get("insights", {}).get("rising_subgenres", [])
        
        for subgenre_trend in trending_subgenres:
            subgenre_name = subgenre_trend["name"]
            compatibility_score = self._calculate_subgenre_compatibility(
                artist_genre, 
                artist_subgenres, 
                subgenre_name
            )
            
            trend_info = {
                "type": "subgenre",
                "name": subgenre_name,
                "relevance_score": subgenre_trend["relevance_score"],
                "compatibility_score": round(compatibility_score, 2),
                "rationale": self._get_subgenre_compatibility_rationale(
                    artist_genre, 
                    artist_subgenres, 
                    subgenre_name, 
                    compatibility_score
                )
            }
            
            # Categorize based on compatibility score
            if compatibility_score >= 0.7:
                analysis["compatible_trends"].append(trend_info)
            elif compatibility_score >= 0.4:
                analysis["partially_compatible_trends"].append(trend_info)
            else:
                analysis["incompatible_trends"].append(trend_info)

    def _analyze_technique_compatibility(
        self, 
        analysis: Dict[str, Any], 
        artist_genre: str, 
        artist_style_tags: List[str], 
        processed_trends: Dict[str, Any]
    ) -> None:
        """
        Analyze compatibility of trending production techniques with the artist.
        
        Args:
            analysis: The analysis dictionary to update
            artist_genre: The artist's main genre
            artist_style_tags: The artist's style tags
            processed_trends: Processed trend data
        """
        trending_techniques = processed_trends.get("insights", {}).get("trending_techniques", [])
        
        for technique_trend in trending_techniques:
            technique_name = technique_trend["name"]
            compatibility_score = self._calculate_technique_compatibility(
                artist_genre, 
                artist_style_tags, 
                technique_name
            )
            
            trend_info = {
                "type": "technique",
                "name": technique_name,
                "relevance_score": technique_trend["relevance_score"],
                "compatibility_score": round(compatibility_score, 2),
                "rationale": self._get_technique_compatibility_rationale(
                    artist_genre, 
                    artist_style_tags, 
                    technique_name, 
                    compatibility_score
                )
            }
            
            # Categorize based on compatibility score
            if compatibility_score >= 0.7:
                analysis["compatible_trends"].append(trend_info)
            elif compatibility_score >= 0.4:
                analysis["partially_compatible_trends"].append(trend_info)
            else:
                analysis["incompatible_trends"].append(trend_info)

    def _analyze_theme_compatibility(
        self, 
        analysis: Dict[str, Any], 
        artist_personality: List[str], 
        processed_trends: Dict[str, Any]
    ) -> None:
        """
        Analyze compatibility of trending lyrical themes with the artist.
        
        Args:
            analysis: The analysis dictionary to update
            artist_personality: The artist's personality traits
            processed_trends: Processed trend data
        """
        trending_themes = processed_trends.get("insights", {}).get("trending_themes", [])
        
        for theme_trend in trending_themes:
            theme_name = theme_trend["name"]
            compatibility_score = self._calculate_theme_compatibility(
                artist_personality, 
                theme_name
            )
            
            trend_info = {
                "type": "theme",
                "name": theme_name,
                "relevance_score": theme_trend["relevance_score"],
                "compatibility_score": round(compatibility_score, 2),
                "rationale": self._get_theme_compatibility_rationale(
                    artist_personality, 
                    theme_name, 
                    compatibility_score
                )
            }
            
            # Categorize based on compatibility score
            if compatibility_score >= 0.7:
                analysis["compatible_trends"].append(trend_info)
            elif compatibility_score >= 0.4:
                analysis["partially_compatible_trends"].append(trend_info)
            else:
                analysis["incompatible_trends"].append(trend_info)

    def _analyze_visual_compatibility(
        self, 
        analysis: Dict[str, Any], 
        artist_style_tags: List[str], 
        processed_trends: Dict[str, Any]
    ) -> None:
        """
        Analyze compatibility of trending visual aesthetics with the artist.
        
        Args:
            analysis: The analysis dictionary to update
            artist_style_tags: The artist's style tags
            processed_trends: Processed trend data
        """
        trending_visuals = processed_trends.get("insights", {}).get("trending_visuals", [])
        
        for visual_trend in trending_visuals:
            visual_name = visual_trend["name"]
            compatibility_score = self._calculate_visual_compatibility(
                artist_style_tags, 
                visual_name
            )
            
            trend_info = {
                "type": "visual",
                "name": visual_name,
                "relevance_score": visual_trend["relevance_score"],
                "compatibility_score": round(compatibility_score, 2),
                "rationale": self._get_visual_compatibility_rationale(
                    artist_style_tags, 
                    visual_name, 
                    compatibility_score
                )
            }
            
            # Categorize based on compatibility score
            if compatibility_score >= 0.7:
                analysis["compatible_trends"].append(trend_info)
            elif compatibility_score >= 0.4:
                analysis["partially_compatible_trends"].append(trend_info)
            else:
                analysis["incompatible_trends"].append(trend_info)

    def _calculate_subgenre_compatibility(
        self, 
        artist_genre: str, 
        artist_subgenres: List[str], 
        trending_subgenre: str
    ) -> float:
        """
        Calculate compatibility score for a trending subgenre.
        
        Args:
            artist_genre: The artist's main genre
            artist_subgenres: The artist's subgenres
            trending_subgenre: The trending subgenre
            
        Returns:
            Compatibility score (0.0 to 1.0)
        """
        # Check if the subgenre is already one of the artist's subgenres
        if trending_subgenre in artist_subgenres:
            return 1.0
        
        # Check compatibility matrix
        genre_matrix = self.genre_compatibility.get(artist_genre, {})
        
        # Check if the subgenre is directly compatible with the main genre
        if trending_subgenre in genre_matrix.get("compatible_with", []):
            return 0.9
        
        # Check if the subgenre is partially compatible with the main genre
        if trending_subgenre in genre_matrix.get("partially_compatible_with", []):
            return 0.6
        
        # Check if the subgenre is incompatible with the main genre
        if trending_subgenre in genre_matrix.get("incompatible_with", []):
            return 0.1
        
        # Check compatibility with artist's existing subgenres
        for subgenre in artist_subgenres:
            subgenre_matrix = self.genre_compatibility.get(artist_genre, {}).get(subgenre, {})
            
            if trending_subgenre in subgenre_matrix.get("compatible_with", []):
                return 0.8
            
            if trending_subgenre in subgenre_matrix.get("partially_compatible_with", []):
                return 0.5
        
        # Default moderate compatibility if no specific rules match
        return 0.4

    def _calculate_technique_compatibility(
        self, 
        artist_genre: str, 
        artist_style_tags: List[str], 
        trending_technique: str
    ) -> float:
        """
        Calculate compatibility score for a trending production technique.
        
        Args:
            artist_genre: The artist's main genre
            artist_style_tags: The artist's style tags
            trending_technique: The trending technique
            
        Returns:
            Compatibility score (0.0 to 1.0)
        """
        # Check if the technique aligns with any of the artist's style tags
        style_match_score = 0.0
        for tag in artist_style_tags:
            if self._are_terms_related(tag, trending_technique):
                style_match_score = 0.8
                break
        
        # Check if the technique is commonly used in the artist's genre
        genre_technique_map = {
            "Electronic": ["synthesis", "sampling", "processing", "field recording", "modular", "granular"],
            "Rock": ["distortion", "amplifier", "live recording", "tape", "room acoustics"],
            "Hip Hop": ["sampling", "drum programming", "808", "beat", "vocal processing"],
            "Pop": ["vocal layering", "pitch correction", "synthesized", "maximized loudness"]
        }
        
        genre_match_score = 0.0
        genre_techniques = genre_technique_map.get(artist_genre, [])
        for technique in genre_techniques:
            if self._are_terms_related(technique, trending_technique):
                genre_match_score = 0.7
                break
        
        # Return the higher of the two scores
        return max(style_match_score, genre_match_score, 0.3)  # Minimum baseline compatibility

    def _calculate_theme_compatibility(
        self, 
        artist_personality: List[str], 
        trending_theme: str
    ) -> float:
        """
        Calculate compatibility score for a trending lyrical theme.
        
        Args:
            artist_personality: The artist's personality traits
            trending_theme: The trending theme
            
        Returns:
            Compatibility score (0.0 to 1.0)
        """
        # Define theme-personality compatibility mappings
        theme_personality_map = {
            "introspection": ["thoughtful", "introspective", "philosophical", "deep"],
            "futurism": ["innovative", "forward-thinking", "experimental", "visionary"],
            "nostalgia": ["nostalgic", "sentimental", "emotional", "reflective"],
            "social commentary": ["outspoken", "political", "conscious", "activist"],
            "love": ["emotional", "romantic", "sensitive", "passionate"],
            "rebellion": ["rebellious", "defiant", "bold", "unconventional"],
            "nature": ["peaceful", "spiritual", "grounded", "environmentalist"],
            "urban life": ["street-smart", "urban", "realistic", "observant"]
        }
        
        # Check if the theme aligns with any of the artist's personality traits
        max_score = 0.3  # Baseline compatibility
        
        for theme, compatible_traits in theme_personality_map.items():
            if self._are_terms_related(theme, trending_theme):
                for trait in artist_personality:
                    if trait in compatible_traits:
                        max_score = max(max_score, 0.9)  # Strong match
                        break
                    elif self._are_terms_related(trait, theme):
                        max_score = max(max_score, 0.7)  # Moderate match
        
        return max_score

    def _calculate_visual_compatibility(
        self, 
        artist_style_tags: List[str], 
        trending_visual: str
    ) -> float:
        """
        Calculate compatibility score for a trending visual aesthetic.
        
        Args:
            artist_style_tags: The artist's style tags
            trending_visual: The trending visual aesthetic
            
        Returns:
            Compatibility score (0.0 to 1.0)
        """
        # Check if the visual style aligns with any of the artist's style tags
        max_score = 0.3  # Baseline compatibility
        
        for tag in artist_style_tags:
            if self._are_terms_related(tag, trending_visual):
                max_score = 0.9  # Strong match
                break
            
            # Check for partial matches
            visual_style_map = {
                "minimalist": ["clean", "simple", "modern", "sleek"],
                "retro": ["vintage", "nostalgic", "classic", "throwback"],
                "futuristic": ["modern", "cutting-edge", "innovative", "high-tech"],
                "organic": ["natural", "earthy", "warm", "textured"],
                "abstract": ["experimental", "artistic", "unconventional", "avant-garde"],
                "urban": ["street", "gritty", "raw", "industrial"]
            }
            
            for style, related_terms in visual_style_map.items():
                if self._are_terms_related(style, trending_visual) and tag in related_terms:
                    max_score = max(max_score, 0.7)  # Moderate match
        
        return max_score

    def _are_terms_related(self, term1: str, term2: str) -> bool:
        """
        Check if two terms are related.
        
        Args:
            term1: First term
            term2: Second term
            
        Returns:
            True if the terms are related, False otherwise
        """
        # Convert to lowercase for comparison
        term1 = term1.lower()
        term2 = term2.lower()
        
        # Direct match
        if term1 == term2:
            return True
        
        # Check if one term contains the other
        if term1 in term2 or term2 in term1:
            return True
        
        # Check for related terms using a simple mapping
        related_terms_map = {
            "electronic": ["synth", "digital", "electronic", "edm"],
            "analog": ["warm", "vintage", "tape", "analog"],
            "experimental": ["avant-garde", "unconventional", "innovative", "experimental"],
            "minimal": ["minimalist", "clean", "sparse", "minimal"],
            "atmospheric": ["ambient", "ethereal", "spacious", "atmospheric"],
            "retro": ["nostalgic", "vintage", "throwback", "retro"],
            "futuristic": ["forward-thinking", "cutting-edge", "futuristic", "modern"],
            "organic": ["natural", "acoustic", "warm", "organic"],
            "urban": ["city", "street", "urban", "metropolitan"],
            "emotional": ["emotive", "passionate", "sentimental", "emotional"]
        }
        
        # Check if terms are in the same related group
        for key, related in related_terms_map.items():
            if term1 in related and term2 in related:
                return True
            if (term1 == key or term1 in related) and (term2 == key or term2 in related):
                return True
        
        return False

    def _get_subgenre_compatibility_rationale(
        self, 
        artist_genre: str, 
        artist_subgenres: List[str], 
        trending_subgenre: str, 
        compatibility_score: float
    ) -> str:
        """
        Generate a rationale for subgenre compatibility.
        
        Args:
            artist_genre: The artist's main genre
            artist_subgenres: The artist's subgenres
            trending_subgenre: The trending subgenre
            compatibility_score: The calculated compatibility score
            
        Returns:
            Rationale text
        """
        if trending_subgenre in artist_subgenres:
            return f"Already part of artist's subgenres"
        
        if compatibility_score >= 0.7:
            return f"Highly compatible with {artist_genre} and existing subgenres"
        elif compatibility_score >= 0.4:
            return f"Moderately compatible with {artist_genre}, could be incorporated gradually"
        else:
            return f"Low compatibility with {artist_genre} and existing style, would represent a significant shift"

    def _get_technique_compatibility_rationale(
        self, 
        artist_genre: str, 
        artist_style_tags: List[str], 
        trending_technique: str, 
        compatibility_score: float
    ) -> str:
        """
        Generate a rationale for technique compatibility.
        
        Args:
            artist_genre: The artist's main genre
            artist_style_tags: The artist's style tags
            trending_technique: The trending technique
            compatibility_score: The calculated compatibility score
            
        Returns:
            Rationale text
        """
        if compatibility_score >= 0.7:
            return f"Aligns well with artist's style and {artist_genre} production approaches"
        elif compatibility_score >= 0.4:
            return f"Could complement existing style with some adaptation"
        else:
            return f"Significant departure from current production style"

    def _get_theme_compatibility_rationale(
        self, 
        artist_personality: List[str], 
        trending_theme: str, 
        compatibility_score: float
    ) -> str:
        """
        Generate a rationale for theme compatibility.
        
        Args:
            artist_personality: The artist's personality traits
            trending_theme: The trending theme
            compatibility_score: The calculated compatibility score
            
        Returns:
            Rationale text
        """
        if compatibility_score >= 0.7:
            return f"Resonates with artist's personality traits: {', '.join(artist_personality[:2])}"
        elif compatibility_score >= 0.4:
            return f"Could be explored while maintaining authentic voice"
        else:
            return f"May feel inauthentic given artist's established personality"

    def _get_visual_compatibility_rationale(
        self, 
        artist_style_tags: List[str], 
        trending_visual: str, 
        compatibility_score: float
    ) -> str:
        """
        Generate a rationale for visual compatibility.
        
        Args:
            artist_style_tags: The artist's style tags
            trending_visual: The trending visual aesthetic
            compatibility_score: The calculated compatibility score
            
        Returns:
            Rationale text
        """
        if compatibility_score >= 0.7:
            return f"Complements artist's visual identity and style tags"
        elif compatibility_score >= 0.4:
            return f"Could be incorporated as a visual accent or evolution"
        else:
            return f"Contrasts significantly with established visual identity"

    def _calculate_overall_compatibility(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall compatibility score based on all trend analyses.
        
        Args:
            analysis: The compatibility analysis
            
        Returns:
            Overall compatibility score (0.0 to 1.0)
        """
        compatible_count = len(analysis["compatible_trends"])
        partially_compatible_count = len(analysis["partially_compatible_trends"])
        incompatible_count = len(analysis["incompatible_trends"])
        
        total_count = compatible_count + partially_compatible_count + incompatible_count
        
        if total_count == 0:
            return 0.5  # Default neutral score
        
        # Calculate weighted average
        weighted_sum = (
            compatible_count * 1.0 + 
            partially_compatible_count * 0.5 + 
            incompatible_count * 0.0
        )
        
        return round(weighted_sum / total_count, 2)

    def _generate_evolution_recommendations(
        self, 
        analysis: Dict[str, Any], 
        artist_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for artist evolution based on compatibility analysis.
        
        Args:
            analysis: The compatibility analysis
            artist_profile: The artist's profile
            
        Returns:
            List of evolution recommendations
        """
        recommendations = []
        
        # Only recommend highly compatible trends with good relevance
        for trend in analysis["compatible_trends"]:
            if trend["relevance_score"] >= 0.7:
                recommendations.append({
                    "type": trend["type"],
                    "name": trend["name"],
                    "recommendation": self._get_recommendation_text(trend, artist_profile),
                    "priority": "high",
                    "compatibility_score": trend["compatibility_score"],
                    "relevance_score": trend["relevance_score"]
                })
        
        # Recommend some partially compatible trends with high relevance
        for trend in analysis["partially_compatible_trends"]:
            if trend["relevance_score"] >= 0.8:
                recommendations.append({
                    "type": trend["type"],
                    "name": trend["name"],
                    "recommendation": self._get_recommendation_text(trend, artist_profile),
                    "priority": "medium",
                    "compatibility_score": trend["compatibility_score"],
                    "relevance_score": trend["relevance_score"]
                })
        
        # Sort by priority and then by combined score
        recommendations.sort(
            key=lambda x: (
                0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2,
                -(x["compatibility_score"] + x["relevance_score"])
            )
        )
        
        return recommendations

    def _get_recommendation_text(self, trend: Dict[str, Any], artist_profile: Dict[str, Any]) -> str:
        """
        Generate recommendation text for a trend.
        
        Args:
            trend: The trend information
            artist_profile: The artist's profile
            
        Returns:
            Recommendation text
        """
        trend_type = trend["type"]
        trend_name = trend["name"]
        
        if trend_type == "subgenre":
            return f"Gradually incorporate elements of {trend_name} into future productions while maintaining core {artist_profile.get('genre', 'genre')} identity"
        
        elif trend_type == "technique":
            return f"Experiment with {trend_name} production technique in upcoming tracks"
        
        elif trend_type == "theme":
            return f"Explore {trend_name} as a lyrical theme in new content, filtered through artist's unique perspective"
        
        elif trend_type == "visual":
            return f"Incorporate {trend_name} visual elements into upcoming visual content while maintaining brand consistency"
        
        return f"Consider incorporating {trend_name} into artist evolution strategy"

    def _load_default_compatibility_matrices(self) -> None:
        """Load default genre and style compatibility matrices."""
        # Default genre compatibility matrix
        self.genre_compatibility = {
            "Electronic": {
                "compatible_with": ["ambient", "downtempo", "chillwave", "synthwave", "house"],
                "partially_compatible_with": ["techno", "trance", "drum and bass", "dubstep"],
                "incompatible_with": ["death metal", "hardcore punk", "gangsta rap"],
                "ambient": {
                    "compatible_with": ["downtempo", "chillwave", "drone", "minimal"],
                    "partially_compatible_with": ["lo-fi", "post-rock", "modern classical"],
                    "incompatible_with": ["hardstyle", "gabber", "trap"]
                },
                "techno": {
                    "compatible_with": ["minimal techno", "dub techno", "electro", "tech house"],
                    "partially_compatible_with": ["house", "trance", "industrial"],
                    "incompatible_with": ["ambient", "chillwave", "pop"]
                }
            },
            "Rock": {
                "compatible_with": ["indie rock", "alternative", "post-rock", "garage rock"],
                "partially_compatible_with": ["punk", "metal", "folk rock", "electronic rock"],
                "incompatible_with": ["trap", "EDM", "country"],
                "indie rock": {
                    "compatible_with": ["alternative", "post-punk", "garage rock", "dream pop"],
                    "partially_compatible_with": ["shoegaze", "indie folk", "indie electronic"],
                    "incompatible_with": ["death metal", "gangsta rap", "EDM"]
                }
            },
            "Hip Hop": {
                "compatible_with": ["trap", "boom bap", "conscious", "lo-fi hip hop"],
                "partially_compatible_with": ["R&B", "soul", "electronic", "jazz rap"],
                "incompatible_with": ["metal", "country", "classical"],
                "trap": {
                    "compatible_with": ["drill", "cloud rap", "mumble rap", "southern hip hop"],
                    "partially_compatible_with": ["EDM trap", "grime", "reggaeton"],
                    "incompatible_with": ["conscious hip hop", "jazz rap", "boom bap"]
                }
            },
            "Pop": {
                "compatible_with": ["synth-pop", "dance-pop", "electro-pop", "indie pop"],
                "partially_compatible_with": ["R&B", "hip hop", "electronic", "rock"],
                "incompatible_with": ["death metal", "noise", "experimental"],
                "synth-pop": {
                    "compatible_with": ["electro-pop", "dream pop", "indie pop", "dance-pop"],
                    "partially_compatible_with": ["new wave", "future bass", "chillwave"],
                    "incompatible_with": ["country", "folk", "metal"]
                }
            }
        }
        
        # Default style compatibility matrix could be added here if needed
        self.style_compatibility = {}
