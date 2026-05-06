"""ProgramGraph data for diagnostic signals."""

from typing import List
from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str


class ProgramGraph(BaseModel):
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
