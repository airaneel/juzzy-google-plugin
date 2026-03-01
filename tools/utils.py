import json
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

PROJECT_PATH = Path(__file__).parent


def load_valid_countries(filepath: Path) -> set[str] | None:
    try:
        if countries := json.loads(filepath.read_text(encoding="utf8")):
            return {country["country_code"] for country in countries}
    except Exception as e:
        logger.error(f"Failed to load valid countries from '{filepath}': {e}")
    return None


def load_valid_languages(filepath: Path) -> set[str] | None:
    try:
        if languages := json.loads(filepath.read_text(encoding="utf8")):
            return {language["language_code"] for language in languages}
    except Exception as e:
        logger.error(f"Failed to load valid languages from '{filepath}': {e}")
    return None


VALID_COUNTRIES: set[str] | None = load_valid_countries(
    PROJECT_PATH.joinpath("google-countries.json")
)
VALID_LANGUAGES: set[str] | None = load_valid_languages(
    PROJECT_PATH.joinpath("google-languages.json")
)
