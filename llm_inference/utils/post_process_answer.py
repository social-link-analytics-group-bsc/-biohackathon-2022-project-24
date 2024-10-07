import ast
import logging
from typing import Optional


def setup_logger() -> logging.Logger:
    """Setup the logger configuration for consistency."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


logger = setup_logger()


def format_to_json(answer: str) -> Optional[dict]:
    """Safely evaluate a string as Python literal."""
    try:
        return ast.literal_eval(answer)
    except (ValueError, SyntaxError) as e:
        logger.error(f"Invalid answer format: {e}")
        return None


def remove_none_values(d: Optional[dict]) -> Optional[dict]:
    """Recursively remove None values from a dictionary."""
    try:
        if not isinstance(d, dict):
            return d
        return {k: remove_none_values(v) for k, v in d.items() if v is not None}
    except ValueError:
        return None


def format_answer(answer: str) -> Optional[dict]:
    answer = format_to_json(answer)
    answer = remove_none_values(answer)
    return answer
