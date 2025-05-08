# artist_creator.py
"""
This module is responsible for the creation of new AI artist personas.
It orchestrates the generation of artist characteristics, backstories, musical styles,
and initial visual concepts, leveraging LLMs and other services.
"""

import json
import os
import uuid
from datetime import datetime

# Assuming llm_orchestrator and services are structured to be importable
from llm_orchestrator.orchestrator import LLMOrchestrator
from services.artist_db_service import ArtistDBService
from services.voice_service import VoiceService


class ArtistCreator:
    """
    Orchestrates the creation of a new AI artist, from conceptualization to profile generation.
    """

    def __init__(
        self,
        llm_orchestrator: LLMOrchestrator,
        db_service: ArtistDBService,
        voice_service: VoiceService,
        output_path="./artist_profiles",
    ):
        """
        Initializes the ArtistCreator.

        Args:
            llm_orchestrator: An instance of the LLMOrchestrator.
            db_service: An instance of the ArtistDBService.
            voice_service: An instance of the VoiceService.
            output_path (str): Path to save generated artist profiles.
        """
        self.llm_orchestrator = llm_orchestrator
        self.db_service = db_service
        self.voice_service = voice_service
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        print(
            f"ArtistCreator initialized. Profiles will be saved to: {self.output_path}"
        )

    def generate_unique_artist_id(self):
        """Generates a unique ID for the new artist."""
        return str(uuid.uuid4())

    def define_core_concept(
        self, genre_preferences=None, mood_tags=None, trend_inputs=None
    ):
        """
        Defines the core concept for a new artist using LLM.

        Args:
            genre_preferences (list, optional): List of preferred genres.
            mood_tags (list, optional): List of mood tags.
            trend_inputs (dict, optional): Data from trend analysis.

        Returns:
            dict: A dictionary containing the artist's core concept (name,
                  persona summary, primary genre, visual style keywords).
        """
        prompt = (
            "Based on the following inputs, generate a compelling core concept "
            "for a new AI virtual music artist.\n"
            "The concept should include:\n"
            "1.  Artist Name (unique and memorable)\n"
            "2.  Persona Summary (a brief, engaging description of their character, "
            "style, and appeal - 2-3 sentences)\n"
            "3.  Primary Music Genre (e.g., Synthwave, Lo-fi Hip Hop, Ethereal Pop)\n"
            "4.  Key Visual Style Keywords (e.g., cyberpunk, minimalist, "
            "retro-futuristic, pastel goth)\n"
            "5.  Target Audience (e.g., Gen Z, indie music lovers, gamers)"
        )
        if genre_preferences:
            prompt += f"\nPreferred Genres: {", ".join(genre_preferences)}"
        if mood_tags:
            prompt += f"\nDesired Moods: {", ".join(mood_tags)}"
        if trend_inputs:
            # Ensure trend_inputs are meaningfully used by LLM
            prompt += f"\nRelevant Trends: {json.dumps(trend_inputs)}"

        prompt += (
            "\n\nReturn the concept as a JSON object with keys: 'artist_name', "
            "'persona_summary', 'primary_genre', 'visual_style_keywords', "
            "'target_audience'."
        )

        print(f"Generating core concept with prompt: {prompt}")
        response_text = self.llm_orchestrator.generate_text(
            prompt, expected_format="json"
        )

        concept_data = None
        if response_text:
            try:
                concept_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(
                    f"Error decoding JSON from LLM response for core concept: {e}"
                )
                # Fallback or error handling strategy needed here
                concept_data = {
                    "artist_name": (
                        f"FallbackSeer_{datetime.now().strftime('%H%M%S')}"
                    ),
                    "persona_summary": "A fallback entity due to LLM error.",
                    "primary_genre": "Experimental",
                    "visual_style_keywords": ["glitch", "abstract"],
                    "target_audience": "Error log reviewers",
                }
        else:
            # Fallback if LLM response is empty
            print("LLM response for core concept was empty. Using fallback.")
            concept_data = {
                "artist_name": f"EmptySeer_{datetime.now().strftime('%H%M%S')}",
                "persona_summary": "An entity born from an empty LLM response.",
                "primary_genre": "Ambient",
                "visual_style_keywords": ["minimalist", "void"],
                "target_audience": "Debuggers",
            }

        print(f"Core concept generated: {concept_data}")
        return concept_data

    def generate_backstory(self, artist_name, persona_summary, primary_genre):
        """
        Generates a detailed backstory for the artist using LLM.

        Args:
            artist_name (str): The artist's name.
            persona_summary (str): The artist's persona summary.
            primary_genre (str): The artist's primary genre.

        Returns:
            str: A detailed backstory for the artist.
        """
        prompt = (
            f"Create a detailed and engaging backstory (3-4 paragraphs) for the "
            f"AI music artist named '{artist_name}'.\n"
            f"Their persona is: '{persona_summary}'.\n"
            f"Their primary music genre is: '{primary_genre}'.\n"
            "The backstory should be imaginative and align with their persona and "
            "genre. \n"
            "Consider their origins, motivations, and what makes them unique."
        )
        print(f"Generating backstory for {artist_name}...")
        backstory = self.llm_orchestrator.generate_text(prompt)
        if not backstory:
            print(
                f"LLM response for backstory was empty. Using fallback for {artist_name}."
            )
            backstory = (
                f"{artist_name} has a mysterious past, woven from the silent "
                f"threads of the digital cosmos. Their story is yet to be fully "
                f"told, echoing the enigmatic nature of {primary_genre}."
            )

        print(f"Backstory generated for {artist_name}.")
        return backstory

    def generate_initial_voice_profile(self, artist_name, persona_summary):
        """
        Generates an initial voice profile/sample for the artist.

        Args:
            artist_name (str): The artist's name.
            persona_summary (str): The artist's persona summary.

        Returns:
            str: A URL or identifier for the generated voice sample.
        """
        print(
            f"Generating initial voice profile for {artist_name} based on "
            f"persona: {persona_summary}"
        )
        # Create a text prompt from persona for voice synthesis
        voice_prompt = f"This is the voice of {artist_name}. {persona_summary}"
        voice_sample_url = self.voice_service.create_voice_sample(
            text_prompt=voice_prompt,
            artist_id=artist_name.lower().replace(" ", "_"),
        )

        if not voice_sample_url:
            print(
                f"Voice sample generation failed for {artist_name}. Using placeholder."
            )
            voice_sample_url = (
                f"/placeholder/voices/{artist_name.lower().replace(' ', '_')}"
                "_voice_error.wav"
            )

        print(f"Voice sample URL for {artist_name}: {voice_sample_url}")
        return voice_sample_url

    def create_artist_profile(
        self, genre_preferences=None, mood_tags=None, trend_inputs=None
    ):
        """
        Creates a complete artist profile.

        Args:
            genre_preferences (list, optional): List of preferred genres.
            mood_tags (list, optional): List of mood tags.
            trend_inputs (dict, optional): Data from trend analysis.

        Returns:
            dict: The complete artist profile, or None if creation fails critically.
        """
        artist_id = self.generate_unique_artist_id()
        print(f"Starting creation for new artist ID: {artist_id}")

        core_concept = self.define_core_concept(
            genre_preferences, mood_tags, trend_inputs
        )
        if not core_concept or not core_concept.get("artist_name"):
            print(
                f"Critical failure: Core concept generation failed for artist ID "
                f"{artist_id}. Aborting profile creation."
            )
            return None

        backstory = self.generate_backstory(
            core_concept["artist_name"],
            core_concept["persona_summary"],
            core_concept["primary_genre"],
        )
        voice_profile_url = self.generate_initial_voice_profile(
            core_concept["artist_name"], core_concept["persona_summary"]
        )

        profile = {
            "artist_id": artist_id,
            "creation_date": datetime.utcnow().isoformat() + "Z",
            "name": core_concept["artist_name"],
            "persona_summary": core_concept["persona_summary"],
            "primary_genre": core_concept["primary_genre"],
            "secondary_genres": [],
            "visual_style_keywords": core_concept.get(
                "visual_style_keywords", []
            ),
            "target_audience": core_concept.get("target_audience", "Unknown"),
            "backstory": backstory,
            "influences": [],
            "themes_and_topics": [],
            "voice_profile_url": voice_profile_url,
            "initial_mood_tags": mood_tags if mood_tags else [],
            "initial_genre_preferences": (
                genre_preferences if genre_preferences else []
            ),
            "creation_method": "ai_assisted_generation_v1.1_recovered",
            "evolution_parameters": {
                "feedback_sensitivity": 0.7,
                "trend_adaptability": 0.5,
            },
            "status": "Candidate",
            "performance_history": [],
            "error_reports": [],
        }

        profile_filename = os.path.join(
            self.output_path,
            f"{artist_id}_{core_concept['artist_name'].replace(' ', '_')}.json",
        )
        try:
            with open(profile_filename, "w") as f:
                json.dump(profile, f, indent=4)
            print(f"Artist profile saved to: {profile_filename}")
        except IOError as e:
            print(f"Error saving artist profile {profile_filename}: {e}")
            # Continue even if file save fails, as DB save is primary

        try:
            db_add_success = self.db_service.add_artist(profile)
            if db_add_success:
                print(
                    f"Artist profile for {core_concept['artist_name']} "
                    "successfully saved to database."
                )
            else:
                print(
                    f"Failed to save artist profile for {core_concept['artist_name']} "
                    "to database."
                )
                # Potentially raise an error or return None if DB save is critical
        except Exception as e:
            print(
                f"Error saving artist profile for {core_concept['artist_name']} "
                f"to database: {e}"
            )
            return None  # Critical failure if DB operation fails

        print(
            f"Artist profile creation process for {core_concept['artist_name']} completed."
        )
        return profile


