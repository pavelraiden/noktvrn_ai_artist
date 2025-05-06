# /home/ubuntu/ai_artist_system_clone/mock_release_runner.py

import asyncio
import yaml
import logging
import os
import sys
import json
from typing import Dict, Any

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
sys.path.insert(0, PROJECT_ROOT)

# --- Configure logging ---
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MockReleaseRunner")

# --- Import Orchestrator and Schema ---
try:
    from llm_orchestrator.orchestrator import (
        LLMOrchestrator,
        OrchestratorError,
    )
    from schemas.song_metadata import SongMetadata
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


# --- Simple Template Substitution Helper ---
def substitute_template(template_str: str, context: Dict[str, Any]) -> str:
    """Very basic substitution for {{ path.to.variable }} format."""
    import re

    def replace_match(match):
        path = match.group(1).strip().split(".")
        value = context
        try:
            for key in path:
                if isinstance(value, dict):
                    value = value.get(key)
                elif isinstance(value, list) and key.isdigit():
                    value = value[int(key)]
                elif hasattr(value, key):
                    value = getattr(value, key)
                elif key in value:  # Added check for dict keys directly
                    value = value[key]
                else:
                    joined_path_str = " -> ".join(path)
                    logger.warning(
                        f"Could not resolve path part {joined_path_str}"
                    )
                    return match.group(0)  # Return original if path fails
            return str(value)
        except Exception as e:
            joined_path = " -> ".join(path)
            logger.warning(f"Error resolving path {joined_path}: {e}")
            return match.group(0)

    # Improved regex to handle potential nested structures better
    # This is still basic and might fail on complex cases
    return re.sub(r"{{\s*([^}]+?)\s*}}", replace_match, template_str)


def substitute_dict_templates(data: Any, context: Dict[str, Any]) -> Any:
    """Recursively substitute templates in dictionaries and lists."""
    if isinstance(data, dict):
        return {
            k: substitute_dict_templates(v, context) for k, v in data.items()
        }
    elif isinstance(data, list):
        return [substitute_dict_templates(item, context) for item in data]
    elif isinstance(data, str):
        return substitute_template(data, context)
    else:
        return data


