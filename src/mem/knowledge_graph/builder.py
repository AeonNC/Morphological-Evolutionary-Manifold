import networkx as nx
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from mem.knowledge_graph.schema import Node, Edge, NodeType, EdgeType

class PriorKnowledgeGraph:
    """
    Builds and manages the cohort-level Morphology-Biology Prior KG.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: Node):
        self.graph.add_node(node.node_id, **node.dict())

    def add_edge(self, edge: Edge):
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge_type=edge.edge_type,
            evidence=edge.evidence_source,
            confidence=edge.confidence,
            is_patient_linked=edge.is_patient_linked
        )

    def build_from_csv(self, nodes_csv: Path, edges_csv: Path):
        """
        Builds the graph from curated CSV files.
        """
        nodes_df = pd.read_csv(nodes_csv)
        for _, row in nodes_df.iterrows():
            node = Node(
                node_id=row['node_id'],
                node_type=NodeType(row['node_type']),
                label=row['label'],
                properties=row.to_dict()
            )
            self.add_node(node)

        edges_df = pd.read_csv(edges_csv)
        for _, row in edges_df.iterrows():
            edge = Edge(
                source_id=row['source_id'],
                target_id=row['target_id'],
                edge_type=EdgeType(row['edge_type']),
                evidence_source=row['evidence_source'],
                evidence_url=row.get('evidence_url', None),
                confidence=float(row['confidence']),
                is_patient_linked=bool(row['is_patient_linked']),
                citation=row.get('citation', None)
            )
            self.add_edge(edge)

    def export_graphml(self, path: Path):
        nx.write_graphml(self.graph, path)

    def get_hypotheses(self, cluster_id: str) -> List[Dict[str, Any]]:
        """
        Finds biological entities linked to a specific model cluster.
        """
        # Find edges where source is a MODEL_CLUSTER
        links = []
        for u, v, d in self.graph.edges(data=True):
            if u == cluster_id:
                links.append({"target": v, "type": d['edge_type'], "evidence": d['evidence']})
        return links
