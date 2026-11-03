import json
from pathlib import Path

from boe_rag_sync.main import DEFAULT_MAX_CHUNK_CHARS

SCHEMA = Path(__file__).parents[1] / ".actor" / "input_schema.json"


def test_local_default_matches_the_input_schema() -> None:
    # chunk ids depend on maxChunkChars: a local run and a platform run with the same input must
    # produce the same chunks.
    properties = json.loads(SCHEMA.read_text())["properties"]
    assert properties["maxChunkChars"]["default"] == DEFAULT_MAX_CHUNK_CHARS
