# Service for generating lyrics using LLM, potentially aligned with beat analysis

import logging
import json
import os

# Assuming LLMOrchestrator is accessible via project structure
# Need to adjust import based on actual location
from llm_orchestrator.orchestrator import LLMOrchestrator, LLMOrchestratorError

logger = logging.getLogger(__name__)

# Initialize LLM Orchestrator (assuming similar setup as in batch_runner)
# This might be better handled via dependency injection or a shared instance
REFLECTION_LLM_PRIMARY = os.getenv("REFLECTION_LLM_PRIMARY", "deepseek:deepseek-chat")
REFLECTION_LLM_FALLBACKS = os.getenv(
    "REFLECTION_LLM_FALLBACKS", "gemini:gemini-pro"
).split(",")
REFLECTION_MAX_TOKENS = int(os.getenv("REFLECTION_MAX_TOKENS", 500))
REFLECTION_TEMPERATURE = float(os.getenv("REFLECTION_TEMPERATURE", 0.6))

try:
    # Attempt to reuse the orchestrator instance if possible, otherwise create new
    # This is a simplification; a better design would pass the orchestrator instance
    llm_orchestrator = LLMOrchestrator(
        primary_model=REFLECTION_LLM_PRIMARY,
        fallback_models=REFLECTION_LLM_FALLBACKS,
        enable_auto_discovery=False,
    )
except Exception as e:
    logger.error(
        f"Failed to initialize LLM Orchestrator in LyricsService: {e}. Lyrics generation disabled."
    )
    llm_orchestrator = None


class LyricsServiceError(Exception):
    """Custom exception for LyricsService errors."""

    pass


class LyricsService:
    def __init__(self):
        # Orchestrator initialized globally for now
        self.orchestrator = llm_orchestrator

    def generate_lyrics(
        self,
        base_prompt: str,
        genre: str,
        style_notes: str,
        llm_config: dict,
        tempo: float | None = None,
        duration: float | None = None,
    ) -> str | None:
        """Generates lyrics using LLM, incorporating tempo and duration if provided.

        Args:
            base_prompt: The core theme or topic for the lyrics.
            genre: The musical genre.
            style_notes: Specific style notes for the artist.
            llm_config: Configuration for the LLM (model, temperature, etc.).
            tempo: Estimated tempo (BPM) of the music track.
            duration: Estimated duration (seconds) of the music track.

        Returns:
            The generated lyrics as a string, or None if generation failed.
        """
        if not self.orchestrator:
            logger.error("LLM Orchestrator not available. Cannot generate lyrics.")
            return None

        # Construct the prompt
        # Corrected f-string: Use escaped newline \n or multi-line string
        prompt = f"Write lyrics for a {genre} song.\n"
        prompt += f"Style: {style_notes}\n"
        prompt += f"Theme/Topic: {base_prompt}\n"

        if duration is not None:
            prompt += f"The track duration is approximately {duration:.0f} seconds.\n"
        if tempo is not None:
            prompt += f"The track tempo is approximately {tempo:.0f} BPM.\n"

        prompt += "Please generate suitable lyrics. Focus on evocative language and structure appropriate for the genre and duration."

        logger.info(f"Generating lyrics with LLM. Tempo: {tempo}, Duration: {duration}")
        logger.debug(f"Lyrics generation prompt:\n{prompt}")

        model = llm_config.get("model", REFLECTION_LLM_PRIMARY)
        temperature = llm_config.get("temperature", REFLECTION_TEMPERATURE)
        max_tokens = llm_config.get("max_tokens", REFLECTION_MAX_TOKENS)

        try:
            response = self.orchestrator.generate_text(
                prompt=prompt,
                model_name=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            lyrics = response.strip()
            # Basic validation: check if response is empty or just whitespace
            if not lyrics:
                logger.error("LLM returned empty response for lyrics generation.")
                return None
            # Corrected f-string: Use escaped newline \n
            logger.info(
                f"Successfully generated lyrics (length: {len(lyrics)}). Preview: \n{lyrics[:100]}..."
            )
            return lyrics
        except LLMOrchestratorError as e:
            logger.error(f"Failed to generate lyrics using LLM: {e}")
            # raise LyricsServiceError(f"LLM generation failed: {e}") from e
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error during lyrics generation: {e}", exc_info=True
            )
            # raise LyricsServiceError(f"Unexpected error: {e}") from e
            return None


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # load_dotenv() # If using .env
    lyrics_service = LyricsService()

    if lyrics_service.orchestrator:
        test_base_prompt = "Neon city nights and lost connections"
        test_genre = "Synthwave"
        test_style = "Dreamy, melancholic, 80s vibe"
        test_config = {}
        test_tempo = 120.0
        test_duration = 180.0

        print("--- Testing Lyrics Generation (with tempo/duration) ---")
        generated_lyrics = lyrics_service.generate_lyrics(
            test_base_prompt,
            test_genre,
            test_style,
            test_config,
            test_tempo,
            test_duration,
        )

        if generated_lyrics:
            print("Generated Lyrics:")
            print(generated_lyrics)
        else:
            print("Lyrics generation failed.")

        print("\n--- Testing Lyrics Generation (without tempo/duration) ---")
        generated_lyrics_no_timing = lyrics_service.generate_lyrics(
            test_base_prompt, test_genre, test_style, test_config
        )
        if generated_lyrics_no_timing:
            print("Generated Lyrics (no timing info):")
            print(generated_lyrics_no_timing)
        else:
            print("Lyrics generation failed.")
    else:
        print("Cannot run example: LLM Orchestrator failed to initialize.")
