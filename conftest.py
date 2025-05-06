import os
import sys
from dotenv import load_dotenv

print("[conftest.py] DEBUG: conftest.py loaded", file=sys.stderr)


def pytest_configure(config):
    """
    Load environment variables from .env file before tests run.
    Also, forcefully set critical keys if not found after loading .env,
    to ensure test collection doesn't fail on import-time checks.
    """
    print("[conftest.py] DEBUG: pytest_configure called", file=sys.stderr)
    # Assuming conftest.py is in the project root /home/ubuntu/ai_artist_system_clone/
    project_root = os.path.dirname(__file__)
    dotenv_path = os.path.join(project_root, ".env")
    print(
        f"[conftest.py] DEBUG: Expected .env path: {dotenv_path}",
        file=sys.stderr,
    )

    if os.path.exists(dotenv_path):
        print(
            f"[conftest.py] DEBUG: .env file found at {dotenv_path}. Loading...",
            file=sys.stderr,
        )
        loaded = load_dotenv(
            dotenv_path=dotenv_path, override=True, verbose=True
        )
        if loaded:
            print(
                "[conftest.py] DEBUG: python-dotenv reported .env was loaded.",
                file=sys.stderr,
            )
        else:
            print(
                "[conftest.py] DEBUG: python-dotenv reported .env was NOT loaded (or empty).",
                file=sys.stderr,
            )
    else:
        print(
            f"[conftest.py] DEBUG: .env file NOT found at {dotenv_path}.",
            file=sys.stderr,
        )

    # Forcefully set known required keys for test collection if not already set or to ensure override
    # This is to prevent import-time errors in modules that check os.getenv directly
    required_keys_for_collection = {
        "PIXABAY_KEY": "dummy_pixabay_key_for_pytest_conftest",
        "PEXELS_API_KEY": "dummy_pexels_key_for_pytest_conftest",
        "SUNO_API_KEY": "dummy_suno_key_for_pytest_conftest",  # Though this was already in .env
    }

    for key, value in required_keys_for_collection.items():
        if not os.getenv(key):
            print(
                f"[conftest.py] DEBUG: Env var {key} not found after dotenv, forcefully setting to '{value}'",
                file=sys.stderr,
            )
            os.environ[key] = value
        else:
            # Optionally override even if found, to ensure conftest controls test env
            # print(f"[conftest.py] DEBUG: Env var {key} found with value '{os.getenv(key)}'. Forcefully overriding to '{value}'", file=sys.stderr)
            # os.environ[key] = value
            print(
                f"[conftest.py] DEBUG: Env var {key} already set to '{os.getenv(key)}'. Not overriding from conftest defaults.",
                file=sys.stderr,
            )

    # Verify after attempting to load and set
    print(
        f"[conftest.py] DEBUG: PIXABAY_KEY after configure: {os.getenv('PIXABAY_KEY')}",
        file=sys.stderr,
    )
    print(
        f"[conftest.py] DEBUG: PEXELS_API_KEY after configure: {os.getenv('PEXELS_API_KEY')}",
        file=sys.stderr,
    )
    print(
        f"[conftest.py] DEBUG: SUNO_API_KEY after configure: {os.getenv('SUNO_API_KEY')}",
        file=sys.stderr,
    )
