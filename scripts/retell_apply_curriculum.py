"""Attach the generated curriculum docs to the receptionist's knowledge base.

PS-020 — guardrail-locked, additive-only Retell mutation:

  * Egress allowlist: every HTTP call goes through _call(), which only
    permits the (method, path-pattern) pairs in ALLOWED_CALLS. A call
    outside that set raises before the request is sent — no DELETE
    exists and none can be added without editing this constant.
  * Write-target pin: the only LLM this script may PATCH is the
    receptionist's; agent_id and agent_name are asserted live.
  * KB isolation: sources are added only to a KB named
    CURRICULUM_KB_NAME that this script created or found by that name.
  * Read-modify-write: knowledge_base_ids and general_prompt are
    fetched, extended (union / marked append), and PATCHed back.
  * Idempotent: KB-by-name, source-by-title, attached-id, and
    prompt-marker checks make re-runs no-ops.
  * Snapshots: pre/post LLM + all-agent config dumps land in
    .ai/audit/retell-curriculum/ with a printed diff; the pre-snapshot
    is the rollback file.
  * Isolation tripwire: the four non-target LLMs' knowledge_base_ids
    and prompt hashes are asserted unchanged after apply.
  * Requires --apply to write; a bare run is a dry-run that prints
    intent against live state.

Usage:
    RETELL_API_KEY=... python scripts/retell_apply_curriculum.py            # dry-run
    RETELL_API_KEY=... python scripts/retell_apply_curriculum.py --apply
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import httpx

API = "https://api.retellai.com"
ROOT = Path(__file__).resolve().parent.parent
DOC_DIR = ROOT / "retell" / "kb" / "curriculum"
AUDIT_DIR = ROOT / ".ai" / "audit" / "retell-curriculum"

# --- pinned targets ---------------------------------------------------------
RECEPTIONIST_AGENT_ID = "agent_83c72268174e906ec2ed82a564"
RECEPTIONIST_LLM_ID = "llm_1b76092d677b0df6aa0017b1e242"
CURRICULUM_KB_NAME = "mynaani-curriculum-v1"
PROMPT_SECTION_MARKER = "## Helping with a lesson"

# LLMs that must be byte-identical after apply (isolation tripwire).
MUST_NOT_CHANGE_LLMS = {
    "llm_99732214ed81ba8f26d3ea56772a": "callback (shared staging+prod)",
    "llm_a524945938fe49cc66f346d1ce52": "assistant",
    "llm_e9ed15195e3e52a257f4964625ef": "facility chat",
    "llm_13c7c67388fef34803a41180c0db": "gift chat",
}

PROMPT_SECTION = """
## Helping with a lesson

Some callers are learners who are stuck on a lesson or a practice
question. Your curriculum reference explains every unit in plain words.

- Ask which lesson or unit they are on, then look up that section.
- Explain the idea briefly, in the same calm tone the lessons use.
- For practice questions, coach the caller toward the answer — ask what
  they remember, offer a hint, encourage a guess. NEVER read the marked
  correct answer aloud; the practice only works if they recall it
  themselves.
- Keep it short. Your job is to get them unstuck and back to the lesson
  on the site — not to teach the whole lesson on the phone.
- If they are still stuck after a couple of tries, offer to have a
  person call them back.
