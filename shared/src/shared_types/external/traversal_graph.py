from pydantic import BaseModel, Field, RootModel, model_validator
from .extractor import ExtractorConfig


class NodeConfig(BaseModel):
    """
    List of edges for adjacency list representation of TraversalGraph
    """

    extractors: list[ExtractorConfig]
    callbacks: list[str] = Field(default_factory=list)


class TraversalGraphConfig(RootModel[dict[str, list[NodeConfig]]]):
    """
    Adjacency list for states

    Maps state: configurations
    """

    @model_validator(mode="after")
    def validate_callbacks(self) -> "TraversalGraphConfig":
        defined_states = set(self.root.keys())

        for state, nodes in self.root.items():
            for node in nodes:
                for cb in node.callbacks:
                    if cb not in defined_states:
                        raise ValueError(
                            f"In state '{state}', callback '{cb}' is not valid state."
                            f"Valid states: {sorted(defined_states)}"
                        )
        return self
