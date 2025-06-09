import json
from importlib import resources
from moduscrape.config.schema.external.config import ConfigSpec
from shared_types.external.input import InputConfig


def load_config(spec: ConfigSpec) -> InputConfig:
    if spec.type == "package":
        # spec.resource == "rules/sites/vulcanhobby.json"
        pkg, _, filename = spec.resource.partition("/")
        # toy_catalogue.config.rules sites/is the package path
        with resources.open_text(f"moduscrape.config.rules.{pkg}", filename) as fp:
            data = json.load(fp)

    elif spec.type == "file":
        with open(spec.path, "r", encoding="utf-8") as fp:
            data = json.load(fp)

    elif spec.type == "url":
        import requests

        r = requests.get(str(spec.url))
        r.raise_for_status()
        data = r.json()

    else:
        raise ValueError(f"Unknown config spec: {spec!r}")
    return InputConfig.model_validate(data)
