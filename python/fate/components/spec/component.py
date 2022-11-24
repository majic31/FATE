from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

roles = Literal["guest", "host", "arbiter"]
stages = Literal["train", "predict", "default"]
labels = Literal["trainable"]


class ParameterSpec(BaseModel):
    type: str
    default: Any
    optional: bool


class ArtifactSpec(BaseModel):
    type: str
    optional: bool
    stages: Optional[List[stages]]
    roles: List[roles]


class InputDefinitionsSpec(BaseModel):
    parameters: Dict[str, ParameterSpec]
    artifacts: Dict[str, ArtifactSpec]


class OutputDefinitionsSpec(BaseModel):
    artifacts: Dict[str, ArtifactSpec]


class ComponentSpec(BaseModel):
    name: str
    description: str
    provider: str
    version: str
    labels: List[labels]
    roles: List[roles]
    input_definitions: InputDefinitionsSpec
    output_definitions: OutputDefinitionsSpec


class ComponentSpecV1(BaseModel):
    component: ComponentSpec
    schema_version: str = "v1"
