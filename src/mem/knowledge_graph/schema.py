from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class NodeRole(str, Enum):
    DISEASE = "disease"
    SUBTYPE = "subtype"
    GENETIC_ENTITY = "genetic_entity"
    GENE = "gene"
    MUTATION = "mutation"
    FUSION = "fusion"
    PATHWAY = "pathway"
    MORPHOLOGY_ATTR = "morphology_attribute"
    MODEL_CLUSTER = "model_cluster"
    TOPOLOGY_SIG = "topology_signature"
    DATASET = "dataset"
    EVIDENCE_SOURCE = "evidence_source"

class EdgeType(str, Enum):
    HAS_SUBTYPE = "has_subtype"
    ASSOCIATED_WITH = "associated_with"
    INCLUDES = "includes"
    PARTICIPATES_IN = "participates_in"
    OBSERVED_IN = "observed_in"
    HAS_TOPOLOGY = "has_topology"
    HYPOTHESIS_LINKED = "hypothesis_linked_to"
    CONTAINS = "contains"
    SUPPORTED_BY = "supported_by"

class KGNode(BaseModel):
    id: str
    role: NodeRole
    label: str
    properties: Dict[str, Any] = {}

class KGEdge(BaseModel):
    source: str
    target: str
    relation: EdgeType
    evidence_level: str = "low"
    source_url: Optional[str] = None
    citation: Optional[str] = None
    is_patient_linked: bool = False
    confidence: float = 0.5
