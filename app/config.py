"""
Central application configuration.

Loads environment variables from the project-root .env file. Secrets are
kept out of source code and are never printed by this module.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# app/config.py -> app -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Load the .env file from a stable location, not from the terminal's cwd.
load_dotenv(PROJECT_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def validate_config() -> None:
    """Raise a clear error if the required Groq key has not been configured."""
    if not GROQ_API_KEY or GROQ_API_KEY == "replace_with_your_groq_api_key":
        raise RuntimeError(
            "GROQ_API_KEY is missing. Copy .env.example to .env and add "
            "your key from https://console.groq.com/keys."
        )