if __name__ == "__main__":
    # This is a regular string, not an f-string, so F541 is fixed.
    print("Simulating Artist Creation (using mock services)...")

    class MockLLMOrchestrator:
        def generate_text(self, prompt, expected_format="text"):
            print("\n--- Mock LLM Call ---") # Not an f-string
            print(f"Prompt: {prompt[:200]}...")
            if "core concept" in prompt and expected_format == "json":
                return json.dumps(
                    {
                        "artist_name": (
                            f"NovaPulse_{datetime.now().strftime('%S%f')}"
                        ),
                        "persona_summary": "A vibrant AI weaving dreams into sound.",
                        "primary_genre": "Chillwave",
                        "visual_style_keywords": ["neon", "abstract", "fluid"],
                        "target_audience": "Dreamers and thinkers.",
                    }
                )
            elif "backstory" in prompt:
                return "Born from starlight and code, NovaPulse explores the universe of sound."
            return "Mocked LLM Response"

    class MockArtistDBService:
        def add_artist(self, profile_data):
            print(
                f"Mock DB: Artist {profile_data['name']} (ID: {profile_data['artist_id']}) "
                "would be added to database."
            )
            return True

    class MockVoiceService:
        def create_voice_sample(self, text_prompt, artist_id):
            print(
                f"Mock Voice Service: Generating voice for {artist_id} - "
                f"{text_prompt[:100]}..."
            )
            return f"/mock/voices/{artist_id}_mock_voice.wav"

    mock_llm_ops = MockLLMOrchestrator()
    mock_db_ops = MockArtistDBService()
    mock_voice_ops = MockVoiceService()

    creator = ArtistCreator(
        llm_orchestrator=mock_llm_ops,
        db_service=mock_db_ops,
        voice_service=mock_voice_ops,
        output_path="./generated_artist_profiles_recovery",
    )

    print("\n--- Creating Artist 1 (No specific inputs) ---") # Not an f-string
    artist1_profile = creator.create_artist_profile()
    if artist1_profile:
        print(f"Successfully created artist: {artist1_profile['name']}")

    print("\n--- Creating Artist 2 (With genre and mood inputs) ---") # Not an f-string
    artist2_profile = creator.create_artist_profile(
        genre_preferences=["Ambient Techno", "IDM"],
        mood_tags=["introspective", "complex", "atmospheric"],
        trend_inputs={"current_hot_sound": "granular synthesis textures"},
    )
    if artist2_profile:
        print(f"Successfully created artist: {artist2_profile['name']}")

    print("\nArtist creation simulation finished.") # Not an f-string

