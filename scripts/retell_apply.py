"""Apply Retell config for the facility chat agent — partner-inquiry path.

Idempotent-by-inspection script (no Retell SDK dependency; httpx only):

1. Adds retell/kb/partner-inquiry.md as a text source on the facility
   knowledge base (skipped when a source with the same title exists).
2. Uploads the 4 mynaani.com whitepaper PDFs as file sources on the
   facility KB (skipped per-filename when already present).
3. Merges retell/tools/submit-partner-inquiry.json into the facility
   agent's LLM `general_tools` (replaces an existing tool of the same
   name; tools live on the Retell LLM response engine, not the agent).

Usage:
    RETELL_API_KEY=... python scripts/retell_apply.py [--dry-run]

Persona isolation (ADR-0032 amendment): this touches the FACILITY
agent/LLM/KB only. The gift agent is never modified.
"""

import json
import os
import sys
from pathlib import Path

import httpx

API = "https://api.retellai.com"
FACILITY_CHAT_AGENT_ID = "agent_719be4f2578150bb27ac06f357"
FACILITY_KB_ID = "knowledge_base_d52a7c13a5b4b702"
KB_TITLE = "partner-inquiry"
ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "frontend/public/whitepapers"
PDFS = [
    "cognitive-engagement.pdf",
    "geragogy-for-caregivers.pdf",
    "geragogy-the-key-to-learning.pdf",
    "the-ai-gap.pdf",
]


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    key = os.environ.get("RETELL_API_KEY", "")
    if not key:
        print("RETELL_API_KEY is not set — refusing to run.")
        return 2

    headers = {"Authorization": f"Bearer {key}"}
    kb_doc = (ROOT / "retell/kb/partner-inquiry.md").read_text()
    tool = json.loads((ROOT / "retell/tools/submit-partner-inquiry.json").read_text())

    with httpx.Client(base_url=API, headers=headers, timeout=30) as c:
        # --- resolve the facility agent's LLM id ----------------------
        agent = c.get(f"/get-chat-agent/{FACILITY_CHAT_AGENT_ID}")
        agent.raise_for_status()
        llm_id = agent.json()["response_engine"]["llm_id"]
        print(f"facility agent -> llm {llm_id}")

        # --- knowledge base source ------------------------------------
        kb = c.get(f"/get-knowledge-base/{FACILITY_KB_ID}")
        kb.raise_for_status()
        titles = {s.get("title") for s in kb.json().get("knowledge_base_sources", [])}
        if KB_TITLE in titles:
            print(f"KB source '{KB_TITLE}' already present — skipping")
        elif dry_run:
            print(f"DRY-RUN: would add KB text source '{KB_TITLE}'")
        else:
            r = c.post(
                f"/add-knowledge-base-sources/{FACILITY_KB_ID}",
                data={
                    "knowledge_base_texts": json.dumps(
                        [{"title": KB_TITLE, "text": kb_doc}]
                    )
                },
            )
            r.raise_for_status()
            print(f"added KB text source '{KB_TITLE}'")

        # --- whitepaper PDFs (file sources, facility KB) ---------------
        filenames = {
            s.get("filename") for s in kb.json().get("knowledge_base_sources", [])
        }
        pending = [p for p in PDFS if p not in filenames]
        if not pending:
            print("all 4 whitepaper PDFs already in facility KB — skipping")
        elif dry_run:
            print(f"DRY-RUN: would upload PDFs -> {pending}")
        else:
            files = [
                ("knowledge_base_files", (name, (PDF_DIR / name).open("rb")))
                for name in pending
            ]
            r = c.post(
                f"/add-knowledge-base-sources/{FACILITY_KB_ID}",
                files=files,
            )
            r.raise_for_status()
            print(f"uploaded PDFs -> {pending}")

        # --- tool on the LLM response engine --------------------------
        llm = c.get(f"/get-retell-llm/{llm_id}")
        llm.raise_for_status()
        llm_cfg = llm.json()
        tools = [
            t for t in llm_cfg.get("general_tools", []) if t.get("name") != tool["name"]
        ]
        tools.append(tool)
        if dry_run:
            print(
                f"DRY-RUN: would set general_tools -> "
                f"{[t.get('name') for t in tools]}"
            )
        else:
            r = c.patch(
                f"/update-retell-llm/{llm_id}",
                json={"general_tools": tools},
            )
            r.raise_for_status()
            print(f"updated {llm_id} general_tools")

    print("done" + (" (dry-run)" if dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
