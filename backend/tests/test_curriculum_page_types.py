"""Tests for the CurriculumPage schema extension (Phase 1 expansion).

The expansion adds `page_type` plus three optional structured blocks
(`principle`, `example`, `retrieval`). These tests pin down:

  - Backward compatibility: legacy pages that set only the original
    four fields continue to validate, and `page_type` defaults to
    "principle".
  - Cross-field invariants: an `example` page must carry an
    `example` block; a `retrieval` page must carry a `retrieval`
    block; mismatched blocks are rejected.
  - Retrieval-block invariants: exactly two choices, unique ids,
    `correct_id` resolves to one of the choices.
  - Author intent: `extra="forbid"` rejects typos/unknown fields.
"""

import pytest
from pydantic import ValidationError

from backend.models.curriculum import (
    CurriculumPage,
    ExampleBlock,
    RetrievalBlock,
    RetrievalChoice,
)

# ---- Backward compatibility -------------------------------------------------


def test_legacy_page_still_validates_and_defaults_to_principle():
    p = CurriculumPage(
        id="legacy-1",
        title="Legacy",
        content=["a", "b"],
        complexity=1,
    )
    assert p.page_type == "principle"
    assert p.principle is None
    assert p.example is None
    assert p.retrieval is None


def test_legacy_page_dump_excludes_none_blocks_when_requested():
    """Routes serialize with exclude_none=True so legacy responses keep
    their original shape on the wire."""
    p = CurriculumPage(id="legacy-2", title="Legacy", content=["x"], complexity=1)
    payload = p.model_dump(exclude_none=True)
    assert "example" not in payload
    assert "retrieval" not in payload
    assert "principle" not in payload
    # page_type defaults to "principle" (a non-None scalar) so it
    # appears in the payload — that's intentional, and existing FE
    # tests assert presence of id/title/content/complexity but do not
    # forbid extras.
    assert payload["page_type"] == "principle"


# ---- Cross-field invariants -------------------------------------------------


def test_example_page_requires_example_block():
    with pytest.raises(ValidationError):
        CurriculumPage(
            id="e1",
            title="Example",
            content=["intro"],
            complexity=1,
            page_type="example",
            # missing example=
        )


def test_retrieval_page_requires_retrieval_block():
    with pytest.raises(ValidationError):
        CurriculumPage(
            id="r1",
            title="Retrieval",
            content=["intro"],
            complexity=1,
            page_type="retrieval",
        )


def test_principle_page_must_not_carry_example_block():
    with pytest.raises(ValidationError):
        CurriculumPage(
            id="p1",
            title="Principle",
            content=["c"],
            complexity=1,
            page_type="principle",
            example=ExampleBlock(situation="s", claude_says="c", takeaway="t"),
        )


def test_recap_page_must_not_carry_retrieval_block():
    with pytest.raises(ValidationError):
        CurriculumPage(
            id="rc1",
            title="Recap",
            content=["c"],
            complexity=1,
            page_type="recap",
            retrieval=RetrievalBlock(
                prompt="x",
                choices=[
                    RetrievalChoice(id="a", text="a"),
                    RetrievalChoice(id="b", text="b"),
                ],
                correct_id="a",
                explanation="e",
            ),
        )


# ---- Retrieval-block invariants ---------------------------------------------


def test_retrieval_block_requires_exactly_two_choices():
    with pytest.raises(ValidationError):
        RetrievalBlock(
            prompt="x",
            choices=[RetrievalChoice(id="a", text="A")],
            correct_id="a",
            explanation="e",
        )
    with pytest.raises(ValidationError):
        RetrievalBlock(
            prompt="x",
            choices=[
                RetrievalChoice(id="a", text="A"),
                RetrievalChoice(id="b", text="B"),
                RetrievalChoice(id="c", text="C"),
            ],
            correct_id="a",
            explanation="e",
        )


def test_retrieval_block_correct_id_must_match_a_choice():
    with pytest.raises(ValidationError):
        RetrievalBlock(
            prompt="x",
            choices=[
                RetrievalChoice(id="a", text="A"),
                RetrievalChoice(id="b", text="B"),
            ],
            correct_id="z",  # not in {a,b}
            explanation="e",
        )


def test_retrieval_block_choice_ids_must_be_unique():
    with pytest.raises(ValidationError):
        RetrievalBlock(
            prompt="x",
            choices=[
                RetrievalChoice(id="a", text="A"),
                RetrievalChoice(id="a", text="A again"),
            ],
            correct_id="a",
            explanation="e",
        )


def test_well_formed_retrieval_page_round_trips():
    p = CurriculumPage(
        id="r-ok",
        title="Pick the safe one",
        content=["Read both. There is no rush."],
        complexity=1,
        page_type="retrieval",
        retrieval=RetrievalBlock(
            prompt="Which response is safer?",
            choices=[
                RetrievalChoice(id="a", text="Ask Claude to confirm first."),
                RetrievalChoice(id="b", text="Send the message immediately."),
            ],
            correct_id="a",
            explanation="Confirming first leaves the choice with you.",
        ),
        example=None,
    )
    payload = p.model_dump()
    assert payload["page_type"] == "retrieval"
    assert payload["retrieval"]["correct_id"] == "a"


def test_well_formed_example_page_round_trips():
    p = CurriculumPage(
        id="ex-ok",
        title="What it might look like",
        content=["A short scene."],
        complexity=1,
        page_type="example",
        example=ExampleBlock(
            situation="You ask Claude to help write a friendly note.",
            claude_says="Here is one option. Change anything that does not sound like you.",
            takeaway="Claude offers options. You decide.",
        ),
    )
    payload = p.model_dump()
    assert payload["page_type"] == "example"
    assert payload["example"]["takeaway"].startswith("Claude offers")


# ---- Closed schema ----------------------------------------------------------


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        CurriculumPage(
            id="x",
            title="x",
            content=["x"],
            complexity=1,
            mystery="not allowed",  # type: ignore[call-arg]
        )
