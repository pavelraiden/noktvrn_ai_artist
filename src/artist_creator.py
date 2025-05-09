"""
This module is responsible for the creation of new AI artist personas.
It orchestrates the generation of artist characteristics, backstories,
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
    Orchestrates the creation of a new AI artist, from conceptualization
    to profile generation.
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
            f"ArtistCreator initialized. Profiles saved to: {self.output_path}"
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
        prompt_base = (
            "Based on the following inputs, generate a compelling core concept "
            "for a new AI virtual music artist.\n"
            "The concept should include:\n"
            "1. Artist Name (unique and memorable)\n"
            "2. Persona Summary (a brief, engaging description of their character, "
            "style, and appeal - 2-3 sentences)\n"
            "3. Primary Music Genre (e.g., Synthwave, Lo-fi Hip Hop, "
            "Ethereal Pop)\n"
            "4. Key Visual Style Keywords (e.g., cyberpunk, minimalist, "
            "retro-futuristic, pastel goth)\n"
            "5. Target Audience (e.g., Gen Z, indie music lovers, gamers)"
        )
        prompt_parts = [prompt_base]

        if genre_preferences:
            genres_str = ", ".join(genre_preferences)
            prompt_parts.append("\nPref Genres: " + genres_str)  # noqa: E501
        if mood_tags:
            mood_string = ", ".join(mood_tags)
            prompt_parts.append("\nDesired Moods: " + mood_string)
        if trend_inputs:
            trends_json = json.dumps(trend_inputs)
            prompt_parts.append("\nRel Trends: " + trends_json)  # noqa: E501

        prompt_outro_json = (
            "\n\nReturn the concept as a JSON object with keys: "
        )
        prompt_outro_keys = (
            "'artist_name', 'persona_summary', 'primary_genre', "
            "'visual_style_keywords', 'target_audience'."
        )
        prompt_parts.append(prompt_outro_json)
        prompt_parts.append(prompt_outro_keys)
        prompt = "".join(prompt_parts)

        prompt_snippet = prompt[:20] if len(prompt) > 20 else prompt
        print(f"Core concept prompt (snippet): {prompt_snippet}...")

        response_text = self.llm_orchestrator.generate_text(
            prompt, expected_format="json"
        )

        concept_data = None
        if response_text:
            try:
                concept_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                err_msg_p1 = "Error decoding JSON from LLM response "
                err_msg_p2 = f"for core concept: {e}"
                print(err_msg_p1 + err_msg_p2)
                fallback_artist_name = (
                    f"FallbackSeer_{datetime.now().strftime('%H%M%S')}"
                )
                concept_data = {
                    "artist_name": fallback_artist_name,
                    "persona_summary": "A fallback entity due to LLM error.",
                    "primary_genre": "Experimental",
                    "visual_style_keywords": ["glitch", "abstract"],
                    "target_audience": "Error log reviewers",
                }
        else:
            print("LLM response for core concept was empty. Using fallback.")
            empty_fallback_name = (
                f"EmptySeer_{datetime.now().strftime('%H%M%S')}"
            )
            empty_persona_summary = (
                "An entity born from an empty LLM response."
            )
            concept_data = {
                "artist_name": empty_fallback_name,
                "persona_summary": empty_persona_summary,
                "primary_genre": "Ambient",
                "visual_style_keywords": ["minimalist", "void"],
                "target_audience": "Debuggers",
            }

        print(f"Core concept generated: {concept_data}")
        return concept_data

    def generate_backstory(self, artist_name, persona_summary, primary_genre):
        """
        Generates a detailed backstory for the artist using LLM.
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
            log_fb_empty = "LLM response for backstory was empty. "
            log_fb_artist_p1 = "Fallback for "
            log_fb_artist_p2 = f"{artist_name}."
            full_log_msg_parts = [
                log_fb_empty,
                log_fb_artist_p1,
                log_fb_artist_p2,
            ]
            print("".join(full_log_msg_parts))  # noqa: E501

            backstory_p1 = (
                f"{artist_name} has a mysterious past,"  # noqa: E501
            )
            b_p1_c1_p1 = " woven from silent "
            b_p1_c1_p2 = "threads"
            b_p1_c2 = " of the digital cosmos. "
            backstory_p2 = "Their story is yet to be fully told,"
            b_p2_c1 = " echoing the enigmatic nature"
            b_p2_c2 = f" of {primary_genre}."

            backstory_lines = [
                backstory_p1,
                b_p1_c1_p1,
                b_p1_c1_p2,
                b_p1_c2,
                backstory_p2,
                b_p2_c1,
                b_p2_c2,
            ]
            backstory = "".join(backstory_lines)

        print(f"Backstory generated for {artist_name}.")
        return backstory

    def generate_initial_voice_profile(self, artist_name, persona_summary):
        """
        Generates an initial voice profile/sample for the artist.
        """
        log_message_part1 = f"Generating voice for {artist_name}"
        log_message_part2 = f" based on persona: {persona_summary[:1]}..."
        print(log_message_part1 + log_message_part2)

        voice_prompt_p1 = f"This is the voice of {artist_name}. "
        voice_prompt_p2 = f"{persona_summary}"
        voice_prompt = voice_prompt_p1 + voice_prompt_p2

        voice_sample_url = self.voice_service.create_voice_sample(
            text_prompt=voice_prompt,
            artist_id=artist_name.lower().replace(" ", "_"),
        )

        if not voice_sample_url:
            log_voice_fail = (
                f"Voice sample generation failed for {artist_name}. "
                "Using placeholder."
            )
            print(log_voice_fail)
            placeholder_p1 = (
                f"/placeholder/voices/{artist_name.lower().replace(' ', '_')}"
            )
            placeholder_p2 = "_voice_error.wav"
            voice_sample_url = placeholder_p1 + placeholder_p2

        print(f"Voice sample URL for {artist_name}: {voice_sample_url}")
        return voice_sample_url

    def create_artist_profile(
        self, genre_preferences=None, mood_tags=None, trend_inputs=None
    ):
        """
        Creates a complete artist profile.
        """
        artist_id = self.generate_unique_artist_id()
        print(f"Starting creation for new artist ID: {artist_id}")

        core_concept = self.define_core_concept(
            genre_preferences, mood_tags, trend_inputs
        )
        if not core_concept or not core_concept.get("artist_name"):
            err_msg_part1 = (
                "Critical failure: Core concept generation failed for "
            )
            err_msg_part2 = (
                f"artist ID {artist_id}. Aborting profile creation."
            )
            print(err_msg_part1 + err_msg_part2)
            return None

        artist_name = core_concept["artist_name"]
        persona_summary = core_concept["persona_summary"]
        primary_genre = core_concept["primary_genre"]

        backstory = self.generate_backstory(
            artist_name, persona_summary, primary_genre
        )
        voice_profile_url = self.generate_initial_voice_profile(
            artist_name, persona_summary
        )

        profile = {
            "artist_id": artist_id,
            "creation_date": datetime.utcnow().isoformat() + "Z",
            "name": artist_name,
            "persona_summary": persona_summary,
            "primary_genre": primary_genre,
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
        profile_file_name_part1 = f"{artist_id}_"
        profile_file_name_part2 = f"{artist_name.replace(' ', '_')}.json"
        profile_filename = os.path.join(
            self.output_path, profile_file_name_part1 + profile_file_name_part2
        )
        try:
            with open(profile_filename, "w") as f:
                json.dump(profile, f, indent=4)
            print(f"Artist profile saved to: {profile_filename}")
        except IOError as e:
            print(f"Error saving artist profile {profile_filename}: {e}")

        try:
            db_add_success = self.db_service.add_artist(profile)
            if db_add_success:
                db_log_msg = (
                    f"Artist profile for {artist_name} saved to db OK."
                )
                print(db_log_msg)
            else:
                fail_msg = (
                    f"Failed to save artist profile for {artist_name} to db."
                )
                print(fail_msg)
        except Exception as e:
            err_log_msg = f"Error saving profile for {artist_name} to db: {e}"
            print(err_log_msg)
            return None

        print(f"Artist profile creation process for {artist_name} completed.")
        return profile


if __name__ == "__main__":
    sim_creation_msg = "\n--- Simulating Artist Creation (mock services) ---"
    print(sim_creation_msg)

    class MockLLMOrchestrator:
        def generate_text(self, prompt, expected_format="text"):
            mock_llm_call_msg = "\n--- Mock LLM Call ---"
            print(mock_llm_call_msg)
            prompt_display = prompt[:60]
            print(f"Prompt (first 60): {prompt_display}...")  # noqa: E501
            if "core concept" in prompt and expected_format == "json":
                artist_name_mock = "NovaPulse_" + datetime.now().strftime(
                    "%S%f"
                )
                return json.dumps(
                    {
                        "artist_name": artist_name_mock,
                        "persona_summary": "A vibrant AI weaving dreams into sound.",
                        "primary_genre": "Chillwave",
                        "visual_style_keywords": ["neon", "abstract", "fluid"],
                        "target_audience": "Dreamers and thinkers.",
                    }
                )
            elif "backstory" in prompt:
                return (
                    "Born from starlight and code, NovaPulse explores "
                    "the universe of sound."
                )
            return "Mocked LLM Response"

    class MockArtistDBService:
        def add_artist(self, profile_data):
            artist_name = profile_data["name"]
            artist_id = profile_data["artist_id"]
            db_msg = f"Mock DB: Artist {artist_name} (ID: {artist_id}) added."
            print(db_msg)
            return True

    class MockVoiceService:
        def create_voice_sample(self, text_prompt, artist_id):
            log_message_part1 = f"MockVoiceSvc: Gen voice for {artist_id}"
            log_message_part2 = f" - {text_prompt[:3]}..."
            print(log_message_part1 + log_message_part2)
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

    print("\n--- Creating Artist 1 (No specific inputs) ---")
    artist1_profile = creator.create_artist_profile()
    if artist1_profile:
        print(f"Successfully created artist: {artist1_profile['name']}")

    print("\n--- Creating Artist 2 (With genre and mood inputs) ---")
    artist2_trend_inputs = {"current_hot_sound": "granular synthesis textures"}
    artist2_profile = creator.create_artist_profile(
        genre_preferences=["Ambient Techno", "IDM"],
        mood_tags=["introspective", "complex", "atmospheric"],
        trend_inputs=artist2_trend_inputs,
    )
    if artist2_profile:
        print(f"Successfully created artist: {artist2_profile['name']}")

    print("\nArtist creation simulation finished.")
