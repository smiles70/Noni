"""Type-safe schema for the landing-page content.

Wraps the dict in `backend.content.landing_page` so API responses and
frontend clients have a validated, documented contract.
"""

from typing import List
from pydantic import BaseModel


class HeroSection(BaseModel):
    headline: str
    subheadline: str


class ProseSection(BaseModel):
    title: str
    body: str


class ListSection(BaseModel):
    title: str
    items: List[str]


class CTA(BaseModel):
    label: str
    note: str


class CallToActionSection(BaseModel):
    primary: CTA
    secondary: CTA


class ClosingSection(BaseModel):
    body: str


class LandingPageContent(BaseModel):
    hero: HeroSection
    introduction: ProseSection
    what_noni_does: ListSection
    how_it_feels: ListSection
    trust_and_safety: ProseSection
    call_to_action: CallToActionSection
    closing: ClosingSection
