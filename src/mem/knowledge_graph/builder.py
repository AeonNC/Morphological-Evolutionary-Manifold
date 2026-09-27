import networkx as nx
import json
from pathlib import Path
from typing import List, Dict, Any
from .schema import KGNode, KGEdge, NodeRole, EdgeType
from ..utils.paths import paths

class BioPriorBridge:
    """
    Constructs the Morphology-Biology Prior Knowledge Graph.
    Links model-derived clusters to public genomic priors.
    """
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: KGNode):
        self.graph.add_node(node.id, role=node.role, label=node.label, **node.properties)

    def add_edge(self, edge: KGEdge):
        self.graph.add_edge(
            edge.source,
            edge.target,
            relation=edge.relation,
            evidence=edge.evidence_level,
            url=edge.source_url,
            is_patient_linked=edge.is_patient_linked,
            confidence=edge.confidence
        )

    def build_from_curated_json(self, json_path: Path):
        """Loads a curated knowledge set into the graph."""
        with open(json_path, 'r') as f:
            data = json.load(f)

        for node_data in data.get('nodes', []):
            self.add_node(KGNode(**node_data))

        for edge_data in data.get('edges', []):
            self.add_edge(KGEdge(**edge_data))

    def export_graphml(self, output_path: Path):
        """Export for Gephi/Cytoscape visualization."""
        nx.write_graphml(self.graph, str(output_path))

    def get_cluster_hypotheses(self, cluster_id: str) -> List[Dict[str, Any]]:
        """
        Traverses the graph to find biological priors associated with a morphology cluster.
        Cluster -> MorphologyAttr -> GeneticEntity -> Pathway
        """
        hypotheses = []
        # Simplified traversal: find paths from cluster to pathway
        for node in self.graph.nodes:
            if self.graph.has_edge(cluster_id, node):
                # Check if node is an attribute
                if self.graph.nodes[node].get('role') == 'morphology_attribute':
                    # Find what this attribute is associated with
                    for target in self.graph.successors(node):
                        hypotheses.append({
                            "cluster": cluster_id,
                            "via": node,
                            "hypothesis": target,
                            "details": self.graph.get_edge_data(node, target)
                        })
        return hypotheses
