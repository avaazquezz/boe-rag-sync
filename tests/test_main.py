import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest

import boe_rag_sync.main as shell
from boe_rag_sync.main import DEFAULT_MAX_CHUNK_CHARS, Settings

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
LAW_ID = "BOE-A-2015-11430"


def test_local_defaults_match_the_input_schema() -> None:
    # chunk ids depend on maxChunkChars: a local run and a platform run with the same input must
    # produce the same chunks.
    properties = json.loads((ROOT / ".actor" / "input_schema.json").read_text())["properties"]
    assert properties["maxChunkChars"]["default"] == DEFAULT_MAX_CHUNK_CHARS
    # ADR 0005: incremental sync is opt-in. The Store's daily test runs the prefilled input and
    # needs a non-empty dataset, which a stateful default would only produce on its first day.
    assert "default" not in properties["syncId"]
    assert "prefill" not in properties["syncId"]


class FakeActor:
    """Records the platform calls of one law sync, in order."""

    def __init__(self, affordable: int | None) -> None:
        self.calls: list[tuple[str, int]] = []
        self.affordable = affordable
        self.manifests: dict[str, Any] = {}
        self.log = SimpleNamespace(info=lambda *_: None, warning=lambda *_: None)

    def get_charging_manager(self) -> SimpleNamespace:
        return SimpleNamespace(
            calculate_max_event_charge_count_within_limit=lambda _: self.affordable
        )

    async def push_data(self, data: list[dict[str, Any]]) -> None:
        self.calls.append(("push", len(data)))

    async def charge(self, _: str, count: int) -> SimpleNamespace:
        self.calls.append(("charge", count))
        return SimpleNamespace(charged_count=count)

    async def get_value(self, key: str, default: Any) -> Any:  # noqa: ANN401
        return self.manifests.get(key, default)

    async def set_value(self, key: str, value: dict[str, str]) -> None:
        self.calls.append(("save manifest", len(value)))
        self.manifests[key] = value


def run(actor: FakeActor, *, billing: bool = True, stateless: bool = False) -> dict[str, Any]:
    def serve(request: httpx.Request) -> httpx.Response:
        part = "meta" if request.url.path.endswith("/metadatos") else "texto"
        return httpx.Response(200, content=(FIXTURES / f"et_{part}.xml").read_bytes())

    settings = Settings(
        as_of=shell.date(2026, 11, 3),
        max_chars=2000,
        full_reload=False,
        billing=billing,
        state_prefix=None if stateless else "default",
    )

    async def call() -> dict[str, Any]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(serve)) as client:
            state = None if stateless else actor
            return await shell._sync_law(client, state, LAW_ID, settings)  # type: ignore[arg-type]  # noqa: SLF001

    return asyncio.run(call())


@pytest.fixture
def actor(monkeypatch: pytest.MonkeyPatch) -> FakeActor:
    fake = FakeActor(affordable=2)
    monkeypatch.setattr(shell, "Actor", fake)
    return fake


def test_delivers_and_records_before_billing_and_stops_at_the_budget(actor: FakeActor) -> None:
    # The fixture has 4 articles in force; the budget pays for 2.
    result = run(actor)
    assert [name for name, _ in actor.calls] == ["push", "save manifest", "charge"]
    assert actor.calls[-1] == ("charge", 2)
    assert result["status"] == "stopped_by_spending_limit"
    assert result["articles_left_for_later"] == 2
    manifest = actor.manifests[f"default.{LAW_ID}"]
    assert {chunk_id.split(":")[1] for chunk_id in manifest} == {"a1", "a4"}


def test_the_next_run_bills_only_what_was_left(actor: FakeActor) -> None:
    run(actor)
    actor.calls.clear()
    actor.affordable = None
    result = run(actor)
    assert actor.calls[-1] == ("charge", 2)
    assert result["status"] == "synced"
    actor.calls.clear()
    assert run(actor)["upserts"] == 0
    assert actor.calls == [("save manifest", len(actor.manifests[f"default.{LAW_ID}"]))]


def test_free_runs_never_charge(actor: FakeActor) -> None:
    result = run(actor, billing=False)
    assert "charge" not in [name for name, _ in actor.calls]
    assert result["status"] == "synced"
    assert result["articles_charged"] == 0


def test_without_sync_id_every_run_exports_everything_and_keeps_no_state(actor: FakeActor) -> None:
    actor.affordable = None
    for _ in range(2):
        actor.calls.clear()
        result = run(actor, stateless=True)
        assert result["upserts"] == result["chunks_in_force"] > 0
        assert [name for name, _ in actor.calls] == ["push", "charge"]
    assert actor.manifests == {}


def test_actor_config_points_to_existing_valid_files() -> None:
    # The Store refuses to publish without an output schema; a missing or broken file would only
    # show up on the platform.
    actor_dir = ROOT / ".actor"
    config = json.loads((actor_dir / "actor.json").read_text())
    for ref in (config["input"], config["output"], config["storages"]["dataset"]):
        json.loads((actor_dir / ref).read_text())
    assert (actor_dir / config["dockerfile"]).is_file()
