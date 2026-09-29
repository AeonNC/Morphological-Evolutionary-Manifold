from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class NodeType(str, Enum):
    DISEASE = "disease"
    SUBTYPE = "subtype"
    GENETIC_ENTITY = "genetic_entity"
    GENE = "gene"
    MUTATION = "mutation"
    FUSION = "fusion"
    PATHWAY = "pathway"
    MORPHOLOGY_ATTRIBUTE = "morphology_attribute"
    MODEL_CLUSTER = "model_cluster"
    TOPOLOGY_SIGNATURE = "topology_signature"
    DATASET = "dataset"
    EVIDENCE_SOURCE = "evidence_source"

class EdgeType(str, Enum):
    HAS_SUBTYPE = "has_subtype"
    ASSOCIATED_WITH = "associated_with"
    INCLUDES = "includes"
    PARTICIPATES_IN = "participates_in"
    OBSERVED_IN = "observed_in"
    HYPOTHESIS_LINK = "hypothesis_link"
    SUPPORTS = "supports"

class Node(BaseModel):
    node_id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = {}

class Edge(BaseModel):
    source_id: str
    target_id: str
    edge_type: EdgeType
    evidence_source: str
    evidence_url: Optional[str] = None
    confidence: float = 1.0
    is_patient_linked: bool = False
    citation: Optional[str] = None
    notes: Optional[str] = None
