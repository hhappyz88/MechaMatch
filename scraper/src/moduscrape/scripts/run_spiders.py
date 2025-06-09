from scrapy.crawler import CrawlerProcess
import typer
from pathlib import Path
from moduscrape.config.config_manager import load_config
from moduscrape.config.schema.external.config import (
    FileConfig,
    PackageConfig,
    UrlConfig,
    ConfigSpec,
)
from moduscrape.session.session_manager import create_session
from moduscrape.spiders.core_spider import CoreSpider
from moduscrape.config.settings import build_settings, load_config_from_package

app = typer.Typer()


@app.command()
def main(
    site: str,
    config_file: Path = typer.Option(None, "--file", help="Path to local JSON config"),
    config_url: str = typer.Option(None, "--url", help="URL to load config from"),
):
    spec: ConfigSpec
    if config_file:
        spec = FileConfig(type="file", path=str(config_file))
    elif config_url:
        spec = UrlConfig.model_validate({"type": "url", "url": config_url})
    else:
        spec = PackageConfig(type="package", resource=f"sites/{site}.json")
    core = load_config_from_package("core_settings.toml")
    custom = load_config_from_package("custom_settings.toml")
    settings = build_settings(core, custom)
    print("Settings created", settings)
    config = load_config(spec)

    print("config created", config)
    session = create_session(config=config, mode="fresh")
    print("Session created", session)

    process = CrawlerProcess(settings)
    process.crawl(CoreSpider, context=session)

    process.start()
    print("Crawler finished")  # Blocks until all spiders finish
