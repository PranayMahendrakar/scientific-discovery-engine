"""
🕸️ Knowledge Graph Module
Builds a graph of scientific concepts, entities, and relationships from papers.
"""

import json
import re
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime


class KnowledgeGraph:
    """
    Constructs and queries a knowledge graph from scientific papers.

    Graph structure:
    - Nodes: concepts, entities, genes, proteins, diseases, methods
    - Edges: relationships (causes, inhibits, interacts_with, studied_by, etc.)
    - Metadata: paper sources, frequency, confidence scores

    Used to:
    - Find strongly connected concept clusters
    - Identify missing connections (knowledge gaps)
    - Track how concepts relate across papers
    """

    def __init__(self):
        self.nodes: Dict[str, Dict] = {}        # node_id -> node metadata
        self.edges: Dict[str, Dict] = {}        # edge_id -> edge metadata
        self.adjacency: Dict[str, Set] = defaultdict(set)  # node -> connected nodes
        self.concept_papers: Dict[str, Set] = defaultdict(set)  # concept -> paper ids
        self.paper_concepts: Dict[str, Set] = defaultdict(set)  # paper_id -> concepts
        self._build_count = 0

    def build_from_papers(self, papers: List[Dict], extractions: List[Dict]) -> None:
        """
        Build graph from papers and their extracted concepts.

        Args:
            papers: List of paper dicts
            extractions: List of extraction results from each paper
        """
        print(f"   Building knowledge graph from {len(papers)} papers...")

        for i, (paper, extraction) in enumerate(zip(papers, extractions)):
            paper_id = paper.get("id", f"paper_{i}")
            self._add_paper_concepts(paper_id, extraction)

        # Compute co-occurrence edges between concepts
        self._build_cooccurrence_edges()
        self._build_count += 1

        print(f"   Graph: {len(self.nodes)} nodes, {len(self.edges)} edges")

    def _add_paper_concepts(self, paper_id: str, extraction: Dict) -> None:
        """Add concepts from a single paper to the graph."""
        concepts = extraction.get("concepts", [])
        relationships = extraction.get("relationships", [])
        entities = extraction.get("entities", {})

        # Add concept nodes
        for concept in concepts:
            concept_id = self._normalize_concept(concept)
            if concept_id:
                self._add_node(concept_id, concept, "concept")
                self.concept_papers[concept_id].add(paper_id)
                self.paper_concepts[paper_id].add(concept_id)

        # Add entity nodes (genes, proteins, diseases, etc.)
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity_id = self._normalize_concept(entity)
                if entity_id:
                    self._add_node(entity_id, entity, entity_type)
                    self.concept_papers[entity_id].add(paper_id)
                    self.paper_concepts[paper_id].add(entity_id)

        # Add explicit relationship edges
        for rel in relationships:
            subject = self._normalize_concept(rel.get("subject", ""))
            predicate = rel.get("predicate", "related_to")
            obj = self._normalize_concept(rel.get("object", ""))
            if subject and obj:
                self._add_edge(subject, predicate, obj, paper_id)

    def _build_cooccurrence_edges(self) -> None:
        """Build edges between concepts that co-occur in the same papers."""
        # Count co-occurrences
        cooc_counts: Dict[Tuple, int] = defaultdict(int)
        cooc_papers: Dict[Tuple, Set] = defaultdict(set)

        for paper_id, concepts in self.paper_concepts.items():
            concept_list = list(concepts)
            for i in range(len(concept_list)):
                for j in range(i + 1, min(i + 10, len(concept_list))):
                    pair = tuple(sorted([concept_list[i], concept_list[j]]))
                    cooc_counts[pair] += 1
                    cooc_papers[pair].add(paper_id)

        # Add edges for concepts co-occurring in 2+ papers
        for (c1, c2), count in cooc_counts.items():
            if count >= 1 and c1 in self.nodes and c2 in self.nodes:
                edge_id = f"{c1}__co_occurs_with__{c2}"
                if edge_id not in self.edges:
                    self.edges[edge_id] = {
                        "source": c1,
                        "target": c2,
                        "relation": "co_occurs_with",
                        "weight": count,
                        "papers": list(cooc_papers[(c1, c2)]),
                    }
                    self.adjacency[c1].add(c2)
                    self.adjacency[c2].add(c1)

    def _add_node(self, node_id: str, label: str, node_type: str) -> None:
        """Add or update a node in the graph."""
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "label": label,
                "type": node_type,
                "paper_count": 0,
                "frequency": 0,
            }
        self.nodes[node_id]["paper_count"] = len(self.concept_papers.get(node_id, set()))
        self.nodes[node_id]["frequency"] = self.nodes[node_id]["paper_count"]

    def _add_edge(self, source: str, relation: str, target: str, paper_id: str) -> None:
        """Add a directed edge to the graph."""
        # Ensure nodes exist
        if source not in self.nodes:
            self._add_node(source, source, "concept")
        if target not in self.nodes:
            self._add_node(target, target, "concept")

        edge_id = f"{source}__{relation}__{target}"
        if edge_id not in self.edges:
            self.edges[edge_id] = {
                "source": source,
                "target": target,
                "relation": relation,
                "weight": 1,
                "papers": [paper_id],
            }
        else:
            self.edges[edge_id]["weight"] += 1
            if paper_id not in self.edges[edge_id]["papers"]:
                self.edges[edge_id]["papers"].append(paper_id)

        self.adjacency[source].add(target)

    def _normalize_concept(self, concept: str) -> Optional[str]:
        """Normalize concept string to a stable node ID."""
        if not concept or len(concept) < 3:
            return None
        # Lowercase, remove special chars, replace spaces with underscores
        normalized = re.sub(r"[^a-z0-9_\s]", "", concept.lower().strip())
        normalized = re.sub(r"\s+", "_", normalized).strip("_")
        return normalized if len(normalized) >= 2 else None

    def get_neighbors(self, concept: str, depth: int = 1) -> Dict:
        """Get neighboring concepts up to given depth."""
        concept_id = self._normalize_concept(concept)
        if not concept_id or concept_id not in self.nodes:
            return {}

        visited = {concept_id}
        frontier = {concept_id}
        result = {concept_id: self.nodes[concept_id]}

        for _ in range(depth):
            next_frontier = set()
            for node in frontier:
                for neighbor in self.adjacency.get(node, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.add(neighbor)
                        result[neighbor] = self.nodes.get(neighbor, {})
            frontier = next_frontier

        return result

    def find_missing_connections(self) -> List[Dict]:
        """
        Identify potential missing connections (knowledge gaps) in the graph.

        Looks for:
        - Concept pairs that appear in overlapping paper sets but have no direct edge
        - High-degree concepts without connections to other high-degree concepts
        - Isolated concept clusters that might interact

        Returns:
            List of potential gaps with confidence scores
        """
        gaps = []
        high_freq_nodes = [
            node_id for node_id, data in self.nodes.items()
            if data.get("paper_count", 0) >= 2
        ]

        # Check pairs of frequently mentioned concepts with no direct edge
        for i, node1 in enumerate(high_freq_nodes[:50]):
            for node2 in high_freq_nodes[i + 1:50]:
                # Not directly connected
                if node2 not in self.adjacency.get(node1, set()):
                    # But share papers
                    papers1 = self.concept_papers.get(node1, set())
                    papers2 = self.concept_papers.get(node2, set())
                    shared = papers1 & papers2

                    # Connected through intermediary (2-hop)
                    two_hop_connections = self.adjacency.get(node1, set()) & self.adjacency.get(node2, set())

                    if len(two_hop_connections) > 0 or len(shared) > 0:
                        score = (len(two_hop_connections) * 0.4 + len(shared) * 0.6) / max(
                            len(papers1 | papers2), 1
                        )
                        gaps.append({
                            "concept_a": self.nodes.get(node1, {}).get("label", node1),
                            "concept_b": self.nodes.get(node2, {}).get("label", node2),
                            "gap_type": "missing_direct_connection",
                            "confidence": min(score, 1.0),
                            "shared_papers": len(shared),
                            "intermediaries": [
                                self.nodes.get(n, {}).get("label", n)
                                for n in list(two_hop_connections)[:3]
                            ],
                        })

        # Sort by confidence
        gaps.sort(key=lambda x: x["confidence"], reverse=True)
        return gaps[:20]  # Top 20 gaps

    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        node_types = defaultdict(int)
        for node in self.nodes.values():
            node_types[node.get("type", "unknown")] += 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "papers_indexed": len(self.paper_concepts),
            "avg_degree": (
                sum(len(neighbors) for neighbors in self.adjacency.values())
                / max(len(self.nodes), 1)
            ),
        }

    def to_json(self) -> str:
        """Export graph as JSON for visualization."""
        return json.dumps({
            "nodes": list(self.nodes.values()),
            "edges": list(self.edges.values()),
            "stats": self.get_statistics(),
        }, indent=2)
