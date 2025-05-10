# llm_registry.py

"""
Central registry for known LLM models supported by the platform.

This registry stores information about known LLM models and providers.
It can be updated manually to include new models as they become available.
The LLMOrchestrator can use this registry to potentially discover and add
new models to its fallback sequence.
"""
# Removed unused typing imports

LLM_REGISTRY = {
    "openai": {
        "models": [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-4o-mini",  # Added as per instructions
        ]
    },
    "deepseek": {
        "models": [
            "deepseek-chat",
            "deepseek-coder",
        ]
    },
    "grok": {
        "models": [
            "grok-1",  # Added as per instructions
            # (assuming Grok3 refers to this or similar)
            # Add other Grok models if known, e.g., grok-1.5
        ]
    },
    "gemini": {
        "models": [
            "gemini-1.5-pro-latest",  # Added as per instructions
            "gemini-pro",  # Existing standard model
            "gemini-1.0-pro",
            "gemini-1.5-flash-latest",
        ]
    },
    "mistral": {
        "models": [
            "mistral-large-latest",
            "mistral-small-latest",
            "open-mixtral-8x7b",
            "open-mixtral-8x22b",
            "codestral-latest",
        ]
    },
    "anthropic": {  # Added provider for Claude
        "models": [
            "claude-3-opus-20240229",  # Added as per instructions
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
    },
    # Add other providers and their models as needed
}


# Function to potentially load/update this registry from a file or external
# source in the future
def load_registry():
    """Loads the LLM registry. Currently returns the hardcoded dictionary."""
    # In the future, this could load from a JSON/YAML file or query APIs.
    return LLM_REGISTRY


if __name__ == "__main__":
    # Example of accessing the registry
    registry = load_registry()
    print("Available Providers and Models:")
    for provider, data in registry.items():
        print(f"- {provider.capitalize()}:")
        for model in data.get("models", []):
            print(f"  - {model}")
