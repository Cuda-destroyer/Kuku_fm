"""
Robust JSON response parsing and Pydantic validation for LLM outputs.
"""
import json
import re
from typing import Type, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def extract_json_str(text: str) -> str:
    """Extracts raw JSON string from an LLM response containing markdown or prose."""
    if not text:
        return ""

    text = text.strip()

    # Match ```json ... ``` blocks
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        return code_block_match.group(1).strip()

    # Match outer { ... } or [ ... ]
    outer_braces = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if outer_braces:
        return outer_braces.group(1).strip()

    return text


def clean_json_str(raw: str) -> str:
    """Cleans common LLM JSON syntax imperfections."""
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r",\s*(\}|\])", r"\1", raw)
    return cleaned


def parse_llm_json(text: str) -> Dict[str, Any]:
    """Parses text into a Python dict or list with fallback heuristics."""
    json_candidate = extract_json_str(text)
    try:
        return json.loads(json_candidate)
    except json.JSONDecodeError:
        cleaned = clean_json_str(json_candidate)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            raise ValueError(f"Could not parse valid JSON from LLM output: {err}\nOutput was: {text[:300]}")


def parse_and_validate(text: str, schema: Type[T]) -> T:
    """Parses JSON and validates against a Pydantic schema."""
    data = parse_llm_json(text)
    try:
        return schema.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Pydantic validation failed for {schema.__name__}: {e}")
