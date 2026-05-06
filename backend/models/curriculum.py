"""Curriculum page data model."""
from typing import List
from pydantic import BaseModel

class CurriculumPage(BaseModel):
    id: str
    title: str
    content: List[str]
    complexity: int
