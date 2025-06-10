import pytest
import os
from pathlib import Path
import json
from shared_types.external.input import InputConfig
from shared_types.external.processors import ProcessorConfig
from shared_types.external.extractor import ExtractorConfig
from shared_types.external.traversal_graph import TraversalGraphConfig

test_dir = Path(os.path.dirname(__file__))


@pytest.fixture
def sample_input_config() -> InputConfig:
    with (test_dir / "examples" / "example_input.json").open(
        "r", encoding="utf-8"
    ) as f:
        return InputConfig.model_validate(json.load(f))


@pytest.fixture
def sample_processors_config(sample_input_config: InputConfig) -> ProcessorConfig:
    return sample_input_config.processors


@pytest.fixture
def sample_graph_config(sample_input_config: InputConfig) -> TraversalGraphConfig:
    return sample_input_config.traversal


@pytest.fixture
def sample_extractor_configs(
    sample_graph_config: TraversalGraphConfig,
) -> list[ExtractorConfig]:
    configs: list[ExtractorConfig] = []
    for grouping in sample_graph_config.root.values():
        for node_config in grouping:
            configs.extend(config for config in node_config.extractors)
    return configs