# --- Main Runner Logic ---
async def run_release_plan(plan_path: str):
    logger.info(f"Loading release plan from: {plan_path}")
    try:
        with open(plan_path, "r") as f:
            plan = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load or parse release plan: {e}")
        return

    # CORRECTED LINE 82:
    logger.info(
        f"Initializing LLM Orchestrator for release: {plan.get('release_id')}"
    )
    global_config = plan.get("global_config", {})
    try:
        # Use primary LLM and fallbacks from the plan
        orchestrator = LLMOrchestrator(
            primary_model=global_config.get(
                "primary_llm", "gemini:gemini-1.5-flash-latest"
            ),
            fallback_models=global_config.get("fallback_llms", [])
            + [
                global_config.get("suno_model")
            ],  # Ensure Suno is in fallbacks if specified
            config={"temperature": 0.7},  # Basic config
            enable_fallback_notifications=False,
        )
    except Exception as e:
        logger.error(
            f"Failed to initialize LLM Orchestrator: {e}", exc_info=True
        )
        return

    # --- Execute Steps Sequentially ---
    step_outputs = {}
    context = {"global_config": global_config, "steps": step_outputs}
    logger.info("Starting release plan execution...")

    for i, step in enumerate(plan.get("steps", [])):
        step_id = step.get("step_id", f"step_{i+1}")
        step_type = step.get("type")
        description = step.get("description", "No description")
        logger.info(f"--- Executing Step: {step_id} ({step_type}) ---")
        logger.debug(f"Description: {description}")

        try:
            # Substitute templates in step parameters using current context
            step_params = substitute_dict_templates(step, context)

            result = None
            if step_type == "llm_generate_text":
                prompt = step_params.get("prompt")
                messages = step_params.get("messages")
                system_prompt = step_params.get("system_prompt")
                model = step_params.get(
                    "model", global_config.get("primary_llm")
                )
                gen_params = step_params.get("params", {})

                logger.info(f"Calling LLM ({model}) for text generation.")
                # Need to ensure the orchestrator uses the specified model if possible
                # For mock, we just call generate_text_async
                result = await orchestrator.generate_text_async(
                    prompt=prompt,
                    messages=messages,
                    system_prompt=system_prompt,
                    generation_params=gen_params,
                    # TODO: Add logic to force specific model if needed
                )
                if isinstance(result, str):
                    logger.info(f"LLM Result (truncated): {result[:100]}...")
                else:
                    logger.warning(
                        f"LLM step returned unexpected type: {type(result)}"
                    )

            elif step_type == "suno_bas_generate_song":
                suno_prompt = step_params.get("suno_prompt", {})
                model_identifier = suno_prompt.get(
                    "model", global_config.get("suno_model")
                )  # Get specific suno model
                if not model_identifier or not model_identifier.startswith(
                    "suno:"
                ):
                    logger.error(
                        f"Invalid or missing Suno model identifier in step {step_id}"
                    )
                    raise ValueError(
                        "Suno model identifier required for suno_bas_generate_song step."
                    )

                # Ensure run_id is passed or generated
                if "run_id" not in suno_prompt:
                    # CORRECTED LINE 144:
                    suno_prompt["run_id"] = (
                        f"{plan.get('release_id', 'mock_release')}_{step_id}_{os.urandom(3).hex()}"
                    )

                logger.info(
                    f"Calling Suno BAS ({model_identifier}) via orchestrator."
                )
                logger.debug(
                    f"Suno Prompt: {json.dumps(suno_prompt, indent=2)}"
                )

                # Call orchestrator, specifically targeting the Suno model via its prompt structure
                # ADDED dummy prompt to satisfy orchestrator check
                result = await orchestrator.generate_text_async(
                    prompt="trigger_suno_bas",  # Dummy prompt
                    suno_generation_prompt=suno_prompt,
                )

                if isinstance(result, SongMetadata):
                    logger.info(
                        f"Suno BAS Result: {result.model_dump_json(indent=2)}"
                    )
                else:
                    logger.warning(
                        f"Suno BAS step returned unexpected type: {type(result)}. Expected SongMetadata."
                    )
                    # In a real scenario, this might be a failure
                    result = None  # Treat as failure for now

            elif step_type == "finalize":
                logger.info("Finalizing release (mock step). Inputs gathered.")
                # In a real runner, compile inputs here
                result = {
                    "status": "finalized",
                    "inputs_received": step_params.get("inputs"),
                }
                logger.info(f"Finalize Result: {result}")

            else:
                logger.warning(
                    f"Unsupported step type: {step_type}. Skipping."
                )
                result = {
                    "status": "skipped",
                    "reason": f"Unsupported type: {step_type}",
                }

            # Store output
            output_var = step.get("output_variable")
            if output_var:
                step_outputs[step_id] = {"output": result}
                logger.debug(
                    f"Stored output in context variable: steps.{step_id}.output"
                )
            else:
                step_outputs[step_id] = {
                    "status": "completed",
                    "result_type": type(result).__name__,
                }

        except Exception as e:
            logger.error(f"Error executing step {step_id}: {e}", exc_info=True)
            step_outputs[step_id] = {"status": "failed", "error": str(e)}
            # Decide whether to stop execution on failure
            logger.warning(
                "Continuing to next step despite error."
            )  # For mock test, continue
            # break # Uncomment to stop on first error

    logger.info("--- Release Plan Execution Finished ---")
    logger.info("Final Context:")
    # Use json dumps for cleaner printing of potentially complex objects
    try:
        print(
            json.dumps(context, indent=2, default=str)
        )  # Use default=str for non-serializable objects
    except Exception as e:
        logger.error(f"Could not serialize final context: {e}")
        print(context)  # Print raw context if serialization fails


if __name__ == "__main__":
    plan_file = os.path.join(PROJECT_ROOT, "release_plan.yaml")
    if not os.path.exists(plan_file):
        logger.error(f"Release plan not found at: {plan_file}")
    else:
        asyncio.run(run_release_plan(plan_file))