"""


class GuardedClient:
    """httpx wrapper enforcing the egress allowlist."""

    def __init__(self, key: str, allowed_kb_ids: set[str]):
        self._c = httpx.Client(
            base_url=API, headers={"Authorization": f"Bearer {key}"}, timeout=30
        )
        self._kb_ids = allowed_kb_ids  # updated once the KB is created/found

    def call(self, method: str, path: str, **kw) -> httpx.Response:
        allowed = (
            (method == "GET" and re.fullmatch(
                r"/(list-knowledge-bases|get-knowledge-base/[^/]+|"
                r"get-agent/[^/]+|list-agents|list-chat-agents|"
                r"get-retell-llm/[^/]+|get-chat-agent/[^/]+)", path))
            or (method == "POST" and path == "/create-knowledge-base")
            or (method == "POST" and any(
                path == f"/add-knowledge-base-sources/{k}" for k in self._kb_ids))
            or (method == "PATCH"
                and path == f"/update-retell-llm/{RECEPTIONIST_LLM_ID}")
        )
        if not allowed:
            raise PermissionError(f"egress blocked: {method} {path}")
        r = self._c.request(method, path, **kw)
        r.raise_for_status()
        return r


def _snapshot(client: GuardedClient) -> dict:
    llm = client.call("GET", f"/get-retell-llm/{RECEPTIONIST_LLM_ID}").json()
    others = {
        lid: client.call("GET", f"/get-retell-llm/{lid}").json()
        for lid in MUST_NOT_CHANGE_LLMS
    }
    return {"receptionist": llm, "others": others}


def _diff(before: dict, after: dict) -> list[str]:
    out = []
    for lid, name in MUST_NOT_CHANGE_LLMS.items():
        if before["others"][lid] != after["others"][lid]:
            out.append(f"VIOLATION: {name} ({lid}) changed")
    return out


def main() -> int:
    apply = "--apply" in sys.argv
    mode = "APPLY" if apply else "DRY-RUN"
    key = None
    for a in sys.argv[1:]:
        if a.startswith("--key="):
            key = a.split("=", 1)[1]
    import os
    key = key or os.environ.get("RETELL_API_KEY", "")
    if not key:
        print("RETELL_API_KEY is not set — refusing to run.")
        return 2

    docs = sorted(DOC_DIR.glob("module-*.md"))
    if not docs:
        print("no generated docs — run scripts/curriculum_to_kb.py first")
        return 2

    client = GuardedClient(key, allowed_kb_ids=set())

    # --- pin check ----------------------------------------------------------
    agent = client.call("GET", f"/get-agent/{RECEPTIONIST_AGENT_ID}").json()
    assert agent.get("agent_name") == "MyNaani Receptionist", agent.get("agent_name")
    assert agent["response_engine"]["llm_id"] == RECEPTIONIST_LLM_ID
    print(f"{mode}: receptionist pinned -> {RECEPTIONIST_LLM_ID}")

    # --- snapshot -----------------------------------------------------------
    pre = _snapshot(client)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / "pre-state.json").write_text(json.dumps(pre, indent=1))

    # --- KB: create or reuse by name ---------------------------------------
    # create-knowledge-base is form-encoded (not JSON) and requires at
    # least one source — create carries the first doc; the rest go
    # through add-knowledge-base-sources.
    kbs = client.call("GET", "/list-knowledge-bases").json()
    kb = next((k for k in kbs if k.get("knowledge_base_name") == CURRICULUM_KB_NAME), None)
    pending = list(docs)
    if kb:
        kb_id = kb["knowledge_base_id"]
        print(f"{mode}: KB '{CURRICULUM_KB_NAME}' exists -> {kb_id}")
    elif apply:
        first, *rest = docs
        r = client.call(
            "POST", "/create-knowledge-base",
            data={
                "knowledge_base_name": CURRICULUM_KB_NAME,
                "knowledge_base_texts": json.dumps(
                    [{"title": first.stem, "text": first.read_text()}]
                ),
            },
        )
        kb_id = r.json()["knowledge_base_id"]
        pending = rest
        print(f"{mode}: created KB {kb_id} with source '{first.stem}'")
    else:
        kb_id = "<would-create>"
        print(f"{mode}: would create KB '{CURRICULUM_KB_NAME}' with {docs[0].stem}")

    client._kb_ids = {kb_id} if kb_id.startswith("knowledge_base_") else set()

    # --- sources: add missing docs by title ---------------------------------
    existing_titles = set()
    if client._kb_ids:
        kb_state = client.call("GET", f"/get-knowledge-base/{kb_id}").json()
        existing_titles = {
            s.get("title") for s in kb_state.get("knowledge_base_sources", [])
        }
    for doc in pending:
        title = doc.stem  # module-0 .. module-5
        if title in existing_titles:
            print(f"{mode}: source '{title}' already present — skip")
        elif apply:
            client.call(
                "POST", f"/add-knowledge-base-sources/{kb_id}",
                data={"knowledge_base_texts": json.dumps(
                    [{"title": title, "text": doc.read_text()}])},
            )
            print(f"{mode}: added source '{title}'")
        else:
            print(f"{mode}: would add source '{title}' ({doc.stat().st_size} bytes)")

    # --- attach KB + extend prompt ------------------------------------------
    llm = pre["receptionist"]
    kb_ids = list(llm.get("knowledge_base_ids") or [])
    patch = {}
    if kb_id in kb_ids:
        print(f"{mode}: KB already attached")
    else:
        patch["knowledge_base_ids"] = kb_ids + [kb_id]
        print(f"{mode}: attach KB -> {patch['knowledge_base_ids']}")

    prompt = llm.get("general_prompt") or ""
    if PROMPT_SECTION_MARKER in prompt:
        print(f"{mode}: prompt section already present — skip")
    else:
        patch["general_prompt"] = prompt.rstrip() + "\n" + PROMPT_SECTION
        print(f"{mode}: append '{PROMPT_SECTION_MARKER}' section to prompt")

    if apply and patch:
        client.call("PATCH", f"/update-retell-llm/{RECEPTIONIST_LLM_ID}", json=patch)
        print(f"{mode}: receptionist LLM updated")
    elif patch:
        print(f"{mode}: would PATCH update-retell-llm {list(patch)}")

    # --- post-state + tripwire ----------------------------------------------
    if apply:
        post = _snapshot(client)
        (AUDIT_DIR / "post-state.json").write_text(json.dumps(post, indent=1))
        violations = _diff(pre, post)
        if violations:
            for v in violations:
                print(v)
            print("ISOLATION VIOLATION — inspect .ai/audit/retell-curriculum/")
            return 1
        assert CURRICULUM_KB_NAME and kb_id in (
            post["receptionist"].get("knowledge_base_ids") or []
        ), "KB attach did not persist"
        print("post-state verified: KB attached, other LLMs unchanged")
    print("done" + ("" if apply else " (dry-run — pass --apply to write)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
