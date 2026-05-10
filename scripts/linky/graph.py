from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


NODE_TYPES = {"url", "document", "entity", "topic", "claim", "action"}
EDGE_TYPES = {"mentions", "relates_to", "supports", "cites", "follow_up", "same_domain"}


@dataclass(frozen=True)
class GraphNode:
    id: str
    type: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in NODE_TYPES:
            raise ValueError(f"invalid node type: {self.type}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in EDGE_TYPES:
            raise ValueError(f"invalid edge type: {self.type}")

    @property
    def id(self) -> str:
        return f"{self.source}|{self.type}|{self.target}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchGraph:
    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: dict[str, GraphEdge] = field(default_factory=dict)

    def add_node(self, node_id: str, node_type: str, label: str, metadata: dict[str, Any] | None = None) -> GraphNode:
        if node_id in self.nodes:
            existing = self.nodes[node_id]
            merged = dict(existing.metadata)
            merged.update(metadata or {})
            self.nodes[node_id] = GraphNode(existing.id, existing.type, existing.label, merged)
        else:
            self.nodes[node_id] = GraphNode(node_id, node_type, label, metadata or {})
        return self.nodes[node_id]

    def add_edge(
        self, source: str, target: str, edge_type: str, metadata: dict[str, Any] | None = None
    ) -> GraphEdge:
        edge = GraphEdge(source, target, edge_type, metadata or {})
        if edge.id in self.edges:
            existing = self.edges[edge.id]
            merged = dict(existing.metadata)
            merged.update(metadata or {})
            self.edges[edge.id] = GraphEdge(existing.source, existing.target, existing.type, merged)
        else:
            self.edges[edge.id] = edge
        return self.edges[edge.id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
        }
