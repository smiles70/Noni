"""Curriculum page data model.

Curriculum-expansion sprint (Phase 1): a page now carries an optional
`page_type` + one of three optional structured blocks (`principle`,
`example`, `retrieval`). All new fields default to None / "principle"
so legacy pages — which set only `id/title/content/complexity` —
continue to validate unchanged.

Why structured blocks instead of free-form `content`:
  - The frontend dispatches on `page_type` to render distinct, tokenized
    sub-views (RecapPage, ContextPage, PrinciplePage, ExamplePage,
    RetrievalPage). Each sub-view obeys CONTRACT V1 (Heading / Body /
    Button / Card / List / Divider / Indicator only).
  - Authors cannot smuggle markup or behavior into `content` strings;
    structured blocks force the shape the renderer expects.
  - Cross-field validation (`page_type == "example"` => `example` set)
    catches malformed authoring at boot, not at render.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


PageType = Literal["recap", "context", "principle", "example", "retrieval"]


class RetrievalChoice(BaseModel):
    """A single answer option on a retrieval page.

    `id` is stable across deploys (used by telemetry to identify which
    option the learner selected). `text` is what the learner reads.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)


class RetrievalBlock(BaseModel):
    """A two-choice recognition prompt.

    Recognition over recall is the geragogy default: it is lower-load
    and dignity-preserving. Exactly two choices keeps the pre-answer
    interaction at 2 primary actions, fitting under
    curriculum.unit.max_primary_actions=5 even with NavBar's 2 entries.
    """

    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(..., min_length=1)
    choices: List[RetrievalChoice] = Field(..., min_length=2, max_length=2)
    correct_id: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def _correct_id_matches_a_choice(self) -> "RetrievalBlock":
        ids = {c.id for c in self.choices}
        if self.correct_id not in ids:
            raise ValueError(
                f"correct_id={self.correct_id!r} does not match any choice id "
                f"in {sorted(ids)!r}"
            )
        if len(ids) != len(self.choices):
            raise ValueError("choice ids must be unique")
        return self


class ExampleBlock(BaseModel):
    """A worked example: situation + sample Claude output + takeaway.

    Authors keep this concrete and short. The renderer surfaces
    `claude_says` inside a Card so the learner visually distinguishes
    "what an assistant might say" from "what the lesson is teaching."
    """

    model_config = ConfigDict(extra="forbid")

    situation: str = Field(..., min_length=1)
    claude_says: str = Field(..., min_length=1)
    takeaway: str = Field(..., min_length=1)


class CurriculumPage(BaseModel):
    """A single page within a curriculum lesson.

    Legacy shape (`id/title/content/complexity` only) is preserved; the
    `page_type` defaults to "principle" so untyped pages render as the
    plain narrative form they always did.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    content: List[str]
    complexity: int

    # ---- Curriculum-expansion fields (Phase 1) ------------------------------
    page_type: PageType = "principle"

    # Optional highlighted statement on a principle page (e.g., a one-line
    # rule the learner can carry away). Renders inside a Card.
    principle: Optional[str] = None

    # Worked example block: required when page_type == "example".
    example: Optional[ExampleBlock] = None

    # Retrieval block: required when page_type == "retrieval".
    retrieval: Optional[RetrievalBlock] = None

    @model_validator(mode="after")
    def _structured_block_matches_page_type(self) -> "CurriculumPage":
        # An example/retrieval page MUST carry its block; renderer would
        # otherwise have nothing to show. Other page types MUST NOT carry
        # a block they do not use, so author intent is unambiguous.
        if self.page_type == "example" and self.example is None:
            raise ValueError(
                f"page {self.id!r}: page_type='example' requires `example` block"
            )
        if self.page_type == "retrieval" and self.retrieval is None:
            raise ValueError(
                f"page {self.id!r}: page_type='retrieval' requires `retrieval` block"
            )
        if self.page_type != "example" and self.example is not None:
            raise ValueError(
                f"page {self.id!r}: `example` block set but page_type={self.page_type!r}"
            )
        if self.page_type != "retrieval" and self.retrieval is not None:
            raise ValueError(
                f"page {self.id!r}: `retrieval` block set but page_type={self.page_type!r}"
            )
        return self
