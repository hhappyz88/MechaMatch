import json
from importlib import resources
from toy_catalogue.config.schema.external.config import ConfigSpec
from toy_catalogue.config.schema.external.schema import SiteConfig


class ConfigManager:
    @staticmethod
    def load_config(spec: ConfigSpec) -> SiteConfig:
        if spec.type == "package":
            # spec.resource == "rules/sites/vulcanhobby.json"
            pkg, _, filename = spec.resource.partition("/")
            # toy_catalogue.config.rules sites/is the package path
            with resources.open_text(
                f"toy_catalogue.config.rules.{pkg}", filename
            ) as fp:
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

        return SiteConfig.model_validate(data)
