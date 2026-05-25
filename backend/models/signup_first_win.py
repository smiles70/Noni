"""Typed schema for the Sign-up -> First Safe Win content (Golden Flow Steps 4-6).

Per ADR 0006, copy lives in backend/content/ as plain Python data. This module
projects that data into Pydantic models so API responses are validated and
the API contract is explicit.
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class InvitationStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    body: str
    options: List[str] = Field(min_length=1)
    note: str


class GuidedInteractionStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    body: str
    guidance: str


class FirstSafeWinStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    body: str
    reflection: str


class OptionalNextSteps(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    options: List[str] = Field(min_length=1)
    note: str


class SignupFirstWinContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step_4_invitation: InvitationStep
    step_5_guided_interaction: GuidedInteractionStep
    step_6_first_safe_win: FirstSafeWinStep
    optional_next_steps: OptionalNextSteps
