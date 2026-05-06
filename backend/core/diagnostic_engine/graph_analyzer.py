"""Diagnostic engine - emits graph insight signals only."""

from typing import List, Dict
from backend.models.agent import ProgramGraph


def analyze_graph(graph: ProgramGraph) -> List[Dict]:
    insights: List[Dict] = []
    node_ids = {n.id for n in graph.nodes}
    linked = {e.source for e in graph.edges} | {e.target for e in graph.edges}
    orphans = node_ids - linked
    if orphans and len(node_ids) > 1:
        insights.append(
            {
                "type": "GRAPH_ORPHAN",
                "severity": "low",
                "message": "Some blocks are not connected yet.",
            }
        )
    return insights
