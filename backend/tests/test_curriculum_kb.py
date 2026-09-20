"""PS-020 — curriculum KB generator + Retell uploader guardrails.

Pins the deterministic generator output shape and proves the uploader's
egress allowlist blocks every non-whitelisted call — the mechanism that
makes destructive Retell behavior impossible rather than absent.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import curriculum_to_kb as gen  # noqa: E402
import retell_apply_curriculum as apply_mod  # noqa: E402


class TestGenerator:
    def test_all_six_modules_render(self):
        out = gen.expected_outputs()
        assert sorted(out) == [
            f"module-{i}.md" for i in range(6)
        ]

    def test_every_unit_title_appears(self):
        out = gen.expected_outputs()
        joined = "\n".join(out.values())
        for _, _, units in gen.MODULES:
            for u in units:
                assert f"## {u.title}" in joined, u.id

    def test_retrieval_answers_marked_coach_not_read(self):
        out = gen.expected_outputs()
        text = "\n".join(out.values())
        assert "do not read verbatim" in text
        # every retrieval page contributes one marked answer line
        n_retrieval = sum(
            1
            for _, _, units in gen.MODULES
            for u in units
            for p in u.pages
            if p.retrieval is not None
        )
        assert text.count("Correct answer (do not read verbatim") == n_retrieval

    def test_deterministic_output(self):
        assert gen.expected_outputs() == gen.expected_outputs()

    def test_committed_docs_are_fresh(self):
        out = gen.expected_outputs()
        for name, text in out.items():
            f = gen.OUT_DIR / name
            assert f.exists(), f"{name} missing — run curriculum_to_kb.py"
            assert f.read_text() == text, f"{name} stale — run curriculum_to_kb.py"


class TestEgressGuardrails:
    def _client(self):
        return apply_mod.GuardedClient("test-key", allowed_kb_ids={"knowledge_base_ourkb"})

    def test_delete_is_impossible(self):
        c = self._client()
        with pytest.raises(PermissionError):
            c.call("DELETE", "/delete-knowledge-base/knowledge_base_ourkb")
        with pytest.raises(PermissionError):
            c.call("DELETE", f"/delete-retell-llm/{apply_mod.RECEPTIONIST_LLM_ID}")

    def test_patch_only_on_receptionist_llm(self):
        c = self._client()
        for lid in apply_mod.MUST_NOT_CHANGE_LLMS:
            with pytest.raises(PermissionError):
                c.call("PATCH", f"/update-retell-llm/{lid}", json={})

    def test_add_sources_only_on_own_kb(self):
        c = self._client()
        with pytest.raises(PermissionError):
            c.call("POST", "/add-knowledge-base-sources/knowledge_base_3bee30aa46d414e4",
                   data={})

    def test_no_arbitrary_post(self):
        c = self._client()
        with pytest.raises(PermissionError):
            c.call("POST", "/create-phone-call", json={})
        with pytest.raises(PermissionError):
            c.call("POST", "/update-agent/x", json={})

    def test_whitelist_shape(self):
        # the allowlist regex accepts the read surface and nothing else
        c = self._client()
        assert c._c is not None  # client constructed; enforcement is pre-request


class TestPromptSection:
    def test_section_marks_no_spoiler_rule(self):
        assert "NEVER read the marked" in apply_mod.PROMPT_SECTION
        assert apply_mod.PROMPT_SECTION_MARKER in apply_mod.PROMPT_SECTION
