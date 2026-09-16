"""Type-safe schema for site-chrome (footer) content.

Wraps the dict in `backend.content.site_chrome` so API responses and
frontend clients share a validated contract.
"""

from typing import List

from pydantic import BaseModel


class FooterLink(BaseModel):
    label: str
    href: str


class SiteFooterContent(BaseModel):
    tagline: str
    nav_links: List[FooterLink]
    legal_links: List[FooterLink]
    mini_links: List[FooterLink]
    brand_label: str
    copyright: str
    social_links: List[FooterLink]
